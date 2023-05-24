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
OS_TYPE = "windows" # synology, windows

con = sqlite3.connect("file_info.db")
cur = con.cursor()

# cur.execute("DROP TABLE IF EXISTS files")

cur.execute("CREATE TABLE IF NOT EXISTS files(\
    id INTEGER PRIMARY KEY AUTOINCREMENT, \
    file_path TEXT, \
    md5, file_size TEXT, \
    file_mtime TEXT, \
    file_ctime TEXT, \
    file_extension TEXT, \
    created_at timestamp, \
    updated_at timestamp \
    )")
class Main:

    def logger(self):
        """ 獲取logger"""
        logger = logging.getLogger()
        if not logger.handlers:
            # 指定logger輸出格式
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)-8s: %(message)s')
            # 檔案日誌
            file_handler = logging.FileHandler("test.log")
            file_handler.setFormatter(formatter)  # 可以通過setFormatter指定輸出格式
            # 控制檯日誌
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.formatter = formatter  # 也可以直接給formatter賦值
            # 為logger新增的日誌處理器
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            # 指定日誌的最低輸出級別，預設為WARN級別
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

    def get_file_info(self, file_path):
        md5 = None
        if IF_GET_CHECKSUM:
            md5 = self.get_md5(file_path)
        file_size = os.path.getsize(file_path)
        file_tmtime = os.path.getmtime(file_path)
        file_mtime = os.path.getmtime(file_path)
        file_ctime = os.path.getctime(file_path)
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        # file_path = os.path.normpath(file_path)

        file_status = {'file_path': file_path, 'md5': md5, 'file_size': file_size,
                       'file_mtime': file_mtime, 'file_ctime': file_ctime, 'file_extension': file_extension}

        # print(file_status)
        return file_status
        # file_status_list.append(file_status)

    def get_file_list(self, root_path):

        file_list = []

        for root, dirs, files in walk(os.path.normpath(root_path)):
            if OS_TYPE == "synology" and '@eaDir' in root:
                continue

            for file in files:
                path = os.path.join(root, file)
                path = os.path.normpath(path)
                # print(path)
                file_list.append(path)
        # print(file_list)

        return file_list

    def sort(self):
        print("sort")

    def find_file_exist_in_db(self, file_path):
    
        cur.execute(f'SELECT * FROM files WHERE file_path == "{file_path}"')
        files_db = cur.fetchall()
        con.commit()
        
        return files_db

if __name__ == '__main__':

    main = Main()
    
    find_dir = "/home/jason/side_project/car_repair_web_react"

    log = main.logger()
    file_list = main.get_file_list(find_dir)
    
    file_count = 0

    for file_path in file_list:
        
        files_db = main.find_file_exist_in_db(file_path)
        # print(files_db)
        print(len(files_db))
        
        if len(files_db) > 0:
            continue
        
        # file_path = file_status["file_path"]
        # print(file)
        file_status = main.get_file_info(file_path)
        
        file_count = file_count + 1
        # print(datetime.datetime.now())
        
        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()
        
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
            updated_at))
        con.commit()

    main.sort()
