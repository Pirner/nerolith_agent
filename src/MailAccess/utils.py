import base64

from src.MailAccess.DTO import Email


class MailUtils:
    @staticmethod
    def parts_has_attachments(parts):
        """
        check whether the parts have an attachment
        :param parts: check for attachments in there
        :return:
        """
        for part in parts:
            filename = part.get("filename")
            body = part.get("body", {})
            att_id = body.get("attachmentId")
            if filename and att_id:
                return True
        return False

    @staticmethod
    def get_text_from_parts(parts):
        """Recursively extract plain text from email parts"""
        for part in parts:
            if part.get("parts"):
                # If this part has nested parts, recurse into them
                return MailUtils.get_text_from_parts(part["parts"])
            mime_type = part.get("mimeType")
            if mime_type == "text/plain":
                data = part["body"].get("data")
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode("utf-8")
                    return decoded
        return None

    @staticmethod
    def convert_email(message) -> Email:
        parts = message['payload'].get('parts', [])

        # Get message headers
        headers = message.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
        # print(f"Subject: {subject}")
        # Extract and print plain text
        email_text = MailUtils.get_text_from_parts(parts) or "(No plain text found)"
        # print("Body:", email_text)
        has_attachments = MailUtils.parts_has_attachments(parts=parts)
        email = Email(subject, email_text, has_attachments, message['id'])
        return email
