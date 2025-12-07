from typing import List
from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph.state import CompiledStateGraph


class FakeAgent(CompiledStateGraph):
    def __init__(self, name='FakeAgent'):
        self.name = name
        self.history = []

    def invoke(self, query, **kwargs):
        messages: List[AnyMessage] = query['messages']
        last_message = messages[-1].content
        bot_message = AIMessage(last_message)
        messages.append(bot_message)
        return {'messages': messages}
    
    async def ainvoke(self, query, **kwargs):
        return self.invoke(query, **kwargs)
