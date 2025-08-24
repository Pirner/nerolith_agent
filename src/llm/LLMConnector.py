from typing import List
import requests

from src.llm.DTO import Message


class LLMConnector:
    """
    communicate with llm hosted over the api system.
    """
    def __init__(self, server_ip='localhost', port=8000):
        """
        main constructor for the API connector to communicate with cora API
        :param server_ip: the ip address of the server
        :param port: the port under which the server runs
        """
        self.server_ip = server_ip
        self.port = port

    def _get_base_url(self):
        """
        get the base url to derive from
        :return:
        """
        url = 'http://{}:{}'.format(self.server_ip, self.port)
        return url

    def call_messages(self, messages: List[Message], tools=None):
        # TODO handle model_id
        # handle optional tools
        # handle messages
        url = '{}/message_generate'.format(self._get_base_url())
        json_messages = [x.dict() for x in messages]
        if tools is None:
            payload = {
                "model_id": "qwen3_0_6B",
                "messages": json_messages,
            }
        else:
            payload = {
                "model_id": "qwen3_0_6B",
                "messages": json_messages,
                "tools": tools
            }

        x = requests.post(url, json=payload)
        return x
