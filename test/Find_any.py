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
import shutil

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


def find_empty_dir(file_paths):

    urlList=[]

    file_count = 0

    for file_path in file_paths:
        for root, dirs, files in walk(os.path.normpath(file_path)):
        	if '@eaDir' not in root:
        		if(len(files) == 0 and len(dirs) == 0):
        			url = os.path.join(root)
        			if os.path.isdir(url):
        				urlList.append(url)
        				file_count = file_count + 1
	        
            # if files:
            #     for file in files:
            #         # print("路徑：", root)
                    
            #         # print("檔案：", files)
            #         # print(os.path.join(root, file))
            #         if '@eaDir' not in root:
            #             url = os.path.join(root, file)

            #             if os.path.isfile(url):
            #                 print(url)
            #                 urlList.append(url)
            #                 file_count = file_count + 1

    return urlList
    
def get_urllist(file_paths):

    base = (file_paths)

    urlList=[]

    file_count = 0

    for file_path in file_paths:
        for root, dirs, files in walk(os.path.normpath(file_path)):
        	if '@eaDir' not in root:
	        	if(len(files) == 0 and len(dirs) == 0):
	        		urlList.append(root)
	        
            # if files:
            #     for file in files:
            #         # print("路徑：", root)
                    
            #         # print("檔案：", files)
            #         # print(os.path.join(root, file))
            #         if '@eaDir' not in root:
            #             url = os.path.join(root, file)

            #             if os.path.isfile(url):
            #                 print(url)
            #                 urlList.append(url)
            #                 file_count = file_count + 1

    print("File count: ", file_count)

    return urlList

def loging_samba():

    host = "192.168.16.3"  #ip或域名
    username = "jason_wu@aai.com.tw"
    password = "123456"
    conn = SMBConnection(username,password, "", "", use_ntlm_v2=True,  is_direct_tcp=True)
    assert conn.connect(host, 445)
    # print("samba: ", result)


    shares = conn.listShares()
    # print(shares)

    # for share in shares:
    #     # print(share.name)
    #     # print(share.isSpecial)
    #     if share.name == '二廠NAS':
    #         print(share.isSpecial)
    #         if not share.isSpecial and share.name not in ['NETLOGON', 'SYSVOL']:
    #             sharedfiles = conn.listPath(share.name, '/')
    #             for sharedfile in sharedfiles:
    #                 print(sharedfile.filename)

    localFile = open(r"\\192.168.16.3\二廠nas\Jason_Wu\新文字文件.txt","r") 

    Lines = localFile.readlines()
    # print(Lines)

    conn.close()

# @background
def get_file_status(file_path):
    md5 = get_md5(file_path)
    # md5 =  ""
    file_size = get_file_size(file_path)
    file_tmtime = os.path.getmtime(file_path)
    file_mtime = os.path.getmtime(file_path)
    file_ctime = os.path.getctime(file_path)
    _ , file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    file_status = {'file_path': file_path, 'md5': md5, 'file_size': file_size, 'file_mtime': file_mtime, 'file_ctime': file_ctime, 'file_extension': file_extension}

    return file_status
    # file_status_list.append(file_status)


def get_all_file_status(urlList):

    pool_obj = Pool(5)

    # file_status_list = []
    # print(urlList)

    file_status_list = pool_obj.map(get_file_status, urlList)

    # for idx, filepath in enumerate(urlList):

    #     if os.path.isfile(filepath):
  

    #         file_status = get_file_status(filepath)
    #         print(file_status)

    #         # file_status_list.append(file_status)

    #     else:
    #         print(f"(Error): {filepath}")
    # print(file_status_list)

    md5_list_sorted = sorted(file_status_list,  key = itemgetter('md5'))

    return md5_list_sorted

def get_md5_groupby_files(md5_list_sorted):

    json_output = {}

    for key, values in groupby(md5_list_sorted, key = itemgetter('md5')):

        group_count = 0
        first_value = {}
        same_file_array = []
        for value in values:

            if group_count > 0:
               
                if group_count == 1:
                    same_file_array.append(first_value)

                same_file_array.append(value)
                # print(value['file_size'])
                
            else:
                first_value = value

            group_count = group_count + 1

        if group_count > 1:
            json_output[key] = same_file_array
    

    return json_output


def move_dir_list_to_destination(dir_list, destination):
	for dolder in dir_list:
		if os.path.isdir(dolder):
			move_path = destination + "/" + dolder
			shutil.move(dolder, move_path)


def search_file_path_in_dict(dicts, path):
    for item in dicts:
        if path in item["file_path"]:
            return path
    return None

if __name__ == '__main__':

    log = logger()

    hash_file_path = '/var/services/homes/jasonwu/Drive/side_project/duplicate_file/hash_jason_out.json'
    delete_file_status_array = []

    if os.path.isfile(hash_file_path):
        with open(hash_file_path) as f:
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
                            if('/var/services/homes/jasonwu/Photos/takeout' not in file_path):
                                # print(find_status)
                                delete_file_status_array.append(find_status)


                                # print(file_path)
                                
                                # find_status_filter.pop()
                                # print(find_status)
                                
                                # filter_idx_array.remove(find_status)
                                
                                # print(find_status_idx)
                                # print(find_status)
                                # print(find_status_filter[find_status_idx])
                                # print(find_status)
                                # reserve_file_path = file_path
                                # reserve_find_status_idx = find_status_idx
                               
                                # reserve_find_status_count = reserve_find_status_count + 1
                                
                        # print(filter_idx_array)
                        
                        # for filter_idx in filter_idx_array:
                        #     find_status_filter.pop(filter_idx)
                            
                        

                        # if reserve_file_path and reserve_find_status_idx:
                        #     find_status_list.pop(reserve_find_status_idx)
                        #     print(reserve_find_status_count)
                            

    for find_status_idx, find_status in enumerate(delete_file_status_array):
       

        file_path = find_status['file_path']
        print(file_path)
        if('/var/services/homes/jasonwu/Photos/takeout' in file_path):
            print("delete_file_status_array")
            print(find_status_idx)
            print(find_status)



                            # print(find_status_list['md5'])
                            # print(find_status_list['file_size'])

                        # if(search_file_path_in_dict(find_status_list, '/var/services/homes/jasonwu/Photos/takeout')):

                        #     for file_status in find_status_list:
                        #         print(file_status['file_path'])
                        #         print(file_status['md5'])
                        #         print(file_status['file_size'])



        

      