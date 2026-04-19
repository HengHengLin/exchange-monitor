"""
配置文件
Webhook URL 从环境变量读取，方便 GitHub Actions Secrets 注入
"""

import os

# 从环境变量读取（GitHub Actions Secrets 注入）
# 本地测试时可以直接赋值字符串，或在终端 export FEISHU_WEBHOOK_URL=https://...
FEISHU_WEBHOOK_URL = os.environ.get(
    "FEISHU_WEBHOOK_URL",
    "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN_HERE"
)

POLL_INTERVAL_SECONDS = 300   # 仅本地循环模式使用

EXCHANGE_KEYWORDS = {
    "Binance": ["binance", "币安", "BNB"],
    "Bitget": ["bitget", "比特get"],
    "Bybit": ["bybit", "比特比"],
    "MEXC / 抹茶": ["mexc", "抹茶", "MXC"],
    "KuCoin": ["kucoin", "库币", "KCS"],
    "WEEX": ["weex"],
    "JuCoin": ["jucoin", "聚币"],
    "OKX": ["okx", "okex", "欧易"],
    "Gate.io": ["gate.io", "gate io", "芝麻开门"],
    "Huobi / HTX": ["huobi", "火币", "htx"],
}

CATEGORY_KEYWORDS = {
    "🪙 上新币种": ["上线", "上币", "新币", "listing", "new token", "将于"],
    "🎁 活动促销": ["活动", "空投", "airdrop", "奖励", "赠送", "福利", "竞赛", "交易大赛"],
    "⚡ 产品上线": ["上线", "推出", "发布", "launch", "新功能", "升级", "支持"],
    "💰 费率变更": ["手续费", "费率", "fee", "佣金", "降费", "涨费"],
    "⚠️ 风险公告": ["维护", "暂停", "宕机", "下线", "delisting", "警告", "风险"],
}
