# 🌿 金瓶梅小说爬虫工具

这是一个使用 Python 构建的多进程 + 多线程爬虫项目，自动抓取《金瓶梅》小说章节内容，并将其保存为本地格式化文本文件。解决 SSL 问题，适配复杂网页结构，适合学习和实战参考。

---

## 🚀 项目功能

- 自动爬取章节目录和每章正文
- 使用 `ThreadPoolExecutor` 并发下载内容
- 使用 `multiprocessing.Queue` 实现数据传递
- 自定义输出格式，每章独立保存为 `.txt` 文件
- 解决 `SSL: UNEXPECTED_EOF` 等证书异常问题

---

## 🧱 技术栈

- Python 3.12+
- requests + certifi
- lxml
- concurrent.futures
- multiprocessing
- textwrap, os, time

---

## 📦 安装依赖

您可以使用以下命令安装所需库：

```bash
pip install requests certifi lxml
# spider-
