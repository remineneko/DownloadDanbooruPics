from dataclasses import dataclass


@dataclass
class MediaMetadata:
    media_id: int
    media_ext: str
    media_url: str
    media_tags: str
    media_size: int
    
