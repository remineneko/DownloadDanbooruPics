from pybooru import Danbooru, exceptions

import concurrent.futures
import urllib.request
import os
import urllib.error
from tqdm import tqdm
from http.client import IncompleteRead
import asyncio
import requests
from bs4 import BeautifulSoup
import re
import shutil
import sys

from constants import (
    WINDOW_ILLEGAL_FILENAME_CHAR_LIST,
    LINUX_ILLEGAL_FILENAME_CHAR_LIST,
    MAC_ILLEGAL_FILENAME_CHAR_LIST,
    MAX_POST_PER_PAGE,
    GOLD_PAGE_SEARCH_LIMIT,
    NORMAL_PAGE_SEARCH_LIMIT,
    SITENAME,
    USERNAME,
    API_KEY,
    DEFAULT_DOWNLOAD_PARENT_LOCATION
)
from src.structures import Database, DownloadSession, CustomDanbooru


class DanbooruDownloader:
    TEMP_FOLDER = 'temp_transfer_folder'
    def __init__(
            self, 
            tag:str = None, 
            location:str = DEFAULT_DOWNLOAD_PARENT_LOCATION, 
            username = USERNAME, 
            api_key = API_KEY
        ):
        '''
            Initialize the downloader
            :param tag: A Danbooru tag.
            :param location: A path to the folder where you want the data to be installed.
            :param username: Danbooru username.
            :param api_key: API key for the username.

            > Credits to username Shishio-kun on MyAnimeList for the search guide <
            How to search Danbooru
                You can enter a term like Vocaloid on Danbooru and get a lot of awesome Vocaloid pics.

                If you want to search a term with two or more words in it, like Hatsune Miku,
                each word needs to be separated by an underscore: Hatsune_Miku.

                Proper names of Japanese characters like Mio Akiyama need to be entered last name first (proper Japanese)
                so for her it would be Akiyama_Mio. If you tried searching Mio_Akiyama you won't get anything.

                Finally if you want to search multiple terms to narrow down the search you can only enter two at once,
                but this still gives you a lot of variety. Separate the terms with a space.
                For example: Akiyama_Mio black_bikini will net you all pictures of Mio in a black bikini!

            Searching Danbooru clean (filter out the hentai)
                There's a lot of ecchi and hentai on Danbooru in addition to really good clean images.
                If you want to filter it out, search this tag with whatever tag you're using: -rating:e
            > End searching guide <

            
            '''
        if tag is None:
            self._location = location
        else:
            self._location = location
            self._pure_tag = tag
            self._tag = tag + f" limit:{MAX_POST_PER_PAGE}" # minimize number of pages needed to be searched
            self._tag_amt_page = self._num_pages()
            print(f"Found {self._tag_amt_page} pages for tag {self._pure_tag}")

            self.access = CustomDanbooru(site_name=SITENAME, username=username,api_key=api_key)
            self.page_limit = GOLD_PAGE_SEARCH_LIMIT if self.access.is_gold(username) else NORMAL_PAGE_SEARCH_LIMIT
            print(f"User {username} can load {self.page_limit} pages per tag.")

        self._path_to_temp = os.path.join(location, self.TEMP_FOLDER)
        try:
            os.makedirs(self._path_to_temp, mode=0o777)
        except FileExistsError:
            pass

        self._db = Database()

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

    def _num_pages(self):
        base_url = f"https://danbooru.donmai.us/posts?tags={self._pure_tag}+limit%3A{MAX_POST_PER_PAGE}"
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        req = requests.get(base_url, headers = header)
        soup = BeautifulSoup(req.text, "html.parser")
        ans_dict = {}
        for t in soup.find_all("a", class_ = "paginator-page desktop-only"):
            href = t['href']
            page_re = re.findall("/posts\?page=(\d+)", str(href))
            if len(page_re) != 0:
                res = int(page_re[0])
                ans_dict[res] = 1
        try:
            return max(list(ans_dict.keys()))
        except ValueError:
            return 1

    def get_amt_post_saved(self):
        return self._db.get_number_of_pictures_for_a_tag(self._tag)

    async def page_search(self, page):
        # print('\r', f"Searching pictures in page {page} for tag {self._pure_tag}",end = '')
        post_list = []
        end_run_again = False
        # force retry when Danbooru decides to timeout the boi.
        while not end_run_again:
            try:
                post_list = self.access.post_list(page=page, tags=self._tag)
                end_run_again = True
            except exceptions.PybooruHTTPError as e:
                pass
        return post_list

    @staticmethod
    async def _async_range_ft(from_point, to_point):
        for i in range(from_point, to_point):
            yield i
            await asyncio.sleep(0.0)

    async def _all_result(self):
        all_res = []
        print(f"Obtaining metadata for pictures with tag {self._pure_tag}")
        async for i in self._async_range_ft(1, self._tag_amt_page + 1):
            all_res.append(self.page_search(i))

        # asyncio.as_completed() takes an iterable of coroutines or futures and
        # returns an iterable of futures in the order that the input futures complete
        return [await f for f in tqdm(asyncio.as_completed(all_res), total=len(all_res), desc=self._pure_tag, position=0, leave= True)]

    async def initial_update(self):
        # update the entries of a tag into the DB for the first time.
        res = await self._all_result()
        print(f"Updating entries for tag {self._pure_tag}")
        for page_data in res:
            for post in page_data:
                try:
                    file_url, file_id, file_ext, file_tags, file_size = post['file_url'], \
                                                                        post['id'], \
                                                                        post['file_ext'], \
                                                                        post['tag_string'], \
                                                                        post['file_size']
                    if len(str(file_id)) != 0 and len(file_ext) != 0 and len(file_url) != 0:
                        self._db.add_values(str(file_tags).replace("'", "''"), file_id, str(file_ext), str(file_url), file_size)
                except KeyError:
                    pass
        print(f"Updated entries for tag {self._pure_tag}")

    async def update_(self):
        # I do wish there would be a better way to update this entire ordeal.
        # Danbooru shows posts from newest to oldest, automatically, and apparently there is no way
        # to change the sorting manner, without having the searcher cancels the search
        # *ehem* order:created_at_asc *ehem*
        # it cancels search if the tag contains far too many entires
        # this really makes the update runs longer than it should by a very long mile.
        start_page = 1
        cont_access = True
        while cont_access and start_page <= self.page_limit:
            res = await self.page_search(start_page)
            if len(res) == 0:
                cont_access = False
            else:
                for post in res:
                    try:
                        file_url, file_id, file_ext, file_tags, file_size = post['file_url'], \
                                                                            post['id'], \
                                                                            post['file_ext'], \
                                                                            post['tag_string'], \
                                                                            post['file_size']
                        if len(str(file_id)) != 0 and len(file_ext) != 0 and len(file_url) != 0:
                            if self._db.isEntryExist(file_id):
                                cont_access = False
                                break
                            else:
                                self._db.add_values(str(file_tags).replace("'", "''"), file_id, str(file_ext), str(file_url), file_size)
                    except KeyError:
                        pass
            start_page += 1
        print(f"Updated entries for tag {self._pure_tag}\n")

    async def multiple_update(self, tags):
        # I really thought I could use threading.Thread for this, but Danbooru returned 423 on my ass.
        await asyncio.gather(*[asyncio.create_task(DanbooruDownloader(tag).update_()) for tag in tags])

    async def multiple_full_update(self, tags):
        await asyncio.gather(*[asyncio.create_task(DanbooruDownloader(tag).initial_update()) for tag in tags])

    @staticmethod
    def has_finished_downloading_file(file_path, expected):
        if not os.path.isfile(file_path):
            return False
        return os.stat(file_path).st_size == expected

    def _download(self, entry, session: DownloadSession, tag_index):
        media_id, media_ext, media_url, tags, file_size = entry

        # first part: get the download location
        save_location = os.path.join(self._location, self.alter_name(session.tags[tag_index]))
        try:
            pic_name = str(media_id) + "." + str(media_ext)
            full_download_dir = self._path_to_temp + "/" + pic_name
            full_saved_dir = save_location + "/" + pic_name
            if self.hasFinishedDownloadingFile(full_saved_dir, file_size):
                pass
            else:
                req = urllib.request.Request(media_url, headers={
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                  " AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/93.0.4577.63 Safari/537.36 Edg/92.0.902.84"})
                content = urllib.request.urlopen(req)
                with open(full_download_dir, 'wb') as downloaded_pic:
                    downloaded_pic.write(content.read())
                for sub_tag in tags.split():
                    if sub_tag in session:
                        tag_location = os.path.join(self._location, self.alter_name(sub_tag))
                        try:
                            os.makedirs(tag_location, mode = 0o777)
                        except FileExistsError:
                            pass

                        paste_loc = os.path.join(tag_location, pic_name)
                        shutil.copyfile(full_download_dir, paste_loc)

        except IncompleteRead:
            self._download(entry, session, tag_index)

    def concur_download(self, session):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=5
        ) as executor:
            future_to_url = {
                executor.submit(self._download, *(pic, session)): pic for pic in tqdm(self._db.all_entries(), total = self._db.get_number_of_pictures())
            }
            for future in tqdm(concurrent.futures.as_completed(future_to_url)):
                pic_data = future_to_url[future]
                try:
                    future.result()
                except Exception as e:
                    print(e)
                    pass

    async def mock_download(self, tag, session, tag_index):
        args = ((p, session, tag_index) for p in self._db.all_values_by_tag(tag))
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=8
        ) as executor:
            executor.map(lambda f: self._download(*f), tqdm(args))

        for filename in os.listdir(self._path_to_temp):
            file_path = os.path.join(self._path_to_temp, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))