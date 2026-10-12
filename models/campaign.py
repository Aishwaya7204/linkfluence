from dataclasses import dataclass

@dataclass
class Campaign:
    id: int
    brand_name: str
    title: str
    niche: str
    platform: str
    budget: float
    target_followers: int
    description: str
