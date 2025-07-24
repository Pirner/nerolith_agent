from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import os


# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_text_from_parts(parts):
    """Recursively extract plain text from email parts"""
    for part in parts:
        if part.get("parts"):
            # If this part has nested parts, recurse into them
            return get_text_from_parts(part["parts"])
        mime_type = part.get("mimeType")
        if mime_type == "text/plain":
            data = part["body"].get("data")
            if data:
                decoded = base64.urlsafe_b64decode(data).decode("utf-8")
                return decoded
    return None

def save_attachments(msg_id, parts):
    """Extract and save attachments"""
    for part in parts:
        filename = part.get("filename")
        body = part.get("body", {})
        att_id = body.get("attachmentId")
        if filename and att_id:
            attachment = service.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=att_id).execute()
            file_data = base64.urlsafe_b64decode(attachment['data'])
            with open(filename, 'wb') as f:
                f.write(file_data)
            print(f"Saved attachment: {filename}")


def get_gmail_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../../token.json'):
        creds = Credentials.from_authorized_user_file('../../token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../../token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, user_id='me', label_ids=['INBOX'], max_results=10):
    try:
        results = service.users().messages().list(userId=user_id, labelIds=label_ids, maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return
        print('Messages:')
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            parts = msg_data['payload'].get('parts', [])

            # Get message headers
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
            print(f"Subject: {subject}")
            # Extract and print plain text
            email_text = get_text_from_parts(parts) or "(No plain text found)"
            print("Body:", email_text)

            # Extract attachments
            save_attachments(msg['id'], parts)
            continue

            # Get message body
            for part in parts:
                mime_type = part['mimeType']
                if mime_type == 'text/plain':
                    data = part['body']['data']
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    print("Text body:", text)

                # Attachments
                if part.get('filename'):
                    att_id = part['body'].get('attachmentId')
                    if att_id:
                        attachment = service.users().messages().attachments().get(
                            userId='me', messageId=msg['id'], id=att_id).execute()
                        file_data = base64.urlsafe_b64decode(attachment['data'])
                        with open(part['filename'], 'wb') as f:
                            f.write(file_data)
                        print(f"Saved attachment: {part['filename']}")
    except Exception as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    service = get_gmail_service()
    list_messages(service)