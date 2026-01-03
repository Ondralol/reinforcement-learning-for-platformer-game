"""Config for CLI Arguments."""
from dataclasses import dataclass

@dataclass
class Config:
    map_path: str
    visibility: int
    max_steps: int