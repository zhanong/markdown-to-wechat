import re
import json
from datetime import datetime

# get color scheme
FILE_FOLDER_PATH = "/home/n8n/file_rw/blogdigest/colorScheme/"

COLORSCHEME = None


def load_color_scheme(timeStamp):
    print ("loading color scheme from " + FILE_FOLDER_PATH + timeStamp + ".json")
    try:
        with open(FILE_FOLDER_PATH + timeStamp + ".json", 'r', encoding='utf-8') as f:
            global COLORSCHEME
            COLORSCHEME = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        raise
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file at {filepath}")
        raise


def gen_css(path, *args):
    tmpl = open("./assets/{}.tmpl".format(path), "r").read()
    return tmpl.format(*args)

def replace_preface(content):
    res = []
    source_id = 0
    for line in content.split("\n"):
        if line.startswith("<h3"):
            tag = '<p style="text-align:center; font-size: 12px; font-weight: 200;  color:black; margin: 0px; ">'
            pattern = r"<h3.*?>"
            line = re.sub(pattern, tag, line, count=1)
            line = line.replace("</h3>", "</p><br>")
            source_id += 1
        res.append(line)
    return "\n".join(res)

def replace_image(content):
    res = []
    for line in content.split("\n"):
        if line.startswith("<p><img"):
            tag = '<p style = "text-align:center"><img'
            line = line.replace("<p><img", tag)
        res.append(line)
    return "\n".join(res)

def replace_source(content):
    res = []
    source_id = 0
    for line in content.split("\n"):
        if line.startswith("<h1"):
            color = COLORSCHEME[source_id]['sourceColor']
            tag = '<header style="text-align:center; font-size:0.85rem; font-weight:bold; letter-spacing: 2px; color:{};">'.format(color)
            pattern = r"<h1.*?>"
            line = re.sub(pattern, tag, line, count=1)
            line = line.replace("</h1>", "</header><br>")
            source_id += 1
        res.append(line)
    return "\n".join(res)

def replace_para(content):
    res = []
    source_id = -1
    for line in content.split("\n"):
        if line.startswith("<header"):
            source_id += 1

        if line.startswith("<p>") and source_id >= 0:
                color = COLORSCHEME[source_id]['textColor']
                tag = '<main style="text-align:justify;letter-spacing:-1px;color:{}">'.format(color)
                line = line.replace("<p>", tag)
                line = line.replace("</p>", "</main>")
        res.append(line)
    return "\n".join(res)

def replace_title(content):
    res = []
    article_id = 0
    source_id = -1
    for line in content.split("\n"):
        if line.startswith("<header"):
            source_id += 1
            article_id = 0
        if line.startswith("<h2") and source_id >= 0:
            line, url = extract_url(line)
            color = COLORSCHEME[source_id]['textColor']
            tag = '<a style="color:{}; font-size:1.3rem; font-weight:bold; text-align:left; border-bottom-width:.5px; border-bottom-style:solid; border-bottom-color:{};" href="{}">'.format(color, color, url)
            pattern = r"<h2.*?>"
            line = re.sub(pattern, tag, line, count=1)
            line = line.replace("</h2>", "</a><br><br>")
            if article_id > 0:
                line = "<br><br>" + line
            article_id += 1
        res.append(line)
    return "\n".join(res)

def extract_url(line):
    url_pattern = r'<a.*?href=["\'](.*?)["\']'
    match = re.search(url_pattern, line)
    extracted_url = None
    if match:
        extracted_url = match.group(1)
    else:
        print("No URL found in the string.")
    remove_tag_pattern = r'<a.*?>'
    output_line = re.sub(remove_tag_pattern, '', line)
    output_line = output_line.replace('</a>', '')
    return output_line, extracted_url

def add_section_tag(content):
    section_start_tag = '<section style="color: black;font-family: &quot;Times New Roman&quot;;font-style: normal;font-variant-ligatures: normal;font-variant-caps: normal;font-weight: 400;letter-spacing: normal;orphans: 2;text-align: start;text-indent: 0px;text-transform: none;widows: 2;word-spacing: 0px;-webkit-text-stroke-width: 0px;white-space: normal;text-decoration-thickness: initial;text-decoration-style: initial;text-decoration-color: initial;line-height: 1.5;font-size: 18px;margin: 20px 0px;background: {};border-radius: 48px;padding: 50px;" data-pm-slice="0 0 []">'
    source_id = [0]
    color_scheme = COLORSCHEME

    def replace_header_with_section(match):
        matched_header = match.group(0) # Get the matched text (<header)
        replacement = ""
        if source_id[0] > 0:
            replacement += "</section><br>"
        color = color_scheme[source_id[0]]['backgroundColor']
        replacement += section_start_tag.format(color) + matched_header
        source_id[0] += 1
        return replacement

    pattern = r'<header'
    output = re.sub(pattern, replace_header_with_section, content)
    if source_id[0] > 0:
        output += "</section>"
    return output
'''
    <section style="color: rgb(0, 0, 0);font-family: &quot;Times New Roman&quot;;font-style: normal;font-variant-ligatures: normal;font-variant-caps: normal;font-weight: 400;letter-spacing: normal;orphans: 2;text-align: start;text-indent: 0px;text-transform: none;widows: 2;word-spacing: 0px;-webkit-text-stroke-width: 0px;white-space: normal;text-decoration-thickness: initial;text-decoration-style: initial;text-decoration-color: initial;line-height: 1.5;font-size: 18px;margin: 20px 0px;background: rgb(0, 0, 0);border-radius: 48px;padding: 30px;" data-pm-slice="0 0 []"><header style="text-align: center;font-size: 0.8rem;font-weight: bold;letter-spacing: 2px;color: rgb(254, 218, 0);"><span leaf="">随机波动 StochasticVolatility</span></header><span leaf=""><br class="ProseMirror-trailingBreak"></span><span leaf=""><a style="color: white; font-size: 1.3rem; font-weight: bold; border-bottom-style: solid; border-bottom-color: rgb(135, 24, 30);" href="https://mp.weixin.qq.com/s?__biz=MzA3MzYzNjMyMA==&amp;mid=2650273267&amp;idx=1&amp;sn=9b477b81d43e6bd4b8fa64b737bd59be&amp;subscene=21#wechat_redirect" textvalue="" target="_blank" linktype="text" data-linktype="2">四月简报：Are You Happy in This Modern World？No News is Good News</a></span><span leaf=""><br class="ProseMirror-trailingBreak"></span><span leaf=""><br class="ProseMirror-trailingBreak"></span><main style="text-align: justify;letter-spacing: -1px;color: white;"><span leaf="">“今日无事发生”，但随机波动的资讯简报《No News Is GoodNews》却总能捕捉到时代的微妙脉搏。本期节目可谓是知性与趣味齐飞：先是“海湖庄园脸”的美学与暴力，不知这又是哪门子的时尚新潮流？接着，“蓝色起源”的全女性太空飞行，如何在分裂与厌女的现实中着陆，引人深思。再聊聊经济衰退期的流行音乐，莫非大家的歌单也跟着“消费降级”了？除了这些犀利资讯，还有一本好书《在八岳南麓，直到最后》倾情推荐，一封科研工作者的来信，以及Lady</span><span leaf=""><br class="ProseMirror-trailingBreak"></span><span leaf="">Gaga的《Shallow》压轴。想知道更多？不妨戴上耳机，细细品味这份独特的资讯简报吧。</span></main></section>

# '<section style="line-height: 1.5; font-family:; font-size: 18px; margin:20px 0px; background:{}; border-radius: 48px; padding: 30px;">'
'''

def beautify(content, *arg):
    load_color_scheme(arg[0])
    content = replace_image(content)
    content = replace_preface(content)
    content = replace_source(content)
    content = replace_para(content)
    content = replace_title(content)
    content = add_section_tag(content)
    print ('html:\n' + content)
    return content