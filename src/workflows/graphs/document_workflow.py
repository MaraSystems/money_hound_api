import json
from typing_extensions import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool

from src.config.llms import get_llm
from src.lib.store.storage import Storage
from src.lib.utils.tool_set import AgentTool
from src.models.workflow import BaseWorkflow, WorkflowSettings


class ImageContentPosition(BaseModel):
    """Represents the position of extracted content in an image.

    Attributes:
        x: X-coordinate of the content's position
        y: Y-coordinate of the content's position
    """
    x: float = Field(..., description="The x cordinate of the content's position")
    y: float = Field(..., description="The y cordinate of the content's position")


class ImageContent(BaseModel):
    """Represents extracted text content from an image.

    Attributes:
        text: Extracted text content
        position: Position of the content in the image
    """
    text: str = Field(..., description="The text of the content")
    position: ImageContentPosition = Field(..., description="The position of the content")


class ImageDetails(BaseModel):
    """Complete extracted details from an image.

    Attributes:
        content: List of extracted content items
        confidence: Confidence score of the extraction (0-1)
    """
    content: list[ImageContent] = Field(..., description='The contents of the image')
    confidence: float = Field(..., description='The confidence of the extraction')


class DocumentCategory(BaseModel):
    """Document classification result.

    Attributes:
        category: Document category (Receipt or Unknown)
        confidence: Confidence score of the classification (0-1)
    """
    category: Optional[Literal['Receipt', 'Unknown']] = Field(None, description='The category of the image')
    confidence: float = Field(..., description='The confidence of the extraction')


class DocumentState(BaseModel):
    """State model for document processing workflow.

    Attributes:
        file_path: Path to the document file
        content_type: MIME type of the document
        category: Document category after classification
        content: Extracted text content from the document
    """
    file_path: str = Field(..., description='The path to the document')
    content_type: str = Field(..., description='The content type of the document')
    category: Optional[Literal['Receipt', 'Unknown']] = Field(None, description='The category of the image')
    content: Optional[str] = Field(None, description='The content of the document')


class DocumentWorkflow(BaseWorkflow):
    """Workflow for processing and categorizing documents.

    Handles reading, image extraction, and categorization of documents
    using LangGraph state machine with LLM-based analysis.
    """
    storage = Storage()
    EXTRACT_RECEIPT = 'extract_receipt'

    def __init__(self, settings=WorkflowSettings):
        """Initialize the document workflow.

        Args:
            settings: Workflow configuration settings
        """
        super().__init__(DocumentState, settings)
        self._build_graph()

    def _build_graph(self):
        """Build the workflow graph with nodes and edges."""
        self.add_node(self.READ_FILE, self.read_file)
        self.add_node(self.EXTRACT_IMAGE, self.extract_image)
        self.add_node(self.CATEGORIZE, self.categorize)

        self.set_entry_point(self.READ_FILE)
        self.add_conditional_edges(self.READ_FILE, self.should_extract_image, [self.EXTRACT_IMAGE, self.CATEGORIZE])
        self.add_edge(self.EXTRACT_IMAGE, self.CATEGORIZE)
        self.set_finish_point(self.CATEGORIZE)

        self.graph = self.compile()

    READ_FILE = 'read_file'
    def read_file(self, state: DocumentState) -> dict:
        """Read and extract text content from a document file.

        Args:
            state: Current workflow state with file path

        Returns:
            Dictionary with extracted content
        """
        self.logger.info('Reading File')
        with open(state.file_path, 'rb') as file:
            content = file.read()
        content = self.storage.binary_to_text(content, file.name, state.content_type)
        return {'content': content}

    def should_extract_image(self, state: DocumentState) -> str:
        """Determine if image extraction is needed based on content type.

        Args:
            state: Current workflow state

        Returns:
            Next node name (EXTRACT_IMAGE or CATEGORIZE)
        """
        return self.EXTRACT_IMAGE if state.content_type.startswith('image/') else self.CATEGORIZE

    EXTRACT_IMAGE = 'extract_image'
    def extract_image(self, state: DocumentState) -> dict:
        """Extract structured content from an image using LLM.

        Args:
            state: Current workflow state with image content

        Returns:
            Dictionary with extracted content as JSON
        """
        self.logger.info('Extracting image')
        prompt = """
            Role
            You are an image content extraction specialist. Your purpose is to analyze an input image and convert information into structured, machine-readable output without assumptions.

            Task
            Inspect the provided image and extract the textual and contextual content both writen and printed. Determine whether the category of the image, and return a strictly structured JSON response.

            Rules (Follow without exception)
            - Extract all information that is in the image.
            - Do NOT infer, assume, interpret intent, or fill gaps.
            - Preserve original wording where possible.
            - Do NOT hallucinate brands, values, or metadata.
            - Categorize the content of the image as one of [Receipt, Unknown].
            - Provide the confidence in your extracted data.

            Output:
            - content: (The content of the image) [
                - text: str
                - position: (Position of the content)
                    - x: float (The x cordinate of the content on the image)
                    - y: float (The y cordinate of the content on the image)
            ]
            - confidence: float (between 0-1)
        """
        llm = get_llm('qwen3-vl:235b-cloud')
        structured_llm = llm.with_structured_output(ImageDetails)

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=[
                {'type': 'text', 'text': 'Extract the details of the receipt'},
                {'type': 'image_url', 'image_url': state.content}
            ])
        ]

        response = structured_llm.invoke(messages)
        return {'content': json.dumps(response.model_dump()['content'])}

    CATEGORIZE = 'categorize'
    def categorize(self, state: DocumentState) -> dict:
        """Categorize a document based on extracted content.

        Args:
            state: Current workflow state with document content

        Returns:
            Dictionary with document category
        """
        self.logger.info('Categorizing document')
        prompt = """
            Role
            You are a content classification specialist. You analyze structured document content and produce an objective category based only on the provided data.

            Task
            Inspect the provided content and determine what it represesnts. Return a strictly structured JSON response.

            Rules (Follow without exception)
            - Use only the provided content as evidence.
            - Do NOT infer missing values, intent, or context beyond what is explicitly present.
            - Do NOT hallucinate entities, brands, totals, or metadata.
            - Classify the content as one of:
                * Receipt: If the content is a valid receipt
                * Unknown
            - Confidence must reflect certainty of classification based on provided content.

            Input
            - {content} (The content)

            Output
            - confidence: float (between 0-1)
            - category: Literal[Receipt, Unknown] (The category of the content)
        """

        formatted_prompt = prompt.format(content=state.content)
        system_message = SystemMessage(content=formatted_prompt)

        llm = get_llm()
        structured_llm = llm.with_structured_output(DocumentCategory)

        response = structured_llm.invoke([system_message]+[HumanMessage(content='Categorize the content')])
        return {'category': response.category}

    def select_function(self, state: DocumentState) -> str:
        """Select the next function based on document category.

        Args:
            state: Current workflow state

        Returns:
            Next function name
        """
        return self.EXTRACT_RECEIPT if state.category == 'Receipt' else self.DESCRIBE

    def invoke(self, state: DocumentState) -> dict:
        """Execute the workflow with given state.

        Args:
            state: Initial document state

        Returns:
            Workflow response with processed results
        """
        response = self.graph.invoke(state)
        return response

    def as_tool(self, name: str) -> AgentTool:
        """Convert the workflow into a LangChain tool.

        Args:
            name: Name for the tool

        Returns:
            AgentTool wrapping the workflow
        """
        tool = StructuredTool.from_function(
            name=name,
            description=(
                'Extracts the contents of a image and pdf documents ussing the file_path'
            ),
            func=lambda file_path, content_type: self.invoke(
                DocumentState(file_path=file_path, content_type=content_type)
            )
        )

        return AgentTool(action='Extracting Document', tool=tool)
