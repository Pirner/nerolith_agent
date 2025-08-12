import requests

from src.agent import NerolithAgent
from src.MailAccess.utils import MailUtils
from src.llm.DTO import Message
from src.llm.LLMConnector import LLMConnector


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_temperature",
            "description": "Get current temperature at a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "celsius".',
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_temperature_date",
            "description": "Get temperature at a location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "date": {
                        "type": "string",
                        "description": 'The date to get the temperature for, in the format "Year-Month-Day".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "celsius".',
                    },
                },
                "required": ["location", "date"],
            },
        },
    },
]


def main():
    messages = [
        {"role": "system", "content": "You are a helpful assistant.\n\nCurrent Date: 2024-08-31 /no_think"},
        {"role": "user", "content": "Whats the weather in Nuremberg tomorrow?"},
    ]
    messages = [Message(role=x['role'], content=x['content']) for x in messages]
    server_ip = 'localhost'
    port = 8000
    agent = NerolithAgent()
    agent.configure_connector(server_ip, port)

    emails = agent.retrieve_emails()
    # emails = [MailUtils.convert_email(x) for x in emails]
    for em in emails:
        converted_email = MailUtils.convert_email(em)
        agent.process_email(email=converted_email)
    # api_connector = LLMConnector(server_ip=server_ip, port=port)
    # response = api_connector.call_messages(messages=messages)
    # print(response.text)


if __name__ == '__main__':
    main()
