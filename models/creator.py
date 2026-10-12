from dataclasses import dataclass

@dataclass
class Creator:
    id: int
    name: str
    handle: str
    niche: str
    platform: str
    followers: int
    engagement: float
    rate: float
    location: str
    bio: str
    image_url: str = ""
