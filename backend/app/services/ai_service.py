"""AI 服务 — DeepSeek (OpenAI 兼容) 封装"""

from typing import Optional, AsyncIterator, Dict, Any, List
import httpx

from app.config import settings


class AIServiceError(Exception):
    """AI 服务异常"""
    pass


class AIService:
    """DeepSeek API 客户端（OpenAI 兼容协议）"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 120.0,
    ):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = (base_url or settings.DEEPSEEK_BASE_URL).rstrip("/")
        self.model = model or settings.DEEPSEEK_MODEL
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: Optional[float] = None,
    ):
        """非流式对话，返回完整响应对象"""
        if self.api_key == "sk-placeholder":
            raise AIServiceError(
                "DeepSeek API Key 未配置，请在 backend/.env 中设置 DEEPSEEK_API_KEY"
            )

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=timeout or self.timeout) as client:
            resp = await client.post(url, json=payload, headers=self._headers())
            if resp.status_code != 200:
                raise AIServiceError(
                    f"AI 服务请求失败 (HTTP {resp.status_code}): {resp.text[:500]}"
                )

        # 返回类似 openai.ChatCompletion 的对象
        class ChatMessage:
            def __init__(self, content):
                self.content = content

        class ChatChoice:
            def __init__(self, message):
                self.message = message

        class ChatResponse:
            def __init__(self, choices):
                self.choices = choices

        data = resp.json()
        choices = []
        for c in data.get("choices", []):
            msg = c.get("message", {})
            choices.append(ChatChoice(ChatMessage(msg.get("content", ""))))
        return ChatResponse(choices)

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """流式对话，逐 chunk yield 文本增量"""
        if self.api_key == "sk-placeholder":
            raise AIServiceError(
                "DeepSeek API Key 未配置，请在 backend/.env 中设置 DEEPSEEK_API_KEY"
            )

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload, headers=self._headers()) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise AIServiceError(f"AI 服务请求失败 (HTTP {response.status_code}): {body.decode()[:500]}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue


# 全局单例
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
