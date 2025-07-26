from src.agent.nerolith import Nerolith
from src.MailAccess.GmailConnector import GmailConnector


def main():
    gmail_connector = GmailConnector(token_filepath='token.json')
    messages = gmail_connector.get_messages()
    main_agent = Nerolith()
    for msg in messages:
        main_agent.process_message(message=msg)


if __name__ == '__main__':
    main()
