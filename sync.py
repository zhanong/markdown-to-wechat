#!/usr/bin/env python
##public/upload_news.py
# -*- coding: utf-8 -*-
"""
hello baby
推送文章到微信公众号
"""
from calendar import c
from datetime import datetime
from datetime import timedelta
from weakref import ref
from pyquery import PyQuery
from datetime import date, timedelta
import time
import html
import urllib
import markdown
from markdown.extensions import codehilite
import os
import hashlib
import pickle
from pathlib import Path
from werobot import WeRoBot
import requests
import json
import urllib.request
import random
import string

from source_getter import local as sg
from content_formatter import blogdigest_formatter as cf

CACHE = {}

CACHE_STORE = "cache.bin"
FILE_FOLDER_PATH = "/home/n8n/file_rw/blogdigest/markdown"
# TIME_STAMP = datetime.today().strftime("%Y-%m-%d")
# MD_PATH = FILE_FOLDER_PATH + "/" + TIME_STAMP + ".md"

COVER_IMAGE_DIR = "/home/processing-exp/"

CURRNT_MD_NAME = ""

try:
    SOURCE = sg.initialize()
    print("Got file sources")
except Exception as e:
    print(f"Failed to get source: {e}")
    exit(1)

def dump_cache():
    fp = open(CACHE_STORE, "wb")
    pickle.dump(CACHE, fp)

def init_cache():
    global CACHE
    if os.path.exists(CACHE_STORE):
        fp = open(CACHE_STORE, "rb")
        CACHE = pickle.load(fp)
        #print(CACHE)
        return
    dump_cache()


class NewClient:

    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0

    def __real_get_access_token(self):
        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (os.getenv('WECHAT_APP_ID'), os.getenv('WECHAT_APP_SECRET')))
        urlResp = urllib.request.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        self.__accessToken = urlResp['access_token']
        self.__leftTime = urlResp['expires_in']

    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
        return self.__accessToken

def Client():
    robot = WeRoBot()
    robot.config["APP_ID"] = os.getenv('WECHAT_APP_ID')
    robot.config["APP_SECRET"] = os.getenv('WECHAT_APP_SECRET')
    client = robot.client
    token = client.grant_token()
    return client, token

def cache_get(key):
    if key in CACHE:
        return CACHE[key]
    return None


def file_digest(file_path, is_local):
    """
    计算文件的md5值
    """
    md5 = hashlib.md5()
    if not is_local:
        try:
            # Get object in streaming mode
            result = SOURCE.read_object_content(file_path, encoding = '')
            md5.update(result)
        except Exception as e:
            print(f"Error calculating digest for OSS object {file_path}: {e}")
            return None
    else:
        with open(file_path, 'rb') as f:
            md5.update(f.read())

    return md5.hexdigest()

def cache_update(file_path, is_local):
    digest = file_digest(file_path, is_local)
    CACHE[digest] = "{}:{}".format(file_path, datetime.now())
    dump_cache()

def file_processed(file_path, is_local):
    digest = file_digest(file_path, is_local)
    return cache_get(digest) != None

def upload_image_from_path(image_path):
    image_digest = file_digest(image_path, True)
    res = cache_get(image_digest)
    if res != None:
        return res[0], res[1]
    client, _ = Client()
    print("uploading image {}".format(image_path))
    try:
        media_json = client.upload_permanent_media("image", open(image_path, "rb")) ##永久素材
        media_id = media_json['media_id']
        media_url = media_json['url']
        CACHE[image_digest] = [media_id, media_url]
        dump_cache()
        print("file: {} => media_id: {}".format(image_path, media_id))
        return media_id, media_url
    except Exception as e:
        print("upload image error: {}".format(e))
        return None, None

def upload_image(img_url):
    """
    * 上传临时素材
    * 1、临时素材media_id是可复用的。
    * 2、媒体文件在微信后台保存时间为3天，即3天后media_id失效。
    * 3、上传临时素材的格式、大小限制与公众平台官网一致。
    """
    resource = urllib.request.urlopen(img_url)
    name = img_url.split("/")[-1]
    f_name = "/tmp/{}".format(name)
    if "." not in f_name:
        f_name = f_name + ".png"
    with open(f_name, 'wb') as f:
        f.write(resource.read())
    return upload_image_from_path(f_name)

def get_images_from_markdown(content):
    lines = content.split('\n')
    images = []
    for line in lines:
        line = line.strip()
        if line.startswith('![') and line.endswith(')'):
            image = line.split('(')[1].split(')')[0].strip()
            images.append(image)
    return images

def fetch_attr(content, key):
    """
    从markdown文件中提取属性
    """
    lines = content.split('\n')
    for line in lines:
        if line.startswith(key):
            return line.split(':')[1].strip()
    return ""

def render_markdown(content):
    exts = ['markdown.extensions.extra',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.sane_lists',
            codehilite.makeExtension(
                guess_lang=False,
                noclasses=True,
                pygments_style='monokai'
            ),]
    post =  "".join(content.split("---")[2:])
    html = markdown.markdown(post, extensions=exts)
    open("/home/repo/markdown-to-wechat/origi.html", "w").write(html)
    return cf.beautify(html, CURRENT_MD_NAME)

def update_images_urls(content, uploaded_images):
    for image, meta in uploaded_images.items():
        orig = "({})".format(image)
        new = "({})".format(meta[1])
        print("{} -> {}".format(orig, new))
        content = content.replace(orig, new)
    return content

def upload_media_news(object_key):
    """
    上传到微信公众号素材
    """
    content = SOURCE.read_object_content(object_key)
    TITLE = fetch_attr(content, 'title').strip('"').strip('\'')
    images = get_images_from_markdown(content)
    print(TITLE)

    '''
    if len(images) == 0 or gen_cover == "true" :
        letters = string.ascii_lowercase
        seed = ''.join(random.choice(letters) for i in range(10))
        print(seed)
        images = ["https://picsum.photos/seed/" + seed + "/400/600"] + images
    '''
    images = [COVER_IMAGE_DIR + CURRENT_MD_NAME + ".png"] + images

    uploaded_images = {}
    for image in images:
        media_id = ''
        media_url = ''
        if image.startswith("http"):
            media_id, media_url = upload_image(image)
        else:
            media_id, media_url = upload_image_from_path(image)
        if media_id != None:
            uploaded_images[image] = [media_id, media_url]

    content = update_images_urls(content, uploaded_images)

    THUMB_MEDIA_ID = (len(images) > 0 and uploaded_images[images[0]][0]) or ''
    RESULT = render_markdown(content)
    digest = fetch_attr(content, 'subtitle').strip().strip('"').strip('\'')
    CONTENT_SOURCE_URL = ''

    articles = {
        'articles':
        [
            {
                "title": TITLE,
                "thumb_media_id": THUMB_MEDIA_ID,
                "digest": digest,
                "show_cover_pic": 1,
                "content": RESULT,
                "content_source_url": CONTENT_SOURCE_URL
            }
            # 若新增的是多图文素材，则此处应有几段articles结构，最多8段
        ]
    }

    fp = open('./result.html', 'w')
    fp.write(RESULT)
    fp.close()

    client = NewClient()
    token = client.get_access_token()
    headers={'Content-type': 'text/plain; charset=utf-8'}
    datas = json.dumps(articles, ensure_ascii=False).encode('utf-8')

    postUrl = "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=%s" % token
    r = requests.post(postUrl, data=datas, headers=headers)
    resp = json.loads(r.text)
    print(resp)
    media_id = resp['media_id']
    cache_update(object_key, False)
    return resp

def run(string_date, file_folder_path):
    #string_date = "2023-03-13"
    
    print(string_date)
    for obj in SOURCE.iterate_object_at(file_folder_path):
        object_key = obj.key
        if not object_key.lower().endswith('.md'): continue
        print(f"Processing object: {object_key}")
        global CURRENT_MD_NAME
        CURRENT_MD_NAME  = Path(object_key).stem
        
        content = SOURCE.read_object_content(object_key)
        if content is None:
            print(f"Skipping {object_key} due to read error.")
            continue
        date_attr = fetch_attr(content, 'date').strip()
        if string_date in date_attr:
            if file_processed(object_key, False):
                print("{} has been processed".format(object_key))
                continue
            print(object_key)
            news_json = upload_media_news(object_key)
            print(news_json)
            print('successful')

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


if __name__ == '__main__':
    print("begin sync to wechat")
    init_cache()
        
    start_time = time.time() # 开始时间
    for x in daterange(datetime.now() - timedelta(days=7), datetime.now() + timedelta(days=2)):
        print("start time: {}".format(x.strftime("%m/%d/%Y, %H:%M:%S")))
        string_date = x.strftime('%Y-%m-%d')
        print(string_date)
        run(string_date, FILE_FOLDER_PATH)
    end_time = time.time() #结束时间
    print("程序耗时%f秒." % (end_time - start_time))
