import random

from src.llm.Tools.ToolParser import LLMToolParser


class ArxivTools:
    @staticmethod
    def get_weather(location: str) -> str:
        """This tool returns the current weather situation.
        Args:

        Returns:
            str:"Weather situation"
            Example Response cloudy
            """
        # Specify stock ticker
        weather_situations = ['cloudy', 'rainy', 'sunny', 'foobar']
        return random.choice(weather_situations)

    @staticmethod
    def add(x: float, y: float) -> float:
        """
        this function adds up the value of x and y
        :param x: first parameter of the addition
        :param y: second parameter of the addition
        :return: result of the addition of x and y
        """
        return x + y

    @staticmethod
    def get_tools():
        """
        gather all the tools for ArxivTools
        :return:
        """
        tools = [ArxivTools.add, ArxivTools.get_weather]
        tools = [LLMToolParser.function_to_json(x) for x in tools]
        return tools
