

async def stream_chat(events):
    async for event in events:
        if event['event'] == 'on_chain_start':
            name = event['name']

            if name == 'enhance_model':
                yield {'type': 'chain_start', 'action': 'Enhancing Query'}

            if name == 'workflow_model':
                yield {'type': 'chain_start', 'action': 'Generating Workflow'}

            if name == 'execute_model':
                yield {'type': 'chain_start', 'action': 'Executing Workflow'}

            if name == 'retrieve_model':
                yield {'type': 'chain_start', 'action': 'Retrieving Knowledge'}

            if name == 'rank_model':
                yield {'type': 'chain_start', 'action': 'Retrieving Knowledge'}

            if name == 'web_model':
                yield {'type': 'chain_start', 'action': 'Searching Web'}

        elif event['event'] == "on_chat_model_stream":
            if event['metadata']['langgraph_node'] in ['execute_model', 'support_node']:
                chunk = event['data']['chunk']
                content = getattr(chunk, 'content', None)
                if content:
                    yield {'type': 'stream', 'content': content}

    content =event['data']['output']['messages'][-1].content
    yield {'type': 'end', 'content': content}
