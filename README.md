# DownloadDanbooruPics

This program can be used to download media files from Danbooru with the help of a local database.

To setup the local database, in this case MySQL, please refer to the following [instruction](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-22-04) (This is for Ubuntu 22.04, but the guide itself can be used for many other operating systems, just choose your desired system).

Setup:

1. Run `pip install -r requirements.txt`.
2. Create an `.env` file, containing the following fields:

```env
DB_HOST=
DB_USERNAME=
DB_PASSWORD=
DANBOORU_USERNAME=
API_KEY=
DEFAULT_FOLDER=
```

3. Run `python3 main.py start`. See the following section for options available.

Usage:

```bash
python3 main.py start --tags-file -tf \
                      --worker-amt -w \
                      --auto-save-to-tags \
                      --ignore-duplicates \
                      --limit \
                      --location \
                      --use-async
```

Explanation:

- `--tag-file` is the file containing tags to be used in the program. Each tag (or combination of tags) should be seperated by each line.

- `--worker-amt` is the amount of workers used for downloading. By default, this is 5, but feel free to use how many that your machine can handle.

- `--auto-save-to-tags` allows the image to be saved in different folders of tags that are also in the downloading session. For instance, if an image `i` has tags `a`, `b`, and `c`, and the session overall contains two tags to be downloaded: `a` and `b`, the image `i`, after downloading, will be copied to both `a` and `b` folders.

- `--ignore-duplicates` ignores the duplicates found in the database while updating the tags.

- `--limit` limits the amount of media files to be downloaded per tag. Currently supported only int values (`-1` for unlimited and others for a specified amount), but supports for floats between 0 and 1 may be added soon (something like 0.4).

- `--location` option should only be used when the desired location for downloading media files is different from the default stated in the .env file.

- `--use-async` enables usage of asynchronicity for the program.
