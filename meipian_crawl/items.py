# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MeipianCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()          # 标题
    category = scrapy.Field()       # 分类
    text = scrapy.Field()           # 正文
    author = scrapy.Field()         # 作者
    article_url = scrapy.Field()    # 文章url
    article_id = scrapy.Field()     # 文章id
    words_count = scrapy.Field()    # 字数统计
