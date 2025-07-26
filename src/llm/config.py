from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    model_path: str
    transformer_based: Optional[bool] = False
