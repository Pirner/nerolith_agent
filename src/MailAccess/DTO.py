from dataclasses import dataclass


@dataclass
class Email:
    subject: str
    email_text: str
    has_attachment: bool
