import requests
from bs4 import BeautifulSoup
import re
from pybooru import exceptions

from constants import (
    MAX_POST_PER_PAGE,
    GOLD_PAGE_SEARCH_LIMIT,
    NORMAL_PAGE_SEARCH_LIMIT
)
from src.structures import (
    Database, 
    CustomDanbooru,
    MediaMetadata,
    TagContent,
    Tags
)


class BaseTagHandler:
    def __init__(self, access: CustomDanbooru, tag: str, db: Database):
        self._tag = tag
        self._tag_to_search = tag + f" limit:{MAX_POST_PER_PAGE}"
        self._db = db
        self._access = access
        self._post_limit = GOLD_PAGE_SEARCH_LIMIT if self.access.is_gold() else NORMAL_PAGE_SEARCH_LIMIT


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
        
    def convert_to_tag_object(self):
        tag_name = self._tag
        tag_data = TagContent([
            MediaMetadata(*e) for e in self._db.all_values_by_tag(self._tag)
        ])
        return Tags(tag_name=tag_name, tag_data=tag_data)
        

class TagHandler(BaseTagHandler):
    def page_search(self, page):
        post_list = []
        end_run_again = False
        # force retry when Danbooru decides to timeout the boi.
        while not end_run_again:
            try:
                post_list = self.access.post_list(page=page, tags=self._tag_to_search)
                end_run_again = True
            except exceptions.PybooruHTTPError as e:
                print(f"An exception occurred while loading page {page} of tag {self._tag}: {e}")
                print("Retrying...")
        return post_list

    def update(self, ignore_duplicate=False):
        start_page = 1
        cont_access = True
        while cont_access and start_page <= self.page_limit:
            res = self.page_search(start_page)
            if len(res) == 0:
                cont_access = False
            else:
                for post in res:
                    try:
                        file_url = post['file_url']
                        file_id = post['id']
                        file_ext = post['file_ext']
                        file_tags = post['tag_string']
                        file_size = post['file_size']
                        if len(str(file_id)) != 0 and len(file_ext) != 0 and len(file_url) != 0:
                            if self._db.isEntryExist(file_id) and not ignore_duplicate:
                                cont_access = False
                                break
                            else:
                                self._db.add_values(str(file_tags).replace("'", "''"), file_id, str(file_ext), str(file_url), file_size)
                    except KeyError:
                        pass
            start_page += 1
        print(f"Updated entries for tag {self._tag}\n")


class AsyncTagHandler(BaseTagHandler):
    async def page_search(self, page):
        post_list = []
        end_run_again = False
        # force retry when Danbooru decides to timeout the boi.
        while not end_run_again:
            try:
                post_list = self.access.post_list(page=page, tags=self._tag_to_search)
                end_run_again = True
            except exceptions.PybooruHTTPError as e:
                print(f"An exception occurred while loading page {page} of tag {self._tag}: {e}")
                print("Retrying...")
        return post_list

    async def update(self, ignore_duplicate=False):
        start_page = 1
        cont_access = True
        while cont_access and start_page <= self.page_limit:
            res = await self.page_search(start_page)
            if len(res) == 0:
                cont_access = False
            else:
                for post in res:
                    try:
                        file_url = post['file_url']
                        file_id = post['id']
                        file_ext = post['file_ext']
                        file_tags = post['tag_string']
                        file_size = post['file_size']
                        if len(str(file_id)) != 0 and len(file_ext) != 0 and len(file_url) != 0:
                            if self._db.isEntryExist(file_id) and not ignore_duplicate:
                                cont_access = False
                                break
                            else:
                                self._db.add_values(str(file_tags).replace("'", "''"), file_id, str(file_ext), str(file_url), file_size)
                    except KeyError:
                        pass
            start_page += 1
        print(f"Updated entries for tag {self._tag}\n")