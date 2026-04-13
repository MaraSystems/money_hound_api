from pydantic import BaseModel, Field
from typing_extensions import Optional

from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from src.config.llms import get_llm
from src.models.workflow import BaseWorkflow, WorkflowSettings


class Summary(BaseModel):
    """Conversation summary model.

    Attributes:
        key_points: List of main discussion points (max 5)
        profile: User profile summary
    """
    key_points: list[str] = Field(default_factory=list, description="Key points from the summary", max_length=5)
    profile: Optional[str] = Field(None, description="The profile of the user")


class SummaryState(BaseModel):
    """State model for conversation summarization.

    Attributes:
        messages: Conversation history messages
        summary: Current summary state
    """
    messages: list[AnyMessage] = Field(..., description='The conversation history')
    summary: Optional[Summary] = Field(None, description='The summary of the conversation')


class SummaryWorkflow(BaseWorkflow):
    """Workflow for summarizing conversation history.

    Generates structured summaries with key points and user profile.
    """

    def __init__(self, settings=WorkflowSettings()):
        """Initialize the summary workflow.

        Args:
            settings: Workflow configuration settings
        """
        super().__init__(state_schema=SummaryState, settings=settings)
        self._build_graph()

    def _build_graph(self):
        """Build the workflow graph with summarize node."""
        self.add_node(self.SUMMARIZE, self.summarize)

        self.set_entry_point(self.SUMMARIZE)
        self.set_finish_point(self.SUMMARIZE)

        self.graph = self.compile()

    SUMMARIZE = "summarize"
    def summarize(self, state: SummaryState) -> dict:
        """Generate a summary of the conversation.

        Args:
            state: Current workflow state with messages

        Returns:
            Dictionary with generated summary
        """
        prompt = """
            You are a Conversation Analyst.
            Generate a detailed summary of the following conversation.

            Input Data:
            - Messages: {messages} - The conversation messages to be summarized
            - Running Summary: {summary} - The current summary of the previous conversations

            Guidelines:
            - Keep language clear, professional, and actionable
            - Focus on key points, decisions, and action items
            - Avoid unnecessary details or filler content
            - Ensure the profile is concise yet comprehensive

            Output: Provide a well-structured summary of the conversation.
            - key_points: List the main points discussed
            - profile: The profile of the user
        """

        formatted_prompt = prompt.format(messages=state.messages, summary=state.summary, profile=state.profile)
        message = [SystemMessage(content=formatted_prompt), HumanMessage(content="Generate the summary now.")]

        llm = get_llm()
        structured_llm = llm.with_structured_output(Summary)
        response = structured_llm.invoke(message)

        return {"summary": response}

    def invoke(self, state: SummaryState) -> Summary:
        """Execute the workflow and return summary.

        Args:
            state: Initial summary state

        Returns:
            Generated conversation summary
        """
        response = self.graph.invoke(state, config=self.settings.config)
        return response['summary']
