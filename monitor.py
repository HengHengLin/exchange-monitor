"""
竞对动态监控 & 飞书推送
支持两种运行模式:
  python monitor.py          # 本地循环模式
  python monitor.py --once   # GitHub Actions 单次模式
"""

import sys
import os
import time
import logging
import xml.etree.ElementTree as ET

import httpx

from config import EXCHANGE_KEYWORDS, POLL_INTERVAL_SECONDS, CATEGORY_KEYWORDS
from feishu import send_feishu_message
from dedup import is_new, mark_seen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

BLOCKBEATS_URL = "https://api.theblockbeats.news/v1/open-api/home-xml"


def fetch_news() -> list[dict]:
    try:
        resp = httpx.get(
            BLOCKBEATS_URL,
            headers={
                "language": "cn",
                "User-Agent": "Mozilla/5.0 (compatible; ExchangeMonitor/1.0)",
            },
            timeout=15,
        )
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"拉取 BlockBeats 失败: {e}")
        return []

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        logger.error(f"XML 解析失败: {e}")
        return []

    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        description = item.findtext("description") or ""
        link = item.findtext("link") or ""
        pub_date = item.findtext("pubDate") or ""
        guid = item.findtext("guid") or link

        description = description.replace("BlockBeats 消息，", "").strip()

        items.append({
            "title": title,
            "description": description,
            "link": link,
            "pub_date": pub_date,
            "guid": guid,
        })

    logger.info(f"共拉取 {len(items)} 条新闻")
    return items


def match_exchanges(item: dict) -> list[str]:
    text = (item["title"] + " " + item["description"]).lower()
    hit = []
    for exchange, keywords in EXCHANGE_KEYWORDS.items():
        if any(kw.lower() in text for kw in keywords):
            hit.append(exchange)
    return hit


def run_once():
    news_list = fetch_news()
    pushed = 0

    for item in news_list:
        guid = item["guid"]

        if not is_new(guid):
            continue

        matched = match_exchanges(item)
        if not matched:
            mark_seen(guid)
            continue

        success = send_feishu_message(item, matched)
        if success:
            mark_seen(guid)
            pushed += 1
            logger.info(f"已推送: [{', '.join(matched)}] {item['title'][:50]}")
        else:
            logger.warning(f"推送失败，下次重试: {item['title'][:50]}")

    logger.info(f"本轮推送 {pushed} 条")


def main():
    once_mode = "--once" in sys.argv

    if once_mode:
        # GitHub Actions 模式：执行一次就退出
        logger.info("=== 单次执行模式（GitHub Actions）===")
        run_once()
    else:
        # 本地循环模式
        logger.info("=== 竞对监控启动（本地循环模式）===")
        logger.info(f"轮询间隔: {POLL_INTERVAL_SECONDS}s")
        while True:
            try:
                run_once()
            except Exception as e:
                logger.exception(f"轮询异常: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
