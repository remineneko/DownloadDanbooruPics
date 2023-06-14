from dataclasses import dataclass
from enum import Enum


class MediaExt(Enum):
    ZIP = 0
    GIF = 1
    JPG = 2
    PNG = 3
    MP4 = 4


@dataclass
class MediaMetadata:
    media_id: int
    media_ext: MediaExt
    media_size: int
    media_tags: str
    media_url: str
