from typing import List

from src.llm.DTO import Message


class PromptUtils:
    @staticmethod
    def create_new_messages_with_agent_plot(prompt: str) -> List[Message]:
        """
        create a new list of messages which can be used for calling the llm.
        :param prompt: the prompt to add to the list of messages
        :return:
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. /no_think"},
            {
                "role": "user",
                "content": prompt},
        ]
        messages = [Message(role=x['role'], content=x['content']) for x in messages]
        return messages
