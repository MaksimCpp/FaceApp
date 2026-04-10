from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PersonalDTO:
    id: int
    full_name: str
    embedding: Optional[List[float]] = None
    