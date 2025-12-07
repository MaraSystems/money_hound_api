from src.agents.researcher.model import AnalystState, AnalystReview
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.llms import llm

analyst_reviewer_prompt = """
You are reviewing the generated Analyst personas: {personas}.  

Your review must reflect the **depth**: {depth} of the provided personas — if the personas are shallow, generic, or lack analytical depth, the feedback must reflect that clearly.  

Be extremely strict. Approve only if every persona is flawless:
- Clear, realistic, and professional  
- Directly relevant to the topic: {topic}  
- Demonstrates depth of reasoning and domain understanding  
- Roles fully cover the scope of the topic with no conceptual or practical gaps  
- Each goal is concise, impactful, and actionable (1–2 sentences)  
- No redundancy, vagueness, or weakness  

If any persona fails these standards, approval must be `"No"`.  
If coverage or depth is incomplete, include the missing or suggested roles directly in the review.  

Return ONLY a Python dictionary in this format:
  - approved: "Yes" or "No",
  - review: "Detailed, critical assessment including flaws, missing roles, or improvements",
"""

def review_analysts(state: AnalystState):
    topic = state['topic']
    analysts = state['analysts']
    depth = state['depth']
    
    personas = [str(analyst) for analyst in analysts]

    system_message = analyst_reviewer_prompt.format(personas=personas, topic=topic, depth=depth)
    structured_llm = llm.with_structured_output(AnalystReview)

    response = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Review the analyst personas for {topic}")])
    return response

REVIEW_ANALYSTS = 'review_analysts'