import asyncio
import click
from click_repl import register_repl

from constants import (
    SITENAME,
    USERNAME,
    API_KEY,
    DEFAULT_DOWNLOAD_PARENT_LOCATION
)

from src.session import DownloadSession
from src.tag_handler import TagHandler, AsyncTagHandler
from src.structures import CustomDanbooru, Database, Tags

def get_tags(tags_file):
    with open(tags_file) as f:
        return [s.strip() for s in f.readlines()]

@click.group()
def main():
    pass

@main.command()
@click.option(
    '--tags-file', 
    '-tf', 
    required=True, 
    help='The file containing different tags to be used in the program.'
)
@click.option(
    '--worker-amt', 
    '-w', 
    default=5, 
    help='The amount of workers needed for the downloading process.'
)
@click.option(
    '--auto-save-to-tags', 
    is_flag=True, 
    default=False, 
    help='Whether to automatically save media files to relevant tags or not.'
)
@click.option(
    '--ignore-duplicates', 
    is_flag=True, 
    default=False, 
    help='Whether to ignore duplicates when updating the contents of the tag.'
)
@click.option(
    '--limit',
    '-l',
    default=-1,
    type=click.INT,
    help='Limits the number of files to download. Defaults to -1, with every file to be downloaded.'
)
@click.option(
    '--location',
    '-loc',
    default=DEFAULT_DOWNLOAD_PARENT_LOCATION,
    help='The folder to download the media files to.'
)
@click.option(
    '--use-async',
    is_flag=True,
    default=False,
    help='Whether to use asynchronicity in the program.'
)
@click.option(
    '--batch-size',
    default=5,
    type=click.INT,
    help='The max size of each batch for asynchronous usage.'
)
def start(
    tags_file, worker_amt, auto_save_to_tags, 
    ignore_duplicates, limit, location, use_async,
    batch_size
):
    tags = get_tags(tags_file)
    new_db_connection = Database()
    new_access = CustomDanbooru(
        site_name=SITENAME,
        username=USERNAME,
        api_key=API_KEY
    )
    all_tags = Tags(
        tag_name=[],
        tag_data=[]
        )
    if use_async:
        print("Using async to update the tags.")
        print(f"Handling {batch_size} tag(s) at once.")
        asyncio.run(_gather_tags(new_access, tags, batch_size, new_db_connection, ignore_duplicates))
    for tag in tags:
        handler = TagHandler(new_access, tag, new_db_connection)
        if not use_async: # no need to update anymore if async has been used.
            handler.update(ignore_duplicates)
        all_tags = Tags.cat([
            all_tags,
            handler.convert_to_tag_object(limit)
        ])
    session = DownloadSession(all_tags, location, worker_amt)
    if auto_save_to_tags:
        print("Auto saving the images to tags in the downloading job.")
    session.download(auto_save_to_tags)

async def _gather_tags(access, tags, batch_size, db, ignore_duplicates):
    work = [asyncio.create_task(AsyncTagHandler(access, tag, db).update(ignore_duplicates)) for tag in tags]
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    if batch_size == -1:
        await asyncio.gather(*work)
    elif batch_size > 0:
        for work_chunk in chunks(work, batch_size):
            await asyncio.gather(*work_chunk)
    else:
        print("Illegal input for batch-size argument. Exiting...")
        exit()

@main.command()
def clear_database():
    new_db_connection = Database()
    new_db_connection.clear_table()
    print("Database cleared.")

if __name__ == "__main__":
    register_repl(main)
    main()