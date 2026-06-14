"""翻译客户端 — 对接第三方翻译 API

支持: Google Translate / 未来可扩展 DeepL 等

API Key 来源（按优先级）:
  1. GOOGLE_TRANSLATE_API_KEY 环境变量
  2. 配置文件 translators.google.api_key
  3. 未配置时返回错误提示，由用户手动设置

此模块仅供手动调用，不会在扫描/识别流程中自动触发。
"""

import os
from typing import Optional

import httpx

from backend.config_manager import ConfigManager


GOOGLE_API = "https://translation.googleapis.com/language/translate/v2"


def get_api_key(service: str = "google") -> Optional[str]:
    """获取翻译服务 API Key"""
    if service == "google":
        key = os.environ.get("GOOGLE_TRANSLATE_API_KEY", "").strip()
        if key:
            return key
        config = ConfigManager.instance()
        return config.get("translators.google.api_key", "").strip() or None
    return None


async def translate(
    text: str,
    target_lang: str = "zh-CN",
    source_lang: str = "auto",
    service: str = "google",
) -> Optional[str]:
    """
    手动调用翻译

    Args:
        text: 待翻译文本
        target_lang: 目标语言 (zh-CN / en)
        source_lang: 源语言 (auto)
        service: 翻译服务 (google)

    Returns:
        翻译结果，失败返回 None
    """
    api_key = get_api_key(service)
    if not api_key:
        return None

    if service == "google":
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    GOOGLE_API,
                    params={"key": api_key},
                    json={
                        "q": text,
                        "target": target_lang,
                        "source": source_lang,
                        "format": "text",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    translations = data.get("data", {}).get("translations", [])
                    if translations:
                        return translations[0].get("translatedText", "")
        except Exception:
            pass

    return None
