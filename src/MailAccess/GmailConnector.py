import os.path
import base64

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from src.MailAccess.DTO import Email, Attachment


class GmailConnector:
    token_filepath: str
    # scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    scopes = ['https://www.googleapis.com/auth/gmail.modify']
    service = None

    def __init__(self, token_filepath: str):
        self.token_filepath = token_filepath
        self.service = self._get_gmail_service()

        user_id = 'me'
        label_ids = ['INBOX']
        max_results = 10
        self.attachments = None

    def _process_parts(self, parts, email: Email):
        for p in parts:
            # Recurse into sub-parts
            if p.get("parts"):
                self._process_parts(p["parts"], email)
                continue

            filename = p.get("filename")
            body = p.get("body", {})
            att_id = body.get("attachmentId")

            if filename and att_id:
                # Fetch attachment
                attachment = self.service.users().messages().attachments().get(
                    userId='me',
                    messageId=email.message_id,
                    id=att_id
                ).execute()

                data = attachment.get("data")
                if data:
                    file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))

                    # file_path = os.path.join(save_dir, filename)
                    # with open(filename, "wb") as f:
                    # f.write(file_data)
                    self.attachments.append(Attachment(filename=filename, data=data))
                    # saved_files.append(file_path)

    def get_attachments(self, email: Email):
        saved_files = []

        # Fetch the message
        message = self.service.users().messages().get(userId='me', id=email.message_id, format='full').execute()
        payload = message.get("payload", {})
        parts = payload.get("parts", [])
        self.attachments = []
        self._process_parts(parts, email)
        return self.attachments

    def _get_gmail_service(self):
        creds = None
        # the token.json stores the user's access and refreshes tokens.
        if os.path.exists(self.token_filepath):
            creds = Credentials.from_authorized_user_file('token.json', self.scopes)
            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)
        return service

    def get_messages(self, user_id='me', label_ids=None, max_results=10):
        """
        retrieve all messages from the gmail service to start processing
        :param user_id: user id to pull from
        :param label_ids: label id to retrieve from
        :param max_results: maximum number of messages to extract
        :return:
        """
        if label_ids is None:
            label_ids = ['INBOX', 'UNREAD']
        results = self.service.users().messages().list(
            userId=user_id,
            labelIds=label_ids,
            maxResults=max_results
        ).execute()
        messages = results.get('messages', [])
        messages = [self.service.users().messages().get(userId='me', id=msg['id']).execute() for msg in messages]
        return messages

    def modify_message(self, msg_id: str, add_labels: list = None, remove_labels: list = None):
        """
        Modify a message: add or remove labels (e.g., mark as read, move to folder).
        :param msg_id: The ID of the message to modify
        :param add_labels: List of labels to add (e.g., a folder label)
        :param remove_labels: List of labels to remove (e.g., 'UNREAD' to mark as read)
        """
        if add_labels is None:
            add_labels = []
        if remove_labels is None:
            remove_labels = []

        body = {
            'addLabelIds': add_labels,
            'removeLabelIds': remove_labels
        }

        message = self.service.users().messages().modify(
            userId='me',
            id=msg_id,
            body=body
        ).execute()

        return message
