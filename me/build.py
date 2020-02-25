import requests
import json
from html.parser import HTMLParser
from urllib.parse import urlparse
from base64 import b64encode

class IconParser(HTMLParser):


    def __init__(self):
        super().__init__()
        self._icon = ''
        self._size = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'link':
            kv = dict(attrs)
            rel, href = kv.get('rel', ''), kv.get('href', '')
            if rel.find('icon') >= 0:
                size = self.parse_size(kv.get('sizes'))
                if size >= self._size and size <= 64:
                    self._icon = href
                    self._size = size

    def parse_size(self, size):
        if size is None:
            return 0
        p = size.split('x')
        n = 0
        if len(p) > 0:
            try:
                n = int(p[0])
            except:
                pass
        return n 

    @property
    def icon(self):
        return self._icon


def load():
    with open('fav.json', encoding="utf-8") as fp:
        return json.load(fp)


req_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 Edg/80.0.361.50'}
req_proxy = {"https": "https://127.0.0.1:1080"}


def icon_url(url, use_proxy):
    resp = requests.get(url, headers=req_headers, proxies = req_proxy if use_proxy else None)
    parser = IconParser()
    parser.feed(resp.text)

    u = urlparse(url)
    if len(parser.icon) == 0:
        return f'{u.scheme}://{u.netloc}/favicon.ico'
    else:
        if parser.icon.startswith('http'):
            return parser.icon
        elif parser.icon.startswith('//'):
            return f'{u.scheme}:{parser.icon}'
        else:
            return f'{u.scheme}://{u.netloc}{parser.icon}'

def icon_data(url, use_proxy=False):
    resp = requests.get(url, headers=req_headers, proxies = req_proxy if use_proxy else None)
    exts = ['ico', 'png', 'jpg', 'jpeg', 'gif', 'svg']
    mimemap = {
        'svg': 'image/svg+xml'
    }
    mime = 'image/ico'
    for ext in exts:
        if url.find(f'.{ext}') > 0:
            mime =  f'image/{ext}' if ext not in mimemap else mimemap[ext]
    data = b64encode(resp.content).decode('utf-8')
    return f'data:{mime};base64,{data}'


def build(navs):
    for nav in navs:
        text, url = nav['text'], nav['url']
        print(url, end=' ')
        proxy = 'proxy' in nav
        if url.startswith('http'):
            icon = icon_url(url, proxy == True)
            nav['icon'] = icon
            nav['icondata'] = icon_data(icon)
        print(icon)
    return navs

def write_js(navs, filename='links.js'):
    with open(filename, 'w', encoding='utf-8') as fp:
        print('let navs =', file=fp)
        print(json.dumps(navs, indent=2, ensure_ascii=False), file=fp)
        print(';', file=fp)


if __name__ == "__main__":
    d = build(load())
    write_js(d)
