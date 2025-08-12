from src.llm.DTO import Message
from src.llm.LLMConnector import LLMConnector
from src.MailAccess.GmailConnector import GmailConnector
from src.MailAccess.DTO import Email


class NerolithAgent:
    llm_connector = None
    server_ip = None
    port = None

    token_filepath = 'token.json'
    gmail_connector = None

    def __init__(self):
        pass

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

    def _create_zettelkasten_entry(self, email: Email):
        """
        create a zettelkasten entry from the given email
        :param email: the email to create a zettelkasten entry for the inbox
        :return:
        """
        print('[INFO] creating a zettelkasten entry from the given email.')
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that creates notes.\n\nCurrent Date: 2024-08-31 /no_think"},
            {
                "role": "user",
                "content": f"""
                    Summarize the information below in markdown format
                    
                    {email.email_text}
                """},
        ]
        messages = [Message(role=x['role'], content=x['content']) for x in messages]
        response = self.llm_connector.call_messages(messages=messages)
        print(response.text)
        raise Exception('foobar')

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
            raise Exception('agent is not sure what to do.')
