from typing import Dict, Any, Literal
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: Dict
