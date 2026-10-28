"""Dictionary Pinyin conversion, independent of transcription and file output."""

import re
from functools import lru_cache
from pathlib import Path


_HANZI_RUN = re.compile(
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
    r"\U00020000-\U0002ffff\U00030000-\U000323af]+"
)


@lru_cache(maxsize=1)
def _get_tokenizer():
    """Keep Jieba's dictionary cache in the project, outside temporary storage."""
    import jieba

    cache_dir = Path(__file__).resolve().parent.parent / ".cache" / "jieba"
    cache_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = jieba.Tokenizer()
    tokenizer.tmp_dir = str(cache_dir)
    return tokenizer


def hanzi_to_pinyin(text: str) -> str:
    """Convert Hanzi to tone-marked dictionary Pinyin without tone sandhi.

    Preserve non-Hanzi text (including English, punctuation, and whitespace).
    Phrase lookup resolves common polyphonic characters; the result is a
    dictionary-based reading rather than a prediction of recorded pronunciation.
    """
    from pypinyin import Style, lazy_pinyin

    def convert(match: re.Match) -> str:
        return " ".join(
            lazy_pinyin(
                match.group(),
                style=Style.TONE,
                errors="default",
                tone_sandhi=False,
            )
        )

    return _HANZI_RUN.sub(convert, text)


def annotate_hanzi(text: str) -> str:
    """Append dictionary Pinyin in parentheses after each segmented Chinese word.

    Non-Hanzi text is preserved. Word boundaries are inferred by Jieba and may
    vary for names or ambiguous phrases.
    """
    def annotate(match: re.Match) -> str:
        return " ".join(
            f"{word}({hanzi_to_pinyin(word)})"
            for word in _get_tokenizer().cut(match.group(), cut_all=False)
        )

    return _HANZI_RUN.sub(annotate, text)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print(annotate_hanzi(text))
    else:
        print("Usage: python pinyin.py <text>")
