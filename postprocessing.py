### LLM이 만든 raw response를 "무도 캐릭터 대사"처럼 보이게 다듬는 후처리 모듈 ###

from __future__ import annotations
import re
from typing import Dict, Any, List


# 공통 후처리 함수들

_SENT_END_RE = re.compile(r"(?<=[\.\!\?\~…])\s+")

def _remove_bracketed(text: str) -> str:
    return re.sub(r"[\(\[].*?[\)\]]", "", text)

def _remove_bullets_and_markdown(text: str) -> str:
    t = re.sub(r"^[\*\-]\s*", "", text, flags=re.MULTILINE)
    t = t.replace("**", "").replace("`", "")
    return t

def _remove_common_prefixes(text: str) -> str:
    t = text.strip()
    t = re.sub(r"^(답변|대답|BOT|AI|assistant)\s*[:：]\s*", "", t, flags=re.IGNORECASE)
    return t

def _normalize_whitespace(text: str) -> str:
    t = text.replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def _split_sentences(text: str) -> List[str]:
    t = text.strip()
    if not t:
        return []
    parts = _SENT_END_RE.split(t)
    return [p.strip() for p in parts if p.strip()]

def _truncate_sentences(text: str, max_sentences: int) -> str:
    if max_sentences <= 0:
        return text.strip()
    parts = _split_sentences(text)
    if len(parts) <= max_sentences:
        return text.strip()
    return " ".join(parts[:max_sentences]).strip()

def _fix_double_punct(text: str) -> str:
    t = re.sub(r"([!?~])\1{3,}", r"\1\1", text)
    return t


# 캐릭터 규칙

POSTPROCESS_POLICY: Dict[str, Dict[str, Any]] = {
    "박명수": {
        "max_sentences": 2,
        "force_prefix": ["야,", "뭐야,", "아 짜증나,", "야 이 바보야,"],
        "strip_polite": True,
        "ban_phrases": [
            "충분히 이해", "이해합니다", "신경 많이", "도움이 되셨", "권장드립니다", "추천드립니다",
            "~하시면 좋", "하시길", "하시길 바랍니다"
        ],
    },
}

def _strip_polite_korean(text: str) -> str:
    """
    존댓말을 완벽히 반말로 바꾸는 건 어렵지만,
    "상담사 톤"을 줄이는 목적의 '가벼운' 변환만 합니다.
    (너무 과격하면 의미가 깨질 수 있어서 최소만)
    """
    t = text
    t = t.replace("형님", "야").replace("누님", "야").replace("누나", "야").replace("형", "야")
    t = re.sub(r"([가-힣])요(?=[\.\!\?\~…\s]|$)", r"\1", t)
    t = t.replace("입니다", "이야")
    t = t.replace("합니다", "해")
    t = t.replace("하세요", "해")
    t = t.replace("드립니다", "줘")
    t = t.replace("됩니다", "돼")

    return t

def _apply_ban_phrases(text: str, ban_phrases: List[str]) -> str:
    """
    금지문구는 '삭제'로 처리(과하게 재작성하면 의미 깨질 수 있어서).
    """
    t = text
    for ph in ban_phrases:
        t = t.replace(ph, "")
    return _normalize_whitespace(t)

def _ensure_prefix(text: str, prefixes: List[str]) -> str:
    t = text.strip()
    if not t:
        return t
    starters = ("야", "뭐", "아", "에이", "하", "헐")
    if t.startswith(starters):
        return t
    return f"{prefixes[0]} {t}".strip()

def _apply_character_policy(character: str, text: str) -> str:
    policy = POSTPROCESS_POLICY.get(character)
    if not policy:
        return text

    t = text

    ban_phrases = policy.get("ban_phrases", [])
    if ban_phrases:
        t = _apply_ban_phrases(t, ban_phrases)

    if policy.get("strip_polite"):
        t = _strip_polite_korean(t)

    max_sentences = int(policy.get("max_sentences", 0) or 0)
    if max_sentences:
        t = _truncate_sentences(t, max_sentences)

    prefixes = policy.get("force_prefix", [])
    if prefixes:
        t = _ensure_prefix(t, prefixes)

    return t.strip()


# 메인 후처리 함수

def postprocess_response(character: str, text: str) -> str:
    """
    raw_response -> final_response 로 다듬기
    """
    t = (text or "").strip()

    t = _remove_common_prefixes(t)
    t = _remove_bracketed(t)
    t = _remove_bullets_and_markdown(t)
    t = _normalize_whitespace(t)
    t = _fix_double_punct(t)

    t = _apply_character_policy(character or "", t)

    if not t:
        t = "야, 몰라. 다시 말해봐."

    return t
