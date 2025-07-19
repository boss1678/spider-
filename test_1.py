import os
import time
import textwrap
import requests
import certifi
from urllib.parse import urljoin
from multiprocessing import Process, Queue
from lxml import etree
from concurrent.futures import ThreadPoolExecutor


def down_sec_url(que):
    url = 'https://www.95590.org/wenxue/jinpingmei.html'
    headers = {

        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, verify=certifi.where()).text
        tree = etree.HTML(res)
        for index, tr in enumerate(tree.xpath('//div[@class="entry-content"]//li/a'), 1):
            sec_url = urljoin(url, tr.xpath('./@href')[0])
            sec_title = tr.xpath('./text()')[0]
            que.put((index, sec_title, sec_url))
        que.put(None)
        print('队列已完成...')
    except Exception as e:
        print(e)


def write_sec_text(que):
    adr = r'D:\PycharmProjects\pythonProject2\线程池\名著\金瓶梅'
    os.makedirs(adr, exist_ok=True)
    while 1:
        tasks = que.get()
        if tasks is None:
            break
        index, sec_title, trs = tasks
        filename = f'{index}--{sec_title}.txt'
        filepath = os.path.join(adr, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sec_title + '\n')
            for line in trs:
                if line:
                    line = textwrap.fill(line.strip(), width=70)
                    f.write(line + '\n\n')
            print(f'{index}--{sec_title} ---> end')


def down_sec_text_threads(que1, que2):
    futures = []

    def down_sec_text(index, sec_title, sec_url):

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "cookie": "_ga=GA1.1.1583204575.1752908045; _ga_13PMVZK1GY=GS2.1.s1752910448$o2$g1$t1752910453$j55$l0$h0",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://www.95590.org/wenxue/jinpingmei.html",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }
        try:
            resp = requests.get(url=sec_url, headers=headers, verify=certifi.where()).text
            tree = etree.HTML(resp)
            trs = [tr for tr in tree.xpath('//div[@class="entry-content"]//text()')]
            return index, sec_title, trs
        except Exception as e:
            print(e)

    with ThreadPoolExecutor(10) as t:
        while 1:
            tasks = que1.get()
            if tasks is None:
                break
            num, tit, ul = tasks
            future = t.submit(down_sec_text, num, tit, ul)
            futures.append(future)
        for future in futures:
            number, title, datas = future.result()
            # print(number, title, datas)
            que2.put((number, title, datas))
        que2.put(None)
        print('text_queue队列 ---> 已完成....')


if __name__ == '__main__':
    url_queue = Queue()
    text_queue = Queue()

    p1 = Process(target=down_sec_url, args=(url_queue,))
    p2 = Process(target=down_sec_text_threads, args=(url_queue, text_queue))
    p3 = Process(target=write_sec_text, args=(text_queue,))

    start = time.time()
    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
    end = time.time()
    print(int(end - start))
