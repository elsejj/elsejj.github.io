import requests
import json
from html.parser import HTMLParser
from urllib.parse import urlparse



class IconParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        if tag == 'link':
            kv = dict(attrs)
            rel, href = kv.get('rel', ''), kv.get('href', '')
            if rel == 'shortcut icon':
                self._icon = href

    @property
    def icon(self):
        if '_icon' in self.__dict__:
            return self._icon
        else:
            return ''


def load():
    with open('fav.json') as fp:
        return json.load(fp)

def icon_url(url, use_proxy):
    headers = {'user-agent': 'curl/7.58.0'}
    proxy = {"https": "https://127.0.0.1:1080"}
    resp = requests.get(url, headers=headers, proxies = proxy if use_proxy else None)
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


def build(navs):
    for nav in navs:
        text, url = nav['text'], nav['url']
        proxy = 'proxy' in nav
        print(url)
        if url.startswith('http'):
            icon = icon_url(url, proxy == True)
            nav['icon'] = icon
    return navs

def write_js(navs, filename='links.js'):
    with open(filename, 'w', encoding='utf-8') as fp:
        print('let navs =', file=fp)
        print(json.dumps(navs, indent=2, ensure_ascii=False), file=fp)
        print(';', file=fp)


if __name__ == "__main__":
    d = build(load())
    write_js(d)