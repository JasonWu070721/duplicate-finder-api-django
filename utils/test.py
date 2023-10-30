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
from pathlib import PurePath

IF_GET_CHECKSUM = False
IF_SAVE_CHECKSUM = True
OS_TYPE = "synology"  # synology, windows
IS_CLEAR_FILE_TABLE = True
DELETE_REPEAT_FILE = False

find_dir = "/app/data"
# reserve_path = find_dir + "/" + os.environ['RESERVE_PATH']


class Main:

    db_file = "db/file_info.db"
    log_file = "findIdenticalFiles.log"
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
                file_md5 TEXT, \
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

            file_handler = logging.FileHandler(self.log_file)
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
        md5_value = None
        mfile = open(filename, "rb")
        if mfile.readable():
            m.update(mfile.read())
            mfile.close()
            md5_value = m.hexdigest()
        return md5_value

    def check_file_modification(self, file_path, file_size, file_mtime, file_ctime, file_md5=None):

        if not os.path.isfile(file_path):
            return False

        if IF_GET_CHECKSUM:
            _md5 = self.get_md5(file_path)

            if (file_md5 == _md5):
                return True
        else:
            _file_size = os.path.getsize(file_path)
            _file_mtime = os.path.getmtime(file_path)
            _file_ctime = os.path.getctime(file_path)

            if (file_size == _file_size and file_mtime == _file_mtime and file_ctime == _file_ctime):
                return False

        return True

    def get_file_info(self, file_path, get_md5=False):
        file_md5 = None
        file_status = None
        isFile = os.path.isfile(file_path)
        if isFile:
            if get_md5:
                file_md5 = self.get_md5(file_path)
            file_size = os.path.getsize(file_path)
            file_mtime = os.path.getmtime(file_path)
            file_ctime = os.path.getctime(file_path)
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()

            file_status = {'file_path': file_path, 'file_md5': file_md5, 'file_size': file_size,
                           'file_mtime': file_mtime, 'file_ctime': file_ctime, 'file_extension': file_extension}

        return file_status

    def get_file_list(self, root_path):

        file_list = []

        for root, _, files in walk(os.path.normpath(root_path)):
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
        db_return = None

        with closing(sqlite3.connect(self.db_file)) as cnn:
            cursor = cnn.cursor()

            cursor.execute(
                f'SELECT * FROM files WHERE file_path == "{file_path}"')
            db_return = cursor.fetchall()

        return db_return

    def update_file_status_in_db(self, file_path, file_id):

        file_info = self.get_file_info(file_path, get_md5=IF_SAVE_CHECKSUM)
        if file_info:
            file_size = file_info["file_size"]
            file_mtime = file_info["file_mtime"]
            file_ctime = file_info["file_ctime"]
            file_md5 = file_info["file_md5"]
            updated_at = datetime.datetime.now()

            with closing(sqlite3.connect(self.db_file)) as cnn:
                cursor = cnn.cursor()

                cursor.execute(f"""
                    UPDATE files SET \
                    file_md5 = {file_md5}, \
                    file_size = {file_size},  \
                    file_mtime = {file_mtime},  \
                    file_ctime = {file_ctime},  \
                    updated_at = "{updated_at}"  \
                    WHERE id == {file_id}
                """)
                cnn.commit()

        return

    def save_file_status(self, file_path):

        files_db = self.get_file_db(file_path)
        if len(files_db) > 0:
            file_size = files_db[0][3]
            file_mtime = files_db[0][4]
            file_ctime = files_db[0][5]
            file_db_id = files_db[0][0]
            file_md5 = files_db[0][2]

            file_is_modify = self.check_file_modification(file_path,
                                                          file_size,
                                                          file_mtime,
                                                          file_ctime,
                                                          file_md5)

            if (file_is_modify):
                self.update_file_status_in_db(file_path, file_db_id)

            return

        try:
            file_status = self.get_file_info(
                file_path, get_md5=IF_SAVE_CHECKSUM)
        except Exception as e:
            print("Error, get file info: ", e)

        created_at = datetime.datetime.now()

        insertQuery = """
            INSERT INTO files (
            file_path,
            file_md5,
            file_size,
            file_mtime,
            file_ctime,
            file_extension,
            created_at,
            updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """

        with closing(sqlite3.connect(self.db_file)) as cnn:
            cursor = cnn.cursor()
            cursor.execute(insertQuery, (
                file_path,
                file_status["file_md5"],
                file_status["file_size"],
                file_status["file_mtime"],
                file_status["file_ctime"],
                file_status["file_extension"],
                created_at,
                created_at))
            cnn.commit()

        return

    def get_same_file_group(self):
        db_return = None
        insertQuery = """
            WITH GroupedData AS (
                SELECT
                    id,
                    file_path,
                    file_md5,
                    file_size,
                    file_mtime,
                    file_ctime,
                    file_extension,
                    created_at,
                    updated_at,
                    DENSE_RANK() OVER (ORDER BY file_md5) AS group_id
                FROM files
            )
            SELECT
                group_id,
                id,
                file_path,
                file_md5,
                file_size,
                file_mtime,
                file_ctime,
                file_extension,
                created_at,
                updated_at
            FROM GroupedData
            ORDER BY group_id;
        """

        with closing(sqlite3.connect(self.db_file)) as cnn:

            cursor = cnn.cursor()
            cursor.execute(insertQuery)
            db_return = cursor.fetchall()

        return db_return

    def delete_other_reserve_path_file(self, same_file_record_list, reserve_path):
        for same_file_record in same_file_record_list:
            repeat_file_count = 0
            for file_status in same_file_record:
                file_path = file_status[2]
                file_group_id = file_status[0]

                check_path = PurePath(file_path)
                if (check_path.is_relative_to(reserve_path)):
                    repeat_file_count += 1

                    if DELETE_REPEAT_FILE:
                        if repeat_file_count > 1:
                            print(file_group_id, "delete file(repeat):", file_path)
                            # os.remove(file_path)
                        else:
                            print(file_group_id, "keep file:", file_path)
                    else:
                        print(file_group_id, "keep file:", file_path)
                else:
                    print(file_group_id, "delete file:", file_path)
                    # os.remove(file_path)

    def selete_fils(self, file_list, reserve_path):

        reserve_path = os.path.normpath(reserve_path)
        same_file_record = []
        find_reserve_path = False
        same_file_group_list = []

        for file_status in file_list:

            same_file_record.append(file_status)

            if len(same_file_record) > 1:
                record_group_id_1 = same_file_record[0][0]
                file_group_id = file_status[0]

                if(record_group_id_1 == file_group_id):

                    file_path = file_status[2]
                    check_path = PurePath(file_path)
                    if (check_path.is_relative_to(reserve_path)):
                        find_reserve_path = True

                else:
                    if find_reserve_path:
                        same_file_record.pop()
                        same_file_group_list.append(same_file_record)

                        find_reserve_path = False
                    same_file_record = []
                    same_file_record.append(file_status)

        return same_file_group_list


if __name__ == '__main__':

    if not os.path.exists(find_dir) and not os.path.exists(reserve_path):
        print("Error, path not found")
        exit()

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
        pool.apply_async(main.save_file_status,
                         (file_path,), callback=log_result)

    pool.close()
    pool.join()

    file_md5_list = main.order_file_table("file_md5")
    md5_group = main.get_same_file_group()

    same_file_group_list = main.selete_fils(md5_group, reserve_path)

    main.delete_other_reserve_path_file(
        same_file_group_list, reserve_path)

    exit()
