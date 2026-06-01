import re
from dataclasses import dataclass, asdict
from typing import Dict, List


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")
WORD_RE = re.compile(r"\b\w+\b")

BULLET_RE = re.compile(r"^\s*([-*•]|\d+[.)])\s+", re.MULTILINE)
SEMICOLON_RE = re.compile(r";")

TRIGGER_PATTERNS = [
    r"\bincluding\b",
    r"\bsuch as\b",
    r"\branging from\b",
    r"\bfrom\b.+\bto\b",
    r"\bwhether\b.+\bor\b",
    r"\bnot only\b.+\bbut also\b",
    r"\bacross\b",
    r"\bvarious\b",
    r"\bmultiple\b",
]

ABSTRACT_NOUNS = {
    "readability", "authorship", "trust", "style", "voice", "governance",
    "transparency", "accountability", "fairness", "safety", "risk",
    "compliance", "policy", "capacity", "infrastructure", "identity",
    "legitimacy", "authority", "access", "control", "quality",
}


@dataclass
class EnumMetrics:
    word_count: int
    sentence_count: int
    paragraph_count: int
    surface_list_count: int
    semicolon_count: int
    trigger_phrase_count: int
    enumerative_sentence_count: int
    enumerative_paragraph_count: int
    surface_list_rate_per_1000_words: float
    trigger_phrase_rate_per_1000_words: float
    enumerative_sentence_rate: float
    enumerative_paragraph_rate: float
    mean_list_span: float
    substitution_score: float


def split_sentences(text: str) -> List[str]:
    parts = SENTENCE_SPLIT_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def split_paragraphs(text: str) -> List[str]:
    parts = PARAGRAPH_SPLIT_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_trigger_phrases(text: str) -> int:
    total = 0
    lowered = text.lower()
    for pattern in TRIGGER_PATTERNS:
        total += len(re.findall(pattern, lowered))
    return total


def estimate_list_span(sentence: str) -> int:
    comma_items = len([p for p in sentence.split(",") if p.strip()])
    and_or_items = len(re.findall(r"\b(and|or)\b", sentence.lower())) + 1
    return max(comma_items, and_or_items)


def has_parallel_chain(sentence: str) -> bool:
    span = estimate_list_span(sentence)
    if span >= 4:
        return True
    lowered = sentence.lower()
    trigger_hit = any(re.search(pattern, lowered) for pattern in TRIGGER_PATTERNS)
    abstract_hits = sum(1 for word in ABSTRACT_NOUNS if re.search(rf"\b{re.escape(word)}\b", lowered))
    if trigger_hit and span >= 3:
        return True
    if abstract_hits >= 4:
        return True
    if sentence.count("?") >= 2:
        return True
    return False


def compute_metrics(text: str) -> Dict[str, float]:
    words = count_words(text)
    sentences = split_sentences(text)
    paragraphs = split_paragraphs(text)

    surface_list_count = len(BULLET_RE.findall(text))
    semicolon_count = len(SEMICOLON_RE.findall(text))
    trigger_phrase_count = count_trigger_phrases(text)

    enumerative_sentences = [s for s in sentences if has_parallel_chain(s)]
    enumerative_sentence_count = len(enumerative_sentences)

    enumerative_paragraph_count = 0
    for paragraph in paragraphs:
        p_sentences = split_sentences(paragraph)
        if any(has_parallel_chain(sentence) for sentence in p_sentences):
            enumerative_paragraph_count += 1

    spans = [estimate_list_span(s) for s in enumerative_sentences]
    mean_list_span = sum(spans) / len(spans) if spans else 0.0

    safe_words = max(words, 1)
    safe_sentences = max(len(sentences), 1)
    safe_paragraphs = max(len(paragraphs), 1)

    surface_rate = surface_list_count / safe_words * 1000
    trigger_rate = trigger_phrase_count / safe_words * 1000
    enum_sentence_rate = enumerative_sentence_count / safe_sentences
    enum_paragraph_rate = enumerative_paragraph_count / safe_paragraphs

    substitution_score = enum_sentence_rate / (surface_rate + 0.01)

    metrics = EnumMetrics(
        word_count=words,
        sentence_count=len(sentences),
        paragraph_count=len(paragraphs),
        surface_list_count=surface_list_count,
        semicolon_count=semicolon_count,
        trigger_phrase_count=trigger_phrase_count,
        enumerative_sentence_count=enumerative_sentence_count,
        enumerative_paragraph_count=enumerative_paragraph_count,
        surface_list_rate_per_1000_words=surface_rate,
        trigger_phrase_rate_per_1000_words=trigger_rate,
        enumerative_sentence_rate=enum_sentence_rate,
        enumerative_paragraph_rate=enum_paragraph_rate,
        mean_list_span=mean_list_span,
        substitution_score=substitution_score,
    )
    return asdict(metrics)
