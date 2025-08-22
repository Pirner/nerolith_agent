from dataclasses import dataclass
from typing import Dict


@dataclass
class Email:
    subject: str
    email_text: str
    has_attachment: bool
    message_id: str


@dataclass
class Attachment:
    filename: str
    data: bytes
