"""
LLM客户端封装
统一使用OpenAI格式调用
支持免费模型限流自动重试
"""

import json
import re
import time
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI, APIConnectionError, APITimeoutError, RateLimitError

from ..config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=300.0
        )
    
    def _make_request(self, kwargs: dict) -> Any:
        """发送请求，免费模型限流时自动重试"""
        max_retries = 3
        retry_delays = [30, 60, 120]
        
        for attempt in range(max_retries):
            try:
                return self.client.chat.completions.create(**kwargs)
            except RateLimitError as e:
                error_msg = str(e)
                if ':free' not in self.model:
                    raise e
                retry_after = retry_delays[attempt] if attempt < len(retry_delays) else 120
                logger.warning(f"LLM限流 ({attempt+1}/{max_retries})，等待{retry_after}秒后重试...")
                time.sleep(retry_after)
            except APITimeoutError as e:
                retry_after = retry_delays[attempt] if attempt < len(retry_delays) else 120
                logger.warning(f"LLM请求超时 ({attempt+1}/{max_retries})，等待{retry_after}秒后重试...")
                time.sleep(retry_after)
            except APIConnectionError as e:
                retry_after = retry_delays[attempt] if attempt < len(retry_delays) else 120
                logger.warning(f"LLM连接错误 ({attempt+1}/{max_retries})，等待{retry_after}秒后重试...")
                time.sleep(retry_after)
        
        raise Exception(f"LLM请求失败，已重试{max_retries}次")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self._make_request(kwargs)
        msg = response.choices[0].message
        content = (msg.content or "").strip() or (getattr(msg, "reasoning", None) or "").strip()
        if content:
            content = re.sub(r'<thinking>[\s\S]*?</thinking>', '', content).strip()
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        cleaned_response = response.strip()
        # 清理 markdown 代码块标记
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            data = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # 可能是被截断的 JSON，尝试修复
            fixed = self._fix_truncated_json(cleaned_response)
            if fixed is not None:
                data = fixed
            else:
                raise ValueError(f"LLM返回的JSON格式无效: {cleaned_response[:500]}...")
        
        # 修复模型输出格式（nemotron-3 等会在 key 前加冒号如 ":sections"）
        return self._strip_colon_keys(data)
    
    @staticmethod
    def _strip_colon_keys(obj):
        """递归去除所有 dict key 的前导冒号（nemotron-3 等模型的怪癖）"""
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                clean_key = k.lstrip(':') if isinstance(k, str) else k
                new_obj[clean_key] = LLMClient._strip_colon_keys(v)
            return new_obj
        elif isinstance(obj, list):
            return [LLMClient._strip_colon_keys(item) for item in obj]
        return obj
    
    def _fix_truncated_json(self, content: str) -> Optional[Dict[str, Any]]:
        """尝试修复被截断的 JSON"""
        import re as _re
        
        # 1. 闭合未闭合的字符串和括号
        content = content.strip()
        
        # 找到最后一对匹配的 {}
        # 先找最外层的花括号
        start = content.find('{')
        if start == -1:
            return None
        
        # 从末尾找到匹配的闭合括号
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(content)):
            ch = content[i]
            if escape_next:
                escape_next = False
                continue
            if ch == '\\':
                escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    # 找到完整 JSON
                    json_str = content[start:i+1]
                    try:
                        return json.loads(json_str)
                    except:
                        return None
        
        # 2. 如果没找到匹配的 }，尝试截断修复
        # 去掉末尾被截断的部分，尝试找到有效 JSON
        # 去掉最后一个可能损坏的键值对
        if in_string:
            content += '"'  # 闭合字符串
            # 尝试闭合括号
            content += '}' * depth  # depth=0 时加了1层
            try:
                return json.loads(content)
            except:
                # 再试：去掉最后一个损坏的字段
                pass
        
        # 3. 暴力修复：去掉最后一个不完整的内容
        if in_string:
            content += '"'
        
        open_braces = content.count('{') - content.count('}') if not depth else depth
        content += '}' * open_braces
        
        try:
            return json.loads(content)
        except:
            return None