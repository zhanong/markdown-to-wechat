def replace_para(content):
    res = []
    for line in content.split("\n"):
        if line.startswith("<p>"):
            line = line.replace("<p>", gen_css("para"))
        res.append(line)
    return "\n".join(res)

def gen_css(path, *args):
    tmpl = open("./assets/{}.tmpl".format(path), "r").read()
    return tmpl.format(*args)

def replace_header(content):
    res = []
    for line in content.split("\n"):
        l = line.strip()
        if l.startswith("<h") and l.endswith(">") > 0:
            tag = l.split(' ')[0].replace('<', '')
            value = l.split('>')[1].split('<')[0]
            digit = tag[1]
            font =  (18 + (4 - int(tag[1])) * 2) if (digit >= '0' and digit <= '9') else 18
            res.append(gen_css("sub", tag, font, value, tag))
        else:
            res.append(line)
    return "\n".join(res)

def replace_links(content):
    pq = PyQuery(open('origi.html').read())
    links = pq('a')
    refs = []
    index = 1
    if len(links) == 0:
        return content
    for l in links.items():
        link = gen_css("link", l.text(), index)
        index += 1
        refs.append([l.attr('href'), l.text(), link])

    for r in refs:
        orig = "<a href=\"{}\">{}</a>".format(html.escape(r[0]), r[1])
        print(orig)
        content = content.replace(orig, r[2])
    content = content + "\n" + gen_css("ref_header")
    content = content + """<section class="footnotes">"""
    index = 1
    for r in refs:
        l = r[2]
        line = gen_css("ref_link", index, r[1], r[0])
        index += 1
        content += line + "\n"
    content = content + "</section>"
    return content

def fix_image(content):
    pq = PyQuery(open('origi.html').read())
    imgs = pq('img')
    for line in imgs.items():
        link = """<img alt="{}" src="{}" />""".format(line.attr('alt'), line.attr('src'))
        figure = gen_css("figure", link, line.attr('alt'))
        content = content.replace(link, figure)
    return content

def format_fix(content):
    # content = content.replace("<ul>\n<li>", "<ul><p></p><li>")
    # content = content.replace("</li>\n</ul>", "</li></ul>")
    # content = content.replace("<ol>\n<li>", "<ol><li>")
    # content = content.replace("</li>\n</ol>", "</li></ol>")
    content = content.replace("</li>", "</li>\n<p></p>")
    content = content.replace("background: #272822", gen_css("code"))
    content = content.replace("""<pre style="line-height: 125%">""", """<pre style="line-height: 125%; color: white; font-size: 11px;">""")
    return content

def css_beautify(content):
    content = replace_para(content)
    content = replace_header(content)
    content = replace_links(content)
    content = format_fix(content)
    content = fix_image(content)
    content = gen_css("header") + content + "</section>"
    print ('html' + content)
    return content