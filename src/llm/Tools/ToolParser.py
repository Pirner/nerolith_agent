import inspect
import json
from typing import List
import re

from src.llm.DTO import Message
from src.llm.Tools.DTO import ToolCall


class LLMToolParser:
    @staticmethod
    def function_to_json(func) -> dict:
        """
        Converts a Python function into a JSON-serializable dictionary
        that describes the function's signature, including its name,
        description, and parameters.

        Args:
            func: The function to be converted.
        Returns:
            A dictionary representing the function's signature in JSON format.
        """
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null",
        }
        try:
            signature = inspect.signature(func)
        except ValueError as e:
            raise ValueError(
                f"Failed to get signature for function {func.__name__}: {str(e)}"
            )
        parameters = {}
        for param in signature.parameters.values():
            try:
                param_type = type_map.get(param.annotation, "string")
            except KeyError as e:
                raise KeyError(
                    f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
                )
            parameters[param.name] = {"type": param_type}
        required = [
            param.name
            for param in signature.parameters.values()
            if param.default == inspect._empty
        ]
        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or "",
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required,
                },
            },
        }

    @staticmethod
    def parse_message_to_tools(t_msg: Message) -> List[ToolCall]:
        """
        parse the llm message into tools (given it has tool calls in it)
        :param t_msg: tool message
        :return:
        """
        ret = []

        matches = re.findall(r"<tool_call>(.*?)</tool_call>", t_msg.content, re.DOTALL)
        # convert each match into a function call
        for m in matches:
            tool_call = json.loads(m)
            tc = ToolCall(**tool_call)
            ret.append(tc)
        return ret
