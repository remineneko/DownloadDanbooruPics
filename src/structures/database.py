import mysql.connector
from constants import DB_HOST, DB_USERNAME, DB_PASSWORD


class EntryExists(Exception):
    pass


class Database:
    def __init__(self, host = DB_HOST, user_name = DB_USERNAME, password = DB_PASSWORD):
        self.access = mysql.connector.connect(
            host = host,
            user = user_name,
            password = password,
            use_unicode = True,
            charset = 'utf8'
        )

        self.dbcursor = self.access.cursor()
        self._create_database()
        self._create_table()

    def _create_database(self):
        self.dbcursor.execute("CREATE DATABASE IF NOT EXISTS Danbooru;")
        self.access.commit()

    def _use_db(self):
        self.dbcursor.execute("USE Danbooru;")
        self.access.commit()

    def _create_table(self):
        self._use_db()
        self.dbcursor.execute("CREATE TABLE IF NOT EXISTS danbooru("
                              "ID INT NOT NULL,"
                              "format VARCHAR(255) NOT NULL,"
                              "URL VARCHAR(255) NOT NULL,"
                              "tags VARCHAR(10000) NOT NULL,"
                              "filesize INT NOT NULL,"
                              "PRIMARY KEY (ID)"
                              ");")
        self.access.commit()

    def add_values(self, tags, p_id, p_format, url, file_size):
        cmd = f"INSERT IGNORE INTO danbooru (ID, format, URL, tags, filesize) VALUES ({p_id}, '{p_format}', '{url}', '{tags}', {file_size});"
        self._use_db()
        self.dbcursor.execute(cmd)
        self.access.commit()

    def all_entries(self):
        self._use_db()
        self.dbcursor.execute("SELECT * FROM danbooru;")
        entries = self.dbcursor.fetchall()
        for entry in entries:
            yield entry

    def all_values_by_tag(self, tag):
        self._use_db()
        self.dbcursor.execute(f"SELECT * FROM danbooru WHERE tags LIKE \"%{tag}%\";")
        entries = self.dbcursor.fetchall()
        return entries

    def get_number_of_pictures(self):
        self._use_db()
        self.dbcursor.execute("SELECT COUNT(*) FROM danbooru;")
        num_tup = self.dbcursor.fetchone()
        return num_tup[0]

    def isEntryExist(self, p_id):
        cmd = f"SELECT EXISTS(SELECT * FROM danbooru WHERE ID = {p_id})"
        self._use_db()
        self.dbcursor.execute(cmd)
        num_res = self.dbcursor.fetchone()
        return num_res[0] == 1

    def get_file_size(self, id_):
        self._use_db()
        self.dbcursor.execute(f"SELECT filesize FROM danbooru WHERE ID = {id_};")
        file_size = self.dbcursor.fetchone()
        return file_size[0]

    def get_number_of_pictures_for_a_tag(self, tag):
        self._use_db()
        self.dbcursor.execute(f"SELECT COUNT(*) FROM danbooru WHERE tags LIKE \"%{tag}%\";")
        num_tup = self.dbcursor.fetchone()
        return num_tup[0]

    def clear_table(self):
        self._use_db()
        self.dbcursor.execute("TRUNCATE danbooru;")
        self.access.commit()
