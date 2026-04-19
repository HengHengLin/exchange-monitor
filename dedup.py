"""
去重模块
用本地 JSON 文件持久化已推送的 guid，重启后不会重复推送
如果后期接 Redis，把这两个函数换掉即可，接口不变
"""

import json
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SEEN_FILE = Path(__file__).parent / "seen_guids.json"
MAX_SEEN = 5000   # 最多保留最近 5000 条，避免文件无限增长


def _load() -> set:
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def _save(seen: set):
    # 超出上限时只保留最新的（转 list 后截断）
    items = list(seen)
    if len(items) > MAX_SEEN:
        items = items[-MAX_SEEN:]
    SEEN_FILE.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def _fingerprint(guid: str) -> str:
    """统一用 MD5 缩短 guid，节省存储"""
    return hashlib.md5(guid.encode()).hexdigest()


def is_new(guid: str) -> bool:
    """返回 True 表示这条消息从未推送过"""
    seen = _load()
    return _fingerprint(guid) not in seen


def mark_seen(guid: str):
    """标记为已处理（无论是否推送，都应调用，避免重复判断）"""
    seen = _load()
    seen.add(_fingerprint(guid))
    _save(seen)
