#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-16 16:44:38
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import random
import json
import asyncio
import aiohttp
import aiofiles
import traceback
from pyquery import PyQuery as pq


folder_name = 'mp-articles'


children_name = ['兴趣', '美文', '美食', '生活', '旅行', '摄影', '亲子', '女神']


category_dict = {
    '11': 'https://www.meipian.cn/photo',
    '12': 'https://www.meipian.cn/tour',
    '13': 'https://www.meipian.cn/beauty',
    '14': 'https://www.meipian.cn/life',
    '15': 'https://www.meipian.cn/fiction',
    '16': 'https://www.meipian.cn/baby',
    '17': 'https://www.meipian.cn/hobby',
    '18': 'https://www.meipian.cn/food'
}


async def start_category(category_id):
    '''各个分类的起点'''
    async with aiohttp.ClientSession() as session:
        res = await session.get(category_dict[category_id])
        text = await res.text(encoding='utf8')
        max_id = await get_max_category_id(text)
        while True:
            try:
                n = await post(category_id, max_id, session)
            except Exception as e:
                n = None
                print('Error: ', e)
                async with aiofiles.open('err.log', 'ab+') as f:
                    log = repr(e) + '\n'
                    await f.write(log.encode('utf-8'))

            max_id = n if n else (int(max_id) - 20)
            if int(max_id) <= 0:
                return
            print('等待一会')
            # await asyncio.sleep(random.randint(1, 5))


async def get_max_category_id(html):
    '''访问分类首页, 取得max_id'''
    doc = pq(html)
    max_id = max([int(i.values()[1]) for i in doc('.item.server-item')])
    return max_id


async def post(category_id, max_id, session):
    '''不断循环 max_id, 抓取 ajax 数据'''
    url = 'https://www.meipian.cn/default/article.php'
    data = {"category_id": "11", "max_id": "100",
            "controller": "category", "action": "list"}
    data['max_id'] = str(max_id)
    data['category_id'] = str(category_id)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3)'
                             ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    res = await session.post(url, data=json.dumps(data), headers=headers)
    rst = await res.text(encoding='utf8')
    rst = json.loads(rst)
    max_id = None
    if rst['articles']:
        max_id = min([i['id'] for i in rst['articles']])
        for article in rst['articles']:
            if article['article_id'] not in filenames:
                await fetch_url(session, article.get('article_id'), article.get('category_name'), article['title'])
                # await asyncio.sleep(random.randint(2, 3))  # 避免太频繁访问服务器拒绝
            else:
                print('文件已存在')
    return max_id


async def fetch_url(session, article_id, category_name, title):
    '''通过文章 id 拼接对应的 url, 抓取文章对应的页面'''
    url = 'https://www.meipian.cn/{0}'.format(article_id)
    try:
        res = await session.get(url)
        html = await res.text(encoding='utf8')
        print('文章链接'.center(20, '-'), url)
        await parse(html, category_name, title, article_id)
    except (aiohttp.client_exceptions.ServerDisconnectedError, aiohttp.client_exceptions.ClientOSError) as e:
        print('Error: ', e)
        async with aiofiles.open('err.log', 'ab+') as f:
            log = repr(e) + '\n'
            await f.write(log.encode('utf-8'))


async def parse(html, category_name, title, article_id):
    '''解析文章页面, 提取相关数据'''
    doc = pq(html)
    # title = doc('.meipian-title').text()
    if not title:
        title = doc('.mp-title').text()
    content = "\n".join([i.text_content() for i in doc('.text').children() if i.text_content()])
    print('分类', category_name)
    print('标题', title)
    # print('内容', content)
    print('文章id', article_id)
    await save_to_file(category_name, article_id, content)


# async def save_to_file(category_name, article_id, content):
#     '''存储'''
#     txt_filename = article_id + '.txt'
#     txt_path = os.path.join(folder_name, category_name, txt_filename)
#     with open(txt_path, 'wt') as f:
#         f.write(content)
#     print('保存成功')

async def save_to_file(category_name, article_id, content):
    txt_filename = article_id + '.txt'
    txt_path = os.path.join(folder_name, category_name,  txt_filename)
    async with aiofiles.open(txt_path, 'wb') as f:
        await f.write(content.encode('utf-8'))
        print('保存成功')


def get_txtname(dir):
    names = []
    for _, dirs, files in os.walk(dir):
        for dir in dirs:
            get_txtname(dir)
        name = (file.split('.')[0] for file in files)
        names.extend(name)
    return set(names)


def main():
    loop = asyncio.get_event_loop()
    tasks = [start_category(i) for i in category_dict.keys()]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()


if __name__ == '__main__':
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    for name in children_name:
        category_path = os.path.join(folder_name, name)
        if not os.path.exists(category_path):
            os.mkdir(category_path)

    filenames = get_txtname(folder_name)

    main()