from typing import Union
from pathlib import Path

import concurrent.futures
import urllib.request
import os
import urllib.error
from tqdm import tqdm
from http.client import IncompleteRead
import shutil
import sys

from .structures.tags import Tags, TagContent, MediaMetadata
from constants import (
    WINDOW_ILLEGAL_FILENAME_CHAR_LIST, 
    LINUX_ILLEGAL_FILENAME_CHAR_LIST, 
    MAC_ILLEGAL_FILENAME_CHAR_LIST
)


class DownloadSession:
    TEMP_FOLDER = 'temp_transfer_folder'
    def __init__(self, all_tags: Tags, location: Union[Path, str], worker_amt: int):
        self._tags = all_tags
        self._location = location
        self._worker_amt = worker_amt
        self._path_to_temp = os.path.join(location, self.TEMP_FOLDER)
        try:
            os.makedirs(self._path_to_temp, mode=0o777)
        except FileExistsError:
            pass

    @property
    def tags(self):
        return self._tags.tag_name
    
    def alter_name(self, tag):
        '''
        Alters the name of the doujin to make it suitable as a folder name for different types of OS
        :param tag: The desired tag
        :return: A OS-compatible name for the folder
        '''
        if sys.platform.startswith('linux'):
            for restriction in LINUX_ILLEGAL_FILENAME_CHAR_LIST:
                tag = tag.replace(restriction,"_")
        elif sys.platform.startswith("darwin"):
            for restriction in MAC_ILLEGAL_FILENAME_CHAR_LIST:
                tag = tag.replace(restriction, "_")
            if tag.startswith("."):
                tag = tag[1:]
        else:
            for restriction in WINDOW_ILLEGAL_FILENAME_CHAR_LIST:
                tag = tag.replace(restriction,"_")
        return tag

    def __contains__(self, item):
        return item in self._tags.tag_name
    
    def download(self, auto_save_to_other_tags):
        for tag_ind in range(len(self._tags)):
            self._single_tag_download(self._tags.tag_name[tag_ind], self._tags.tag_data[tag_ind], auto_save_to_other_tags)
            print(f"Completed downloading media files for tag {self._tags}")

    def _single_tag_download(self, tag_name: str, tag_data: TagContent, auto_save_to_other_tags: bool):
        args = ((tag_name, content, auto_save_to_other_tags) for content in tag_data.content)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._worker_amt
        ) as executor:
            executor.map(lambda f: self._single_file_download(*f), tqdm(args))

        for filename in os.listdir(self._path_to_temp):
            file_path = os.path.join(self._path_to_temp, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    @staticmethod
    def _has_finished_downloading_file(file_path, expected_size):
        if not os.path.isfile(file_path):
            return False
        return os.stat(file_path).st_size == expected_size

    def _single_file_download(self, tag_name: str, media_metadata: MediaMetadata, auto_save_to_other_tags: bool):
        media_id = media_metadata.media_id
        media_ext = media_metadata.media_ext
        media_url = media_metadata.media_url
        tags = media_metadata.media_tags
        file_size = media_metadata.media_size

        save_location = os.path.join(self._location, self.alter_name(tag_name))
        try:
            pic_name = str(media_id) + "." + str(media_ext)
            full_download_dir = self._path_to_temp + "/" + pic_name
            full_saved_dir = save_location + "/" + pic_name
            if self._has_finished_downloading_file(full_saved_dir, file_size):
                pass
            else:
                req = urllib.request.Request(media_url, headers={
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                  " AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/93.0.4577.63 Safari/537.36 Edg/92.0.902.84"})
                content = urllib.request.urlopen(req)
                with open(full_download_dir, 'wb') as downloaded_pic:
                    downloaded_pic.write(content.read())
                if auto_save_to_other_tags:
                    for sub_tag in tags.split():
                        if sub_tag in self._tags.tag_name:
                            tag_location = os.path.join(self._location, self.alter_name(sub_tag))
                            try:
                                os.makedirs(tag_location, mode = 0o777)
                            except FileExistsError:
                                pass

                            paste_loc = os.path.join(tag_location, pic_name)
                            shutil.copyfile(full_download_dir, paste_loc)

        except IncompleteRead:
            self._single_file_download(tag_name, media_metadata, auto_save_to_other_tags)

    




