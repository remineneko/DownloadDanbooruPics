from typing import List
from .tags import Tags, TagMetadata, MediaMetadata


class DownloadSession:
    def __init__(self, all_tags: Tags):
        self._tags = all_tags

    @property
    def tags(self):
        return self._tags.tag_name

    def __contains__(self, item):
        return item in self._tags.tag_name
    
    def download(self):
        pass

    def _single_tag_download(self, tag_name: List[str], tag_data: List[TagMetadata]):
        pass

    def _single_file_download(self):
        pass





