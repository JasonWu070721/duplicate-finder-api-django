# -*- coding: UTF-8 -*-
import os
import hashlib
import logging
import sys
from os import walk
import json
from operator import itemgetter
from itertools import groupby
from smb.SMBConnection import SMBConnection
# from PyQt5 import QtWidgets
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
from multiprocessing import Pool
import asyncio
import time
from datetime import datetime

file_status_list = []

# def background(f):
#     def wrapped(*args, **kwargs):
#         return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

#     return wrapped

def logger(): 
    """ 獲取logger""" 
    logger = logging.getLogger()
    if not logger.handlers: 
        # 指定logger輸出格式
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
        # 檔案日誌 
        file_handler = logging.FileHandler("test.log")
        file_handler.setFormatter(formatter) # 可以通過setFormatter指定輸出格式 
        # 控制檯日誌 
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formatter # 也可以直接給formatter賦值 
        # 為logger新增的日誌處理器 
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        # 指定日誌的最低輸出級別，預設為WARN級別 
        logger.setLevel(logging.INFO)
    return logger 

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

def get_md5(filename):

    m = hashlib.md5()
    mfile = open(filename, "rb")
    m.update(mfile.read())
    mfile.close()
    md5_value = m.hexdigest()
    # print("md5: ", md5_value)
    return md5_value

def get_file_size(file_name):
    return os.path.getsize(file_name)

def get_urllist(file_paths):

    base = (file_paths)

    urlList=[]

    file_count = 0

    for file_path in file_paths:
        for root, dirs, files in walk(os.path.normpath(file_path)):
            # print("目錄：", dirs)
            if files:
                for file in files:
                    # print("路徑：", root)
                    
                    # print("檔案：", files)
                    # print(os.path.join(root, file))
                    if '@eaDir' not in root:
                        url = os.path.join(root, file)

                        if os.path.isfile(url):
                            # print(url)
                            urlList.append(url)
                            file_count = file_count + 1

    print("File count: ", file_count)

    return urlList


def get_delete_file_json(hash_json_path, search_path):
    delete_file_status_array = []

    if os.path.isfile(hash_json_path):
        with open(hash_json_path) as f:
            data = json.load(f)

            if data.get('md5_group_list') is not None:
                md5_group_list = data['md5_group_list']

                for md5_group in md5_group_list:
                    # print(md5_group)

                    find_status_list = md5_group_list.get(md5_group)

                    if find_status_list is not None and len(find_status_list) > 1:

                        find_status_filter = find_status_list.copy()
                        # print(find_status_filter)
                        reserve_file_path = None
                        reserve_find_status_idx = None
                        reserve_find_status_count = 0
                        filter_idx_array = []

                        # for find_status in find_status_list:
                        for find_status_idx, find_status in enumerate(find_status_filter):
                           

                            file_path = find_status['file_path']
                            if(search_path not in file_path):
                                # print(find_status)
                                delete_file_status_array.append(find_status)
                            

    for find_status_idx, find_status in enumerate(delete_file_status_array):

        file_path = find_status['file_path']
        # print(file_path)
        if(search_path in file_path):
            print("delete_file_status_array")
            print(find_status_idx)
            print(find_status)
    
    json_output = json.dumps(delete_file_status_array, indent = 4, ensure_ascii = False)
    return json_output


if __name__ == '__main__':

    log = logger()

    hash_json_path = "hash_jason_out.json"

    root_path = '/var/services/homes/jasonwu/Drive/side_project/duplicate_file/hash_dir'

    paths = [
        # r'\\192.168.37.218\data\MY_HDD\備份\佳華家裡電腦\佳華家電桌面20150920',
        # r'/volume1/data/MY_HDD/備份/佳華家裡電腦/佳華家電桌面20150920',
        # r'/volume1/homes/jasonwu/Photos/生活照片/施郁婷資料庫.照片',
        # f'{root_path}/生活照片',
        # root_path + '/MobileBackup',
        # root_path + '/PhotoLibrary',
        # root_path + '/takeout',
        root_path,
        # r'/jasonwu/photos/takeout',
        # r'/jasonwu/photos/PhotoLibrary',
        # r'\\192.168.37.218\homes\jasonwu\Photos\生活照片'
    ]
    
    
    search_file_path = '/var/services/homes/jasonwu/Photos/takeout'
    delete_file_json_file = 'delete_file_jason_out.json'
    
    delete_file_list_json = get_delete_file_json(hash_json_path, search_file_path)
   
    with open(delete_file_json_file, "w", encoding='utf8') as outfile:
        outfile.write(delete_file_list_json)
   
    exit()

