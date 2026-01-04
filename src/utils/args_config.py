"""Config for CLI Arguments."""

from dataclasses import dataclass


@dataclass
class Config:
    """Cli arguments configuration"""

    map_path: str
    visibility: int
    max_steps: int
