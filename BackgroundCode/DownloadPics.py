# Author: Hoang V. Tran
# Start Date: 30/11/2019

from pybooru import Danbooru
import urllib.request
import os
import settings
import urllib.error
from BackgroundCode.DumpToPickle import DumpToPickle


ANON_SEARCH_LIMIT = 1000


class DownloadDanbooruPics:
    def __init__(self,tag):
        '''

        :param tag:
        '''
        self.__tag = tag
        self.__isAltered = False
        for char in tag:
            if char in settings.SPECIAL_CHARACTERS:
                tag = tag.replace(char,"_")
                self.__isAltered = True
        if self.__isAltered:
            self.__temp_tag = tag
            self.__JSON_path = os.path.join(settings.JSON_FILES_PATH, str(self.__temp_tag + ".json"))
            self.__pickle_path = os.path.join(settings.PICKLE_FILES_PATH, str(self.__temp_tag))
            self.__page_counter_path = os.path.join(settings.TAG_PAGE_COUNTERS_PATH, str(self.__temp_tag + ".txt"))
            self.__tag_run_counter_path = os.path.join(settings.TAG_RUN_COUNTER, str(self.__temp_tag + ".txt"))
        else:
            self.__JSON_path = os.path.join(settings.JSON_FILES_PATH, str(self.__tag + ".json"))
            self.__pickle_path = os.path.join(settings.PICKLE_FILES_PATH, str(self.__tag))
            self.__page_counter_path = os.path.join(settings.TAG_PAGE_COUNTERS_PATH, str(self.__tag + ".txt"))
            self.__tag_run_counter_path = os.path.join(settings.TAG_RUN_COUNTER, str(self.__tag + ".txt"))
        self.__print()
        self.__obtain_post_list()

    def __print(self):
        '''
        Prints the downloading UI for the program.
        '''
        print("----------------------------------------- Danbooru Downloader -----------------------------------------")
        print("~Welcome to the Danbooru Downloader")
        print("~Received tag:", self.__tag)

    def __obtain_access(self):
        '''
        Gets access to Danbooru
        :return: Access to Danbooru
        '''
        return Danbooru(site_name='danbooru')

    def __obtain_post_list(self):
        '''
        Gets the posts from a searched tag in Danbooru.
        The posts' information are stored in a pickle altogether as a list, and each post is saved in the following format:
        {'id': ,
         'created_at': ,
         'uploader_id': ,
         'score': ,
         'source': ,
         'md5': ,
         'last_comment_bumped_at': ,
         'rating': ,
         'image_width': ,
         'image_height': ,
         'tag_string':,
         'is_note_locked':,
         'fav_count': ,
         'file_ext': ,
         'last_noted_at': ,
         'is_rating_locked': ,
         'parent_id': ,
         'has_children': ,
         'approver_id': ,
         'tag_count_general': ,
         'tag_count_artist': ,
         'tag_count_character': ,
         'tag_count_copyright': ,
         'file_size': ,
         'is_status_locked': ,
         'pool_string': ,
         'up_score': ,
         'down_score': ,
         'is_pending': ,
         'is_flagged': ,
         'is_deleted': ,
         'tag_count': ,
         'updated_at': ,
         'is_banned':,
         'pixiv_id': ,
         'last_commented_at': ,
         'has_active_children':,
         'bit_flags': ,
         'tag_count_meta': ,
         'uploader_name': ,
         'has_large':,
         'has_visible_children': ,
         'children_ids': ,
         'is_favorited': ,
         'tag_string_general': ,
         'tag_string_character': ,
         'tag_string_copyright': ,
         'tag_string_artist': ,
         'tag_string_meta': ,
         'file_url': ,
         'large_file_url':,
         'preview_file_url': }

        Since a tag can have a lot of posts, this function can be rerunned so that the posts can be fully added.
        Note that the limit of search page for anonymous users and members is 1000,
            while that for Gold and Platinum users is 2000 and 5000, respectively.

        '''
        access = self.__obtain_access()
        start = 1
        if os.path.isfile(self.__page_counter_path):
            with open(self.__page_counter_path, 'r') as current_counter:
                start = int(float(current_counter.read()))
        else:
            with open(self.__page_counter_path, 'w') as new_counter:
                new_counter.write(str(start))
                new_counter.close()
        continue_access = True
        while continue_access:
            print("Loading page", start)
            if start > ANON_SEARCH_LIMIT:
                print("This is the limit to search for Anonymous users.\
                 To have more pages in search, please upgrade to Gold or Platinum.")
                continue_access = False
            else:
                try:
                    post_list_obtained = access.post_list(page=start, tags = self.__tag)
                    if len(post_list_obtained) != 0:
                        try:
                            cur_data = self.__load_pickle()
                            cur_data.extend(post_list_obtained)
                            DumpToPickle(self.__pickle_path,cur_data).DumpToPickle()
                        except FileNotFoundError:
                            DumpToPickle(self.__pickle_path,post_list_obtained).DumpToPickle()
                    else:
                        continue_access = False
                except KeyError:
                    continue_access = False
                req_write = open(self.__page_counter_path,'w')
                req_write.write(str(start))
                req_write.close()
                print("Loaded page",start)
                start += 1
        if os.stat(self.__pickle_path).st_size == 0:
            print("There is no posts available for the given tag. Please try again.")
        os.remove(self.__page_counter_path)

    def __load_pickle(self):
        '''
        Loads the pickle
        :return: The loaded pickle
        :type: list
        '''
        return DumpToPickle(self.__pickle_path).loadPickle()

    def __obtain_post_ID(self, post):
        '''
        Gets the post's ID
        :param post: A Danbooru post
        :return: The post's ID
        :type: int
        '''
        return post['id']

    def __obtain_post_file_ext(self, post):
        '''
        Gets the post's file extension
        :param post: A Danbooru post
        :return: The file's extension
        :type: str
        '''
        try:
            return post['file_ext']
        except KeyError:
            return None

    def __obtain_post_file_url(self,post):
        '''
        Gets the post's picture's download link
        :param post: A Danbooru post
        :return: The download link for the picture in the post
        '''
        try:
            return post['file_url']
        except KeyError:
            return None

    def __obtain_all_post_ID(self):
        '''
        Gets every obtained posts' IDs
        :return: A list of IDs
        :type: list
        '''
        id_list = []
        post_list = self.__load_pickle()
        for post in post_list:
            id_list.append(self.__obtain_post_ID(post))
        return id_list

    def __obtain_all_post_file_url(self):
        '''
        Gets every posts' pictures' download URLs
        :return: A list of links
        :type: list
        '''
        all_url = []
        post_list = self.__load_pickle()
        no_url = []
        for post in post_list:
            url = self.__obtain_post_file_url(post)
            if url is not None:
                all_url.append(url)
            else:
                all_url.append(url)
                no_url.append(url)
        print("Finish appending",len(all_url),"entries for tag", self.__tag, "to download with", len(no_url),
              "pictures with no download link")
        if len(all_url) == 0:
            os.remove(self.__pickle_path)
        return all_url

    def __obtain_all_file_ext(self):
        '''
        Gets every posts' file extensions
        :return: A list of file extensions
        '''
        ext_list = []
        post_list = self.__load_pickle()
        for post in post_list:
            ext_list.append(self.__obtain_post_file_ext(post))
        return ext_list

    def __is_finished_scraping(self, data_list, file):
        '''
        Checks if a tag has all currently posted pictures downloaded
        :param data_list: A data list related to the posts. This could be, including but not limited to, a list of URLs or
        a list of IDs.
        :param file: A file, usually a counter.
        :return: True if all pictures have been downloaded, False otherwise
        '''
        with open(file,'r') as f:
            if os.stat(file).st_size != 0:
                current_num = int(float(f.read()))
                if current_num == len(data_list) - 1:
                    finished_downloading = True
                else:
                    finished_downloading = False
            else:
                finished_downloading = False
        return finished_downloading

    def __download_pictures(self):
        '''
        Downloads the pictures
        '''
        url_list = self.__obtain_all_post_file_url()
        if len(url_list) != 0:
            id_list = self.__obtain_all_post_ID()
            ext_list = self.__obtain_all_file_ext()
            download_base_location = "C:\\Users\\Hoang Tran\\Desktop\\Danbooru Collection"
            if self.__isAltered:
                download_actual_location = download_base_location + "\\" + self.__temp_tag
                file_counter_location = os.path.join(settings.TAG_COUNTERS_PATH, str(self.__temp_tag + "_file_counter.txt"))
            else:
                download_actual_location = download_base_location + "\\" + self.__tag
                file_counter_location = os.path.join(settings.TAG_COUNTERS_PATH,
                                                     str(self.__tag + "_file_counter.txt"))
            if not os.path.isfile(file_counter_location) or os.stat(file_counter_location).st_size == 0:
                with open(file_counter_location,'w+') as file:
                    file.write("0")
                    file.close()

            if self.__is_finished_scraping(url_list,file_counter_location):
                print("This program has downloaded all pictures with the specified tag.")
            else:
                try:
                    os.mkdir(download_actual_location, mode=0o777)
                except FileExistsError:
                    pass
                link_pos = 0
                while_run = 0
                while link_pos < len(url_list):
                    while_run += 1
                    if while_run == 1:
                        with open(file_counter_location,'r') as file:
                            content = file.read()
                            link_pos = int(float(content))
                    url = url_list[link_pos]
                    if url is not None:
                        print("Downloading:",url)
                        pic_name = str(id_list[link_pos]) + "." + ext_list[link_pos]
                        full_dir = download_actual_location + "\\" + pic_name
                        req = urllib.request.Request(url,headers = {'User-Agent':
                                                                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                                                                         AppleWebKit/537.36 (KHTML like Gecko) \
                                                                         Chrome/51.0.2704.79 \
                                                                         Safari/537.36 \
                                                                         Edge/14.14931"})
                        content = urllib.request.urlopen(req)
                        with open(full_dir,'wb') as downloaded_pic:
                            downloaded_pic.write(content.read())
                        print("Finished downloading pic #" + str(link_pos + 1))
                    else:
                        print("Pic #" + str(link_pos + 1) + " has no download link")
                    req_open = open(file_counter_location,'w')
                    req_open.write(str(link_pos))
                    req_open.close()

                    link_pos += 1

    def initiate_download(self):
        '''
        Starts the download
        :return:
        '''
        self.__download_pictures()

class DownloadMultipleTags:
    def __init__(self,tag_list):
        self.__tag_list = tag_list

    def __download_individual_tag(self, tag):
        '''
        Download the pictures of each tag
        :param tag: A tag that is listed as a tag in Danbooru
        '''
        DownloadDanbooruPics(tag).initiate_download()

    def __download_all_tags(self):
        '''
        Downloads the pictures in all tags
        '''
        for tag in self.__tag_list:
            self.__download_individual_tag(tag)

    def initiate_download(self):
        '''
        Starts the download
        '''
        self.__download_all_tags()


