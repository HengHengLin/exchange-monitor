"""
飞书推送模块
使用「卡片消息」格式，支持颜色标签和分类显示
"""

import httpx
import logging
from config import FEISHU_WEBHOOK_URL, CATEGORY_KEYWORDS

logger = logging.getLogger(__name__)


def classify(item: dict) -> str:
    """根据标题+描述判断消息分类，返回带 emoji 的分类标签"""
    text = (item["title"] + " " + item["description"]).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw.lower() in text for kw in keywords):
            return category
    return "📢 行业动态"


def format_pub_date(raw: str) -> str:
    """把 RSS pubDate 格式化为易读时间"""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return raw


def build_card(item: dict, matched_exchanges: list[str]) -> dict:
    """
    构建飞书卡片消息
    文档: https://open.feishu.cn/document/ukTMukTMukTM/uAjNwUjLwYDM14CM2ATN
    """
    category = classify(item)
    exchanges_str = "  |  ".join(matched_exchanges)
    pub_time = format_pub_date(item["pub_date"])

    # 卡片颜色：根据分类选择
    color_map = {
        "🪙 上新币种": "blue",
        "🎁 活动促销": "green",
        "⚡ 产品上线": "turquoise",
        "💰 费率变更": "yellow",
        "⚠️ 风险公告": "red",
        "📢 行业动态": "grey",
    }
    card_color = color_map.get(category, "grey")

    # 截断过长的描述
    desc = item["description"]
    if len(desc) > 200:
        desc = desc[:200] + "..."

    card = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{category}  {item['title']}"
                },
                "template": card_color,
            },
            "elements": [
                # 交易所标签行
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**交易所**\n{exchanges_str}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**时间**\n{pub_time}"
                            }
                        }
                    ]
                },
                # 分割线
                {"tag": "hr"},
                # 正文摘要
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": desc
                    }
                },
                # 分割线
                {"tag": "hr"},
                # 原文链接按钮
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "查看原文 →"
                            },
                            "type": "default",
                            "url": item["link"]
                        }
                    ]
                }
            ]
        }
    }
    return card


def send_feishu_message(item: dict, matched_exchanges: list[str]) -> bool:
    """推送一条飞书卡片消息，返回是否成功"""
    payload = build_card(item, matched_exchanges)
    try:
        resp = httpx.post(
            FEISHU_WEBHOOK_URL,
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 0:
            return True
        else:
            logger.error(f"飞书返回错误: {result}")
            return False
    except Exception as e:
        logger.error(f"飞书推送异常: {e}")
        return False
