# -*- coding: UTF-8 -*-
import os
import hashlib
import logging
import sys
from os import walk
import json

from datetime import datetime
import sqlite3
import datetime

from contextlib import closing

import os
import multiprocessing

IF_GET_CHECKSUM = False
IF_SAVE_CHECKSUM = True
OS_TYPE = "windows"  # synology, windows
IS_CLEAR_FILE_TABLE = False

class Main:

    db_file = "file_info.db"
    file_amount = 0
    file_count = 0

    def init_db(self):

        with closing(sqlite3.connect(self.db_file)) as cnn:
            cursor = cnn.cursor()

            if IS_CLEAR_FILE_TABLE:
                cursor.execute("DROP TABLE IF EXISTS files")

            cursor.execute("CREATE TABLE IF NOT EXISTS files(\
                id INTEGER PRIMARY KEY AUTOINCREMENT, \
                file_path TEXT, \
                md5 TEXT, \
                file_size FLOAT, \
                file_mtime FLOAT, \
                file_ctime FLOAT, \
                file_extension TEXT, \
                created_at timestamp, \
                updated_at timestamp \
                )")

            cnn.commit()

    def logger(self):

        logger = logging.getLogger()
        if not logger.handlers:

            formatter = logging.Formatter(
                '%(asctime)s %(levelname)-8s: %(message)s')

            file_handler = logging.FileHandler("test.log")
            file_handler.setFormatter(formatter)

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.formatter = formatter

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(logging.INFO)
        return logger

    def is_json(self, myjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True

    def get_md5(self, filename):
        m = hashlib.md5()
        mfile = open(filename, "rb")
        m.update(mfile.read())
        mfile.close()
        md5_value = m.hexdigest()
        return md5_value

    def check_file_modification(self, file_path, file_size, file_mtime, file_ctime, md5=None):

        if IF_GET_CHECKSUM:
            _md5 = self.get_md5(file_path)

            if (md5 == _md5):
                return True
        else:
            _file_size = os.path.getsize(file_path)
            _file_mtime = os.path.getmtime(file_path)
            _file_ctime = os.path.getctime(file_path)

            if (file_size == _file_size and file_mtime == _file_mtime and file_ctime == _file_ctime):
                return False

        return True

    def get_file_info(self, file_path, get_md5=False):
        md5 = None
        if get_md5:
            md5 = self.get_md5(file_path)
        file_size = os.path.getsize(file_path)
        file_mtime = os.path.getmtime(file_path)
        file_ctime = os.path.getctime(file_path)
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        file_status = {'file_path': file_path, 'md5': md5, 'file_size': file_size,
                       'file_mtime': file_mtime, 'file_ctime': file_ctime, 'file_extension': file_extension}

        return file_status

    def get_file_list(self, root_path):

        file_list = []

        for root, dirs, files in walk(os.path.normpath(root_path)):
            if OS_TYPE == "synology" and '@eaDir' in root:
                continue

            for file in files:
                path = os.path.join(root, file)
                path = os.path.normpath(path)

                file_list.append(path)

        return file_list

    def order_file_table(self, column_name):
        with closing(sqlite3.connect(self.db_file)) as cnn:
            cursor = cnn.cursor()
            cursor.execute(f'SELECT * FROM files ORDER BY {column_name} ASC')
            files_db = cursor.fetchall()

        return files_db

    def get_file_db(self, file_path):

        with closing(sqlite3.connect(self.db_file)) as cnn:
            cursor = cnn.cursor()

            cursor.execute(
                f'SELECT * FROM files WHERE file_path == "{file_path}"')
            files_db = cursor.fetchall()

        return files_db

    def update_file_status_in_db(self, file_path, file_id):
        

        file_info = self.get_file_info(file_path, get_md5=IF_SAVE_CHECKSUM)

        file_size = file_info["file_size"]
        file_mtime = file_info["file_mtime"]
        file_ctime = file_info["file_ctime"]
        md5 = file_info["md5"]
        updated_at = datetime.datetime.now()

        with closing(sqlite3.connect(self.db_file)) as cnn:
            cursor = cnn.cursor()
            
            cursor.execute(f'UPDATE files SET \
                md5 = {md5}, \
                file_size = {file_size},  \
                file_mtime = {file_mtime},  \
                file_ctime = {file_ctime},  \
                updated_at = "{updated_at}"  \
                WHERE id == {file_id}')
            cnn.commit()

        return

    def save_file_status(self, file_path):
        

        files_db = main.get_file_db(file_path)
        if len(files_db) > 0:
            file_size = files_db[0][3]
            file_mtime = files_db[0][4]
            file_ctime = files_db[0][5]
            file_db_id = files_db[0][0]     
            md5 = files_db[0][2]

            file_is_modify = main.check_file_modification(file_path,
                                                          file_size,
                                                          file_mtime,
                                                          file_ctime,
                                                          md5)

            if (file_is_modify):
                main.update_file_status_in_db(file_path, file_db_id)

            return

        file_status = main.get_file_info(file_path, get_md5=IF_SAVE_CHECKSUM)

        created_at = datetime.datetime.now()
        
        insertQuery = """INSERT INTO files (
            file_path,
            md5,
            file_size,
            file_mtime,
            file_ctime,
            file_extension,
            created_at,
            updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""

        with closing(sqlite3.connect(self.db_file)) as cnn:
            cursor = cnn.cursor()
            cursor.execute(insertQuery, (
                file_path,
                file_status["md5"],
                file_status["file_size"],
                file_status["file_mtime"],
                file_status["file_ctime"],
                file_status["file_extension"],
                created_at,
                created_at))
            cnn.commit()


if __name__ == '__main__':

    find_dir = "/home/jason/side_project/car_repair_web_react"

    main = Main()

    main.init_db()

    log = main.logger()
    file_list = main.get_file_list(find_dir)

    main.file_amount = len(file_list)

    cpu_cores = multiprocessing.cpu_count()

    pool = multiprocessing.Pool(cpu_cores)

    result_list = []
    def log_result(result):
        main.file_count = main.file_count + 1
        print("Progress bar: ", main.file_count, " / ", main.file_amount)
        result_list.append(result)

    for file_path in file_list:
        pool.apply_async(main.save_file_status, (file_path,), callback = log_result)

    pool.close()
    pool.join()
