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


def get_hash_jason(hash_file_path):
    
    root_path = os.getcwd()

    file_size = get_file_size(hash_file_path)

    if os.path.isfile(hash_file_path):
        with open(hash_file_path) as f:
            data = json.load(f)
            
            if (data.get('file_path') is not None) and \
                (len(data.get('md5')) == 32) and \
                (data.get('file_size') is not None) and \
                (data.get('file_mtime') is not None) and \
                (data.get('file_ctime') is not None)  and \
                (data.get('file_extension') is not None):
                # print("json data is true.")
                # print(data)

                return data


# @background
def get_file_status(parameter):

    root_path = os.getcwd()

    if (len(parameter) != 2):
        return {}

    file_path = parameter[0]
    is_sava_hash = parameter[1]

    file_size = get_file_size(file_path)


    if (file_size > 30 * 1048576):
        return {}

    file_mtime = os.path.getmtime(file_path)
    file_ctime = os.path.getctime(file_path)
    _ , file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    if(is_sava_hash):

        hash_file_path = root_path + '/hash_dir/' + file_path + '.hash'

        if os.path.isfile(hash_file_path):
            print(hash_file_path)

            with open(hash_file_path) as f:
                data = json.load(f)
                
                if (data.get('file_path') == file_path) and \
                    (len(data.get('md5')) == 32) and \
                    (data.get('file_size') == file_size) and \
                    (data.get('file_mtime') == file_mtime) and \
                    (data.get('file_ctime') == file_ctime)  and \
                    (data.get('file_extension') == file_extension):
                    print("json data is true.")
                    return {}
        else:
            os.makedirs(os.path.dirname(hash_file_path), exist_ok=True)

    # md5 =  ""
 
    md5 = get_md5(file_path)

    file_status = {'file_path': file_path, 'md5': md5, 'file_size': file_size, 'file_mtime': file_mtime, 'file_ctime': file_ctime, 'file_extension': file_extension}
    
    if(is_sava_hash):
        json_output = json.dumps(file_status, indent = 4, ensure_ascii = False)

        with open(hash_file_path, "w", encoding='utf8') as outfile:
            outfile.write(json_output)


    print(file_status)
    return file_status
    # file_status_list.append(file_status)


def get_all_hash_json(urlList):

    pool_obj = Pool(12)

    file_status_list = pool_obj.map(get_hash_jason, urlList)

    return file_status_list

def get_all_file_status(urlList):

    pool_obj = Pool(12)

    file_status_list = pool_obj.map(get_file_status, urlList)    

    return file_status_list

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
    
def md5_list_to_json_file(md5_list, out_file):
    now = datetime.now()

    dict_output['md5_group_list'] = md5_list

    dict_output['create_time'] = now.strftime("%Y/%m/%d %H:%M:%S")

    json_output = json.dumps(dict_output, indent = 4, ensure_ascii = False)

    # print(json_output)

    with open(out_file, "w", encoding='utf8') as outfile:
        outfile.write(json_output)



if __name__ == '__main__':

    log = logger()
    dict_output = {}

    # paths = [
    #     r'\\192.168.37.218\data\MY_HDD\備份\偉捷PC_Backup1',
    #     r'\\192.168.37.218\data\MY_HDD\備份\偉捷PC_Backup2',
    #     r'\\192.168.37.218\data\MY_HDD\備份\偉捷PC_Backup2-2',
    # ]

    # root_path = '/var/services/homes/jasonwu/Photos'
    # root_path = '/jasonwu/Photos'
    
    hash_json_out = "hash_jason_out.json"

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
    
    urlList = get_urllist(paths)
    print('urlList len: ')
    print(len(urlList))
    # print(urlList)

    file_status_list = get_all_hash_json(urlList)

    if file_status_list:
        md5_list_sorted = sorted(file_status_list,  key = itemgetter('md5'))

    md5_group_list = get_md5_groupby_files(md5_list_sorted)

    md5_list_to_json_file(md5_group_list, hash_json_out)
    
    exit()

    # now = datetime.now()

    # dict_output['file_paths'] = paths
    # dict_output['create_time'] = now.strftime("%Y/%m/%d %H:%M:%S")
    # file_name_time = now.strftime("%Y%m%d%H%M%S")

    # json_output = json.dumps(dict_output, indent = 4, ensure_ascii = False)

    # print(json_output)
      
    # # Writing to sample.json
    # with open("output_md5/md5_dir_path_" + file_name_time + ".json", "w", encoding='utf8') as outfile:
    #     outfile.write(json_output)
        
        
    # get_delete_file_json(hash_json_out)
    
    # exit()

    # md5_list_sorted = sorted(file_status_list,  key = itemgetter('md5'))

    # print('md5_list_sorted len: ')
    # print(len(md5_list_sorted))

    # md5_group_list = get_md5_groupby_files(md5_list_sorted)
    # print('md5_group_list: ')
    # print(md5_group_list)

    # now = datetime.now()

    # dict_output['md5_group_list'] = md5_group_list
    # dict_output['file_paths'] = paths
    # dict_output['create_time'] = now.strftime("%Y/%m/%d %H:%M:%S")

    # json_output = json.dumps(dict_output, indent = 4, ensure_ascii = False)

    # print(json_output)
      
    # # Writing to sample.json
    # with open("json_output.json", "w", encoding='utf8') as outfile:
    #     outfile.write(json_output)

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