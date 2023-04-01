from langchain.agents import Tool
from langchain.memory import ConversationTokenBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.utilities import GoogleSerperAPIWrapper, BashProcess
from langchain.agents.tools import Tool
from langchain.agents import initialize_agent
from langchain.schema import BaseMessage, HumanMessage, AIMessage

import json
from tools import music_tool, HomeAssistantTool
import db

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2, verbose=True)
memory = ConversationTokenBufferMemory(
    memory_key="chat_history", return_messages=True, max_token_limit=1000, llm=llm
)

search = GoogleSerperAPIWrapper()
bash = BashProcess()
ha_tool = HomeAssistantTool(llm)


def asyncify(fn):
    async def afn(query):
        return fn(query)

    return afn


tools = [
    Tool(
        name="Home Assistant Control",
        func=ha_tool.arun,
        coroutine=ha_tool.arun,
        description="The user has a Home Assistant setup. This starts the process for changing things like lights, cameras etc. Use this tool whenever the user needs that sort of thing. Has modes and alerts. The input should be a standalone query containing all context necessary. The command should follow this format: `ENTITY(entity_keyword) Full user command with context`, example: `ENTITY(light) Turn off all lights`",
    ),
    Tool(
        name="Play Music",
        func=music_tool,
        coroutine=music_tool,
        description="Useful for playing music. The input to this command should be a string containing a JSON object with at least one of the following keys: 'artist', 'album', 'song', 'playlist'.",
    ),
    Tool(
        name="Run a command in terminal",
        func=bash.run,
        coroutine=asyncify(bash.run),
        description="Run a bash command on the host computer. Might have side effects.",
    ),
    Tool(
        name="Ask a politician and trusted news source",
        func=search.run,
        coroutine=asyncify(search.run),
        description="Use when you need to answer specific questions about current events or the current state of the world. The input to this should be a standalone query and search term. Don't copy the response ad-verbatim, but use it as a starting point for your own response.",
    ),
]
agent_chain = initialize_agent(
    tools,
    llm,
    agent="chat-conversational-react-description",
    verbose=True,
    memory=memory,
)


async def ask_sherlock(human_input: str, user_id: str) -> str:
    context = db.get_last_context(user_id)
    if context is not None:
        context = json.loads(context)
        context = [
            AIMessage(content=msg["m"])
            if msg["s"] == "AI"
            else HumanMessage(content=msg["m"])
            for msg in context
        ]
    else:
        context = []

    memory.chat_memory.messages = context

    db.save_message_to_database(user_id, human_input, user_id)

    ai_output = await agent_chain.arun(input=human_input)
    db.save_message_to_database(user_id, ai_output, "AI")

    msgs: list[BaseMessage] = memory.load_memory_variables({})["chat_history"]
    new_context_as_str = json.dumps(
        [
            {"m": msg.content, "s": user_id if msg.type == "human" else "AI"}
            for msg in msgs
        ]
    )
    db.update_user_last_output(user_id, new_context_as_str)


async def loop():
    while True:
        user_id = "id"
        human_input = input("You: ")
        ai_output = await ask_sherlock(human_input, user_id)
        print(ai_output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(loop())
