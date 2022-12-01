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
            if files:
                for file in files:
                    # print("路徑：", root)
                    # print("目錄：", dirs)
                    # print("檔案：", files)
                    # print(os.path.join(root, file))
                    url = os.path.join(root, file)

                    if os.path.isfile(url):
                        print(url)
                        urlList.append(url)
                        file_count = file_count + 1

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
    print(Lines)

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


def get_all_file_status(file_paths):

    pool_obj = Pool(12)

    # file_status_list = []
    urlList = get_urllist(file_paths)
    # print(urlList)

    file_status_list = pool_obj.map(get_file_status, urlList)

    # for idx, filepath in enumerate(urlList):

    #     if os.path.isfile(filepath):
  

    #         file_status = get_file_status(filepath)
    #         print(file_status)

    #         # file_status_list.append(file_status)

    #     else:
    #         print(f"(Error): {filepath}")
    print(file_status_list)

    md5_list_sorted = sorted(file_status_list,  key = itemgetter('md5'))

    return md5_list_sorted

def get_groupby_files(file_paths):

    md5_list_sorted = get_all_file_status(file_paths)

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


if __name__ == '__main__':

    log = logger()
    # dict_output = {}

    # # paths = [
    # #     r'\\192.168.37.218\data\MY_HDD\備份\偉捷PC_Backup1',
    # #     r'\\192.168.37.218\data\MY_HDD\備份\偉捷PC_Backup2',
    # #     r'\\192.168.37.218\data\MY_HDD\備份\偉捷PC_Backup2-2',
    # # ]

    # paths = [
    #     # r'\\192.168.37.218\data\MY_HDD\備份\佳華家裡電腦\佳華家電桌面20150920',
    #     # r'/volume1/data/MY_HDD/備份/佳華家裡電腦/佳華家電桌面20150920',
    #     r'/volume1/homes/jasonwu/Photos/生活照片',
        
    #     #r'\\192.168.37.218\homes\jasonwu\Photos\生活照片'
    # ]


    # md5_group_list = get_groupby_files(paths)
    # print(md5_group_list)

    # now = datetime.now()

    # dict_output['md5_group_list'] = md5_group_list
    # dict_output['file_paths'] = paths
    # dict_output['create_time'] = now.strftime("%Y/%m/%d %H:%M:%S")

    # json_output = json.dumps(dict_output, indent = 4, ensure_ascii = False)


    # print(json_output)
      
    # Writing to sample.json
    with open("json_output.json", encoding='utf8') as json_file:
        # outfile.write(json_output)
        data = json.load(json_file)
        print(len(data["md5_group_list"]))
        for md5_group_list in data["md5_group_list"]:
            print(md5_group_list)
            for file_data in data["md5_group_list"][md5_group_list]:
                file_path = file_data["file_path"]
                if os.path.isfile(file_path):
                    print(file_path)

    # with open('output.json', 'w', encoding='utf-8') as f:
    #     try:
    #         json.dump(json_output, f, ensure_ascii=False, indent=4)

    #     except ValueError as e:
    #         print(e)
    # for md5 in md5_list_sorted:
    #     # print(md5List[md5]['file_path'])
    #     print(md5List[md5])

        # if (md5 in md5List): 
        #     os.remove(a) 
        #     print("重複：%s"%a) 
        #     log.info("重複：%s"%a) 
        # else: 
        #     md5List.append(md5) 
        #     # print(md5List) 
        #     print("一共%s張照片"%len(md5List)) 