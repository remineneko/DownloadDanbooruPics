# DownloadDanbooruPics
A program aims to download pictures from Danbooru - a NSFW site where fan arts of animated characters/game characters are posted.
This program uses Pybooru as main site access using Python.

Change log:
* Version 0.1.0: 
  - Changes in downloading pictures: Users now can put custom path to desired location where the pictures will be downloaded. 
    The syntax to download now is:
      DownloadDanbooruPics(tag,"path\\to\\desired\\location").initiate_download()
      DownloadMultipleTags([tags],"path\\to\\desired\\location").initiate_download()
  - Adds FalseTag error when a specified tag does not exist in Danbooru
  - The data obtained for a tag can now be automatically be updated when either DownloadMultipleTags or DownloadDanbooruPics is called/recalled with the same tag.

* First version:
  - class DownloadDanbooruPics(tag)
      initate_download(): 
      ''' Starts the download '''
    
  - class DownloadMultipleTags(list_of_tags)
      initiate_download():
      ''' Starts the download '''
  
  - To download pictures, use DownloadMultipleTags if there are one or more tags needed to be downloaded - with argument being a list of tags, and DownloadDanbooruPics if there is only one tag needed to be downloaded,  and use the initiate_download() function.
For instance, 
      + DownloadMultipleTags(['mash_kyrielight','touhou']).initiate_download()
      + DownloadDanbooruPics('mash_kyrielight').initiate_download()

This program supports resumability. That is, if the program is on idle from being continuosly disconnected from the internet, rerunning the program with the same tag and path will not reset the current downloading/loading status.
For instance, if you are downloading the 789th picture out of 3000 found pictures for a tag, and you need to rerun the program, the program will continue downloading from the specified picture if you use the same tag again.


Future update: Add profiles for users, i.e., users' fixed tags that they want to check.
