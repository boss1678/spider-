"""
1, 创建三个进程分别对应下载章节url任务函数, 下载章节内容任务函数, 和写入本地文件任务函数
2, 下载章节内容任务函数, 和写入本地文件任务函数假如协程的逻辑
协程里await后得到返回值, 返回值是一个列表, 内容就是任务函数的返回值, result = await asyncio.gather(*tasks)
线程池里submit后得到一个Future对象, 通过Future对象.result()取值, 内容是任务函数的返回值 future = t.submit()==>future.result()
"""

import requests
import os
import re
import time
import textwrap
from multiprocessing import Process, Queue
import aiohttp, asyncio, aiofiles
from lxml import etree
from urllib.parse import urljoin


def down_chart_url(queue):
    url = 'https://www.shicimingju.com/book/xiyouji.html'
    headers = {

        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers).content
        resp = res.decode('utf-8')
        tree = etree.HTML(resp)
        for index, tr in enumerate(tree.xpath('//div[@class="list"]/a'), 1):
            chart_url = urljoin(url, tr.xpath('./@href')[0])
            chart_title = tr.xpath('./text()')[0]
            queue.put((index, chart_title, chart_url))
        queue.put(None)
    except Exception as e:
        print(e)


async def down_chart_text(session, index, chart_title, chart_url):
    async with session.get(chart_url) as res:
        data = await res.text('utf-8')
        tree = etree.HTML(data)
        trs = tree.xpath('//div[@class="text p_pad"]//text()')
        dats = [re.sub(r'\xa0+', '\n\n', tr) for tr in trs]
        return index, chart_title, dats


# 同步队列改为异步队列的逻辑(工具函数)
async def bridge_queue(mp_queue, async_queue):
    loop = asyncio.get_running_loop()
    while True:
        # 在后台线程中执行同步队列的 get 方法
        task = await loop.run_in_executor(None, mp_queue.get)

        if task is None:  # 终止信号
            await async_queue.put(None)
            break
        await async_queue.put(task)


def run_main(queue_1, queue_2):
    async def main(qu1, qu2):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }
        args_list = []
        async with aiohttp.ClientSession(headers=headers) as session:
            while 1:
                tasks = await qu1.get()
                if tasks is None:
                    break
                args_list.append(tasks)

            tasks = [down_chart_text(session, *r) for r in args_list]
            results = await asyncio.gather(*tasks)
            for index, title, content in results:
                queue_2.put((index, title, content))
            queue_2.put(None)

    async def task():
        async_queue = asyncio.Queue()

        # ✅ 步骤一：同步队列 → 异步队列
        await bridge_queue(queue_1, async_queue)

        # ✅ 步骤二：使用异步队列执行下载任务
        await main(async_queue, queue_2)

    asyncio.run(task())


def run_writer(queue):
    async def write_chart_text(qu2):
        while 1:
            tasks = await qu2.get()
            if tasks is None:
                break
            index, title, datas = tasks
            adr = os.path.abspath(r'D:\PycharmProjects\pythonProject2\协程\名著\西游记')
            os.makedirs(adr, exist_ok=True)
            filename = f'{index}--{title}'
            filepath = os.path.join(adr, filename)
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(title + '\n')
                for line in datas:
                    if line:
                        line = textwrap.fill(line.strip(), width=70)
                        await f.write(line + '\n')
                print(f'{index}--{title} --> 写入完成....')

    async def task():
        async_queue = asyncio.Queue()

        # ✅ 步骤一：同步队列 → 异步队列
        await bridge_queue(queue, async_queue)

        # ✅ 步骤二：使用异步队列执行下载任务
        await write_chart_text(async_queue)

    asyncio.run(task())


if __name__ == '__main__':
    # 创建队列:
    q1 = Queue()
    q2 = Queue()

    # 创建进程:
    # 进程调用的是普通函数, 要将协程函数的调用包裹在普通函数里面.
    p1 = Process(target=down_chart_url, args=(q1,))
    p2 = Process(target=run_main, args=(q1, q2))
    p3 = Process(target=run_writer, args=(q2,))

    # 计时开始:
    s = time.time()

    # 调用进程:
    p1.start()
    p2.start()
    p3.start()

    # 结束进程:
    p1.join()
    p2.join()
    p3.join()

    # 计时结束:
    e = time.time()

    # 打印总用时长:
    print(int(e - s))
