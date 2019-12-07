from DanbooruDownloader import start_download, isPath


print('Welcome to Danbooru Downloader!')
print('Please provide a path to the folder you want your pictures to be installed:')
path = input()
verified_path = isPath(path)
start_download(verified_path)

