import re

from src.llm.DTO import Message
from src.llm.Tools.DTO import ToolCall


class ToolUtils:
    @staticmethod
    def has_tools(msg: Message) -> bool:
        """
        check whether a message has tools
        :return:
        """
        # get the tools
        matches = re.findall(r"<tool_call>(.*?)</tool_call>", msg.content, re.DOTALL)
        if len(matches) > 0:
            return True
        return False
