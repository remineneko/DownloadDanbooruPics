from DanbooruDownloader.MainDownloadWizard import *


print('Welcome to Danbooru Downloader!')
print('Please provide a path to the folder you want your pictures to be installed:')
path = input()
verified_path = isPath(path)
user_input = question()
start_download(user_input, verified_path)

