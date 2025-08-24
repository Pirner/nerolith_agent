import random

from src.agent import NerolithAgent
from src.llm.DTO import Message
from src.llm.Tools.ArxivTools import ArxivTools
from src.llm.Tools.ToolParser import LLMToolParser
from src.MailAccess.utils import MailUtils


def main():
    server_ip = '192.168.178.25'
    port = 8000
    agent = NerolithAgent()
    agent.configure_connector(server_ip, port)

    # tools = [get_weather, add]
    # tools_schema = [LLMToolParser.function_to_json(x) for x in tools]
    tools_schema = ArxivTools.get_tools()

    messages = [
        {
            "role": "system",
            "content":
                f"""
                You are a helpful assistant, only call for tools if necessary. /no_think
                """
        },
        {
            "role": "user",
            "content": f"""
            Describe a turtle!
            """},
    ]
    # What is the weather in New York?
    messages = [Message(role=x['role'], content=x['content']) for x in messages]
    response = agent.process_messages(
        messages=messages,
        tools=tools_schema,
    )
    print(response)


if __name__ == '__main__':
    main()
