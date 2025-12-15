# ==========================================
# AI 模型配置
# ==========================================

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AIConfig:
    """AI 模型配置。

    Attributes:
        model: AI 模型名称
        system_prompt: 系统提示词
        timeout: 请求超时秒数
        max_retries: 最大重试次数
    """

    model: str
    system_prompt: str
    timeout: int
    max_retries: int

    @classmethod
    def from_env(cls) -> AIConfig:
        """从环境变量加载配置。"""
        timeout_str = os.environ.get("XAI_TIMEOUT", "120")
        max_retries_str = os.environ.get("XAI_MAX_RETRIES", "3")

        return cls(
            # grok-4-1-fast 支持完整的 agentic tools 和 inline citations
            # grok-4-1-fast-non-reasoning 不支持自动 inline citations
            model=os.environ.get("XAI_MODEL", "grok-4-1-fast"),
            system_prompt=os.environ.get(
                "XAI_SYSTEM_PROMPT",
                "You are Grok, a highly intelligent, helpful AI assistant.",
            ),
            timeout=int(timeout_str) if timeout_str.isdigit() else 120,
            max_retries=int(max_retries_str) if max_retries_str.isdigit() else 3,
        )


# 单例实例
_ai_config = AIConfig.from_env()

# 便捷访问常量
AI_MODEL = _ai_config.model
AI_SYSTEM_PROMPT = _ai_config.system_prompt
AI_TIMEOUT = _ai_config.timeout
AI_MAX_RETRIES = _ai_config.max_retries


__all__ = [
    "AI_MAX_RETRIES",
    "AI_MODEL",
    "AI_SYSTEM_PROMPT",
    "AI_TIMEOUT",
    "AIConfig",
]

