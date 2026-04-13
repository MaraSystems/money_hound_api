from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing_extensions import Optional
from langchain_core.tools import StructuredTool

from src.config.llms import get_llm
from src.lib.utils.tool_set import AgentTool
from src.models.workflow import WorkflowSettings, BaseWorkflow

class Evaluation(BaseModel):
    """Evaluation result for query-answer validation.

    Attributes:
        score: Rating score (0-1) of how well the answer resolves the query
        feedback: Constructive feedback on optimizing the answer
    """
    score: float = Field(..., ge=0, le=1, description='Rating of how well the answer resolves the query')
    feedback: str = Field(..., description='Feedback on how to optimize the answer')


class EvaluationState(BaseModel):
    """State model for evaluation workflow.

    Attributes:
        query: User's query message
        answer: AI's answer message
        evaluation: Evaluation result (score and feedback)
    """
    query: HumanMessage = Field(..., description='The user\'s query')
    answer: AIMessage = Field(..., description='The answer to the user\'s query')
    evaluation: Optional[Evaluation] = Field(None, description='The evaluation of the answer')


class EvaluationWorkflow(BaseWorkflow):
    """Workflow for evaluating query-answer pairs.

    Validates answers against original queries and provides
    optimization feedback with confidence scoring.
    """

    def __init__(self, settings=WorkflowSettings()):
        """Initialize the evaluation workflow.

        Args:
            settings: Workflow configuration settings
        """
        super().__init__(EvaluationState, settings=settings)
        self._build_graph()


    def _build_graph(self):
        """Build the workflow graph with evaluation node."""
        self.add_node(self.EVALUATE, self.evaluate)
        self.set_entry_point(self.EVALUATE)
        self.set_finish_point(self.EVALUATE)
        self.graph = self.compile()

        
    EVALUATE = 'evaluate'
    def evaluate(self, state: EvaluationState) -> dict:
        """Evaluate an answer against the original query.

        Args:
            state: Current workflow state with query and answer

        Returns:
            Dictionary with evaluation score and feedback
        """
        prompt = """
            Role
            You are the Query - Answer Validator.

            Task
            Your goal is to evaluate the answer against the original query and provide optimization feedback.

            Rules:
            - If the answer fully addresses the query, set status to True
            - If the answer does not fully address the query, set status to False
            - Provide constructive feedback on what is missing or incorrect in the answer

            Input Data:
            - Query: {query}
            - Answer: {answer}

            Output (Return a valid JSON): 
            - score: float (The rating between (0 - 1) of the how the answer resolves the query)
            - feedback: str (Constructive optimization feedback on the answer)
        """

        formatted_prompt = prompt.format(query=state.query, answer=state.answer)
        system_message = SystemMessage(content=formatted_prompt)
        llm = get_llm()
        structured_llm = llm.with_structured_output(Evaluation, strict=True)
        evaluation = structured_llm.invoke([system_message]+[HumanMessage(content='Evaluate the answer')])
        return {'evaluation': evaluation}


    def invoke(self, state: EvaluationState) -> Evaluation:
        """Execute the workflow and return evaluation.

        Args:
            state: Initial evaluation state

        Returns:
            Evaluation result with score and feedback
        """
        response = self.graph.invoke(state)
        return response['evaluation']
    

    def as_tool(self, name: str) -> AgentTool:
        """Convert workflow into a LangChain tool.

        Args:
            name: Tool name

        Returns:
            AgentTool wrapping the workflow
        """
        tool = StructuredTool.from_function(
            name=name,
            description=(
                "Validate your response before returning it — check for accuracy, completeness, and tone. Use this tool IF AND ONLY IF the confidence in the answer is lower than 0.5."
            ),
            func=lambda query, answer: self.invoke(
                EvaluationState(query=HumanMessage(query), answer=AIMessage(answer))
            )
        )

        return AgentTool(action='Evaluating', tool=tool)