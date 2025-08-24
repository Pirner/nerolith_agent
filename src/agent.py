from typing import List

from src.llm.DTO import Message
from src.llm.parsing.md_parser import MarkdownParser
from src.llm.LLMConnector import LLMConnector
from src.llm.PromptUtils import PromptUtils
from src.llm.Tools.DTO import ToolCall
from src.llm.Tools.ToolUtils import ToolUtils
from src.llm.Tools.ToolParser import LLMToolParser
from src.llm.Tools.ArxivTools import ArxivTools
from src.MailAccess.GmailConnector import GmailConnector
from src.MailAccess.DTO import Email
from src.OneDriveAccess.OneDriveManager import OneDriveManager


class NerolithAgent:
    llm_connector = None
    server_ip = None
    port = None

    token_filepath = 'token.json'
    gmail_connector = None
    od_manager = None

    def __init__(self):
        self.od_manager = OneDriveManager(local_path=r'C:\Users\steph\OneDrive')

    def call_tool(self, t: ToolCall):
        if t.name == 'get_weather':
            res = ArxivTools.get_weather(**t.arguments)
        elif t.name == 'add':
            res = ArxivTools.add(**t.arguments)
        else:
            raise Exception('unknown tool')
        return res

    def process_tools(self, t_msg: Message) -> List[Message]:
        messages = []
        tools = LLMToolParser.parse_message_to_tools(t_msg)
        for t in tools:
            ret = self.call_tool(t=t)
            content = f'''
            {t}: return: {ret}
            '''
            m = Message(role='assistant', content=content)
            messages.append(m)
        return messages

    def process_messages(self, messages: List[Message], tools):
        """
        process the messages that are given to the agent.
        :param messages: the messages, so the whole conversation to process
        :param tools: which tools are available from a function definition standpoint to the agent
        :return:
        """
        all_messages = [] + messages
        if tools is None:
            response = self.llm_connector.call_messages(messages=messages)
        else:
            response = self.llm_connector.call_messages(messages=messages, tools=tools)
        if response.status_code != 200:
            print('failed llm response with: ', response.status_code)
        response = response.json()
        response_msg = Message(role='assistant', content=response['outputs'])
        all_messages.append(response_msg)
        if ToolUtils.has_tools(msg=response_msg):
            tool_messages = self.process_tools(t_msg=response_msg)
            # create a last response from the tools messages
            all_messages += tool_messages
            format_response = self.llm_connector.call_messages(all_messages)
            return format_response
        else:
            return response_msg

    def configure_connector(self, server_ip: str, port: int):
        """
        configure the connector for the llm interaction
        :param server_ip: ip to the server for local api call
        :param port: under which port the model is running
        :return:
        """
        self.server_ip = server_ip
        self.port = port
        self.llm_connector = LLMConnector(server_ip=self.server_ip, port=self.port)

    def retrieve_emails(self):
        self.gmail_connector = GmailConnector(token_filepath=self.token_filepath)
        messages = self.gmail_connector.get_messages()
        return messages

    def _create_paper_summary(self, email: Email):
        """
        creates given an email with an attachment a summary of the paper
        :param email: the email that holds the paper
        :return:
        """
        # download the attachment
        attachments = self.gmail_connector.get_attachments(email=email)
        if len(attachments) != 1:
            raise Exception('have an unsupported number of attachments: {}'.format(len(attachments)))
        exit(0)

    def _create_zettelkasten_entry(self, email: Email):
        """
        create a zettelkasten entry from the given email
        :param email: the email to create a zettelkasten entry for the inbox
        :return:
        """
        print('[INFO] creating a zettelkasten entry from the given email.')
        # check if it has an attachment
        if email.has_attachment:
            self._create_paper_summary(email=email)

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that creates notes.\n\nCurrent Date: 2024-08-31 /no_think"},
            {
                "role": "user",
                "content": f"""
                    Summarize the information below in markdown format and construct it like an article.
                    
                    {email.email_text}
                """},
        ]
        messages = [Message(role=x['role'], content=x['content']) for x in messages]
        response = self.llm_connector.call_messages(messages=messages)
        if response.status_code != 200:
            raise Exception('received status code unequal to 200 when communicating with llm: ', response)
        # parse the message -> get proper markdown which can be further processed
        json_response = response.json()
        md_parsed = MarkdownParser.parse_markdown(text=json_response['outputs'])
        # append original email test
        final_md = f"""{md_parsed}\n\n-----------------------------------------------------------------------------------------------------------\n\nOriginal: {email.email_text}"""

        # find a title for this
        title_response = self.llm_connector.call_messages(
            messages=PromptUtils.create_new_messages_with_agent_plot(prompt='{} create a filename for the text before only 4 words response ONLY with the filename and add .md extension. /no_think'.format(email.email_text)))
        if title_response.status_code != 200:
            raise Exception('received status code unequal to 200 when communicating with llm: ', title_response)
        # parse the message -> get proper markdown which can be further processed
        title_response = title_response.json()
        title = MarkdownParser.parse_title(text=title_response['outputs'])
        # write it into the zettelkasten
        self.od_manager.store_markdown(
            relative_path=r'Zettelkasten\Inbox',
            markdown=final_md,
            title=title,
        )

        # TODO mark email as done
        # Get your label ID (e.g., for folder 'Processed')
        label_name = 'processed'
        # labels = self.gmail.service.users().labels().list(userId='me').execute()
        labels = self.gmail_connector.service.users().labels().list(userId='me').execute()
        label_id = next((label['id'] for label in labels['labels'] if label['name'] == label_name), None)

        if label_id:
            self.gmail_connector.modify_message(
                email.message_id,
                add_labels=[label_id],
                remove_labels=['UNREAD'],
            )
        else:
            print(f"Label '{label_name}' not found.")

        # TODO - include summarization of file for papers.

    def process_email(self, email: Email):
        """
        process an email and act upon the email as communication space
        :param email: the email to process
        :return:
        """
        # decide what to do with the email
        if 'zettelkasten' in email.subject.lower():
            self._create_zettelkasten_entry(email=email)
        else:
            print('Not sure how to process this email?')
