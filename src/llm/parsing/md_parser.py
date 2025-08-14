import re


class MarkdownParser:
    @staticmethod
    def remove_think(text: str) -> str:
        cleaned_text = re.sub(r'\n?\s*<think>.*?</think>\s*\n?', '', text, flags=re.DOTALL)
        return cleaned_text

    @staticmethod
    def parse_markdown(text: str) -> str:
        """
        parse llm output and find the proper markdown in between
        :param text: the text to parse into markdown
        :return:
        """
        # remove all the tags and thinking stuff from the response
        # cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        cleaned_text = MarkdownParser.remove_think(text)
        cleaned_text = cleaned_text.replace('<|im_end|>', '')
        cleaned_text = cleaned_text.strip('\n ')
        return cleaned_text

    @staticmethod
    def parse_title(text: str) -> str:
        """
        parse from a given llm output the title
        :param text: find the title
        :return:
        """
        text_tbp = MarkdownParser.remove_think(text)
        text_tbp = text_tbp.replace('*', ' ')
        text_tbp = text_tbp.replace('<|im_end|>', ' ')

        string_splits = text_tbp.split(' ')
        for split in string_splits:
            if '.md' in split:
                return split
        raise Exception('Did not find valid filename in this string: ', text)
