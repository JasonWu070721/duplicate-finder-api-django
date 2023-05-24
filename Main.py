# -*- coding: UTF-8 -*-
import os
import hashlib
import logging
import sys
from os import walk
import json
from operator import itemgetter
from itertools import groupby

from multiprocessing import Pool
import asyncio
import time
from datetime import datetime
import sqlite3
import datetime

import os

IF_GET_CHECKSUM = False
OS_TYPE = "windows"  # synology, windows
IS_CLEAR_FILE_TABLE = False

con = sqlite3.connect("file_info.db")
cur = con.cursor()

if IS_CLEAR_FILE_TABLE:
    cur.execute("DROP TABLE IF EXISTS files")

cur.execute("CREATE TABLE IF NOT EXISTS files(\
    id INTEGER PRIMARY KEY AUTOINCREMENT, \
    file_path TEXT, \
    md5, file_size TEXT, \
    file_mtime FLOAT, \
    file_ctime FLOAT, \
    file_extension TEXT, \
    created_at timestamp, \
    updated_at timestamp \
    )")


class Main:

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

    def check_file_modification(self, file_path, file_size, file_mtime):
        _file_size = os.path.getsize(file_path)
        _file_mtime = os.path.getmtime(file_path)

        if (file_size == _file_size and file_mtime == _file_mtime):
            return True

        return False

    def get_file_info(self, file_path):
        md5 = None
        if IF_GET_CHECKSUM:
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

    def sort(self):
        print("sort")

    def get_file_db(self, file_path):

        cur.execute(f'SELECT * FROM files WHERE file_path == "{file_path}"')
        files_db = cur.fetchall()
        con.commit()

        return files_db

    def update_file_status_in_db(self, file_path, file_id):

        file_info = self.get_file_info(file_path)

        file_size = file_info["file_size"]
        file_mtime = file_info["file_mtime"]
        file_ctime = file_info["file_ctime"]
        updated_at = datetime.datetime.now()

        cur.execute(f'UPDATE files SET \
            file_size = {file_size},  \
            file_mtime = {file_mtime},  \
            file_ctime = {file_ctime},  \
            updated_at = "{updated_at}"  \
            WHERE id == {file_id}')

        con.commit()
        return files_db


if __name__ == '__main__':

    main = Main()

    find_dir = "/home/jason/side_project/car_repair_web_react"

    log = main.logger()
    file_list = main.get_file_list(find_dir)

    file_count = 0

    file_amount = len(file_list)

    for file_path in file_list:
        file_count = file_count + 1
        print("Progress bar: ", file_count, " / ", file_amount)

        files_db = main.get_file_db(file_path)
        if len(files_db) > 0:
            file_size = files_db[0][3]
            file_mtime = files_db[0][4]
            file_db_id = files_db[0][0]

            file_is_modify = main.check_file_modification(file_path,
                                                          file_size,
                                                          file_mtime)

            if (file_is_modify):
                main.update_file_status_in_db(file_path, file_db_id)

            continue

        file_status = main.get_file_info(file_path)

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

        cur.execute(insertQuery, (
            file_path,
            file_status["md5"],
            file_status["file_size"],
            file_status["file_mtime"],
            file_status["file_ctime"],
            file_status["file_extension"],
            created_at,
            created_at))

        con.commit()

    main.sort()
