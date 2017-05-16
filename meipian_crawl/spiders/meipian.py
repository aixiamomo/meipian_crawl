# -*- coding: UTF-8 -*-
import re
import scrapy
from bs4 import BeautifulSoup  # 解析scrapy抓取的response，可以用习惯的包
from scrapy.http import Request
from meipian_crawl.items import MeipianCrawlItem


class Myspider(scrapy.Spider):
    name = 'meipian'  # 同entrypoint.py文件中的第三个参数

    def __init__(self):
        super(Myspider, self).__init__(scrapy.Spider)
        self.name = 'meipian'
        self.allowed_domains = ['meipian.cn']
        self.category = {'photo': '摄影',
                         'tour': '旅行',
                         'beauty': '女神',
                         'life': '生活',
                         'fiction': '美文',
                         'baby': '亲子',
                         'hobby': '兴趣',
                         'food': '美食'}
        self.bash_url = 'https://www.meipian.cn/'
        self.category_name = self.category.keys()

    def start_requests(self):
        for category in self.category_name:
            url = self.bash_url + category
            yield Request(url, self.parse)  # 回调：将Request返回的response作为参数传递给parse

    def parse(self, response):
        print(response.text)
