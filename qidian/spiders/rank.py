import scrapy
import os
from fontTools.ttLib import TTFont
import requests


def extract_with_css(el, query):
    """ 用css选择器提取数据 """
    return el.css(query).extract_first(default='').strip()


def add_scheme(s):
    """ url加上协议 """
    if s.startswith('//'):
        s = 'https:' + s
    return s


class RankSpider(scrapy.Spider):
    """ 爬作品排行榜 """

    name = 'rank'

    def __init__(self, *args, **kwargs):
        self.max_page = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        self.num_map = {'period': '.', 'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'}
        super().__init__(*args, **kwargs)

    def start_requests(self):
        self.type = getattr(self, 'type', 'yuepiao')  # 默认爬月票榜
        self.url = 'https://www.qidian.com/rank/%s?style=1' % self.type
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        if self.max_page == 0:
            self.max_page = int(response.css('div[data-pagemax]::attr(data-pagemax)').extract_first())

        yield from self.parse_item(response)

        for i in range(2, self.max_page + 1):
            url = self.url + ('&page=%d' % i)
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response):
        font = None
        font_file = response.css('div.book-img-text').re_first(r'qidian\.gtimg\.com\/qd_anti_spider\/(\w+\.woff)')
        if font_file:
            font = self.create_font(font_file)

        for book in response.css('div.book-img-text li'):
            item = {
                'rank': int(extract_with_css(book, 'span.rank-tag::text')),
                'id': extract_with_css(book, 'a[data-eid=qd_C39]::attr(data-bid)'),
                'url': add_scheme(extract_with_css(book, 'a[data-eid=qd_C39]::attr(href)')),
                'img_url': add_scheme(extract_with_css(book, 'a[data-eid=qd_C39] img::attr(src)')),
                'name': extract_with_css(book, 'a[data-eid=qd_C40]::text'),
                'author_name': extract_with_css(book, 'a[data-eid=qd_C41]::text'),
                'author_url': add_scheme(extract_with_css(book, 'a[data-eid=qd_C41]::attr(href)')),
                'class': extract_with_css(book, 'a[data-eid=qd_C42]::text'),
                'status': extract_with_css(book, 'p.author span:last-child::text'),
                'intro': extract_with_css(book, 'p.intro::text'),
                'update_chapter_name': extract_with_css(book, 'a[data-eid=qd_C43]::text'),
                'update_chapter_url': add_scheme(extract_with_css(book, 'a[data-eid=qd_C43]::attr(href)')),
                'update_time': extract_with_css(book, 'p.update span:last-child::text')
            }
            if font:
                item[self.type] = int(self.modify_data(extract_with_css(book, 'div.book-right-info div.total style + span::text'), font))
            yield item

    def get_font(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content

    def create_font(self, font_file):
        if not os.path.exists('./fonts'):
            os.mkdir('./fonts')

        file_list = os.listdir('./fonts')
        if font_file not in file_list:
            # print('不在字体库中, 下载:', font_file)
            url = 'https://qidian.gtimg.com/qd_anti_spider/' + font_file
            new_file = self.get_font(url)
            with open('./fonts/' + font_file, 'wb') as f:
                f.write(new_file)

        return TTFont('./fonts/' + font_file)

    def modify_data(self, data, font):
        """ 把获取到的数据用字体对应起来，得到真实数据 """
        data = data.encode('ascii', 'xmlcharrefreplace').decode()
        # print(data)
        cmap = font['cmap'].getBestCmap()
        # print(char_map)
        for code, name in cmap.items():
            c = '&#%d;' % code
            if c in data:
                data = data.replace(c, self.num_map[name])
        return data


class FansRankSpider(scrapy.Spider):
    """ 爬粉丝打赏排行榜 """

    name = 'fans-rank'

    def start_requests(self):
        self.type = getattr(self, 'type', '1')  # 默认爬日榜
        self.url = 'https://www.qidian.com/rank/fans?dateType=%s' % self.type
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        for fan in response.css('div.fans-data-list li[data-rid]'):
            yield {
                'rank': int(extract_with_css(fan, 'span.rank-tag::text')),
                'nickname': extract_with_css(fan, 'a::text'),
                'fan_url': add_scheme(extract_with_css(fan, 'a::attr(href)')),
                'qidianbi': int(extract_with_css(fan, 'i::text'))
            }
