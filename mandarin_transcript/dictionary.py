"""Offline word definitions from the project's CC-CEDICT download."""

from functools import lru_cache
from pathlib import Path
import re

from mandarin_transcript.pinyin import _HANZI_RUN


DICTIONARY_PATH = Path(__file__).resolve().parent.parent / "data" / "cedict" / "cedict_ts.u8"
_ENTRY = re.compile(r"^(\S+) (\S+) \[([^]]+)\] /(.+)/$")


@lru_cache(maxsize=1)
def load_dictionary():
    try:
        source = DICTIONARY_PATH.open(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"CC-CEDICT dictionary is missing: {DICTIONARY_PATH}") from exc
    entries = {}
    with source:
        for line in source:
            match = _ENTRY.match(line.rstrip())
            if match is None:
                continue
            traditional, simplified, reading, definitions = match.groups()
            entry = (reading, definitions.replace("/", "; "))
            for word in {traditional, simplified}:
                meanings = entries.setdefault(word, [])
                if entry not in meanings:
                    meanings.append(entry)
    return entries


def dictionary_definitions(text):
    """List all senses for longest matching words; never guess missing meanings."""
    runs = list(_HANZI_RUN.finditer(text))
    if not runs:
        return ""
    entries = load_dictionary()
    max_length = max(map(len, entries), default=1)
    lines = []
    seen = set()
    for match in runs:
        run = match.group()
        offset = 0
        while offset < len(run):
            word = run[offset]
            for length in range(min(max_length, len(run) - offset), 0, -1):
                candidate = run[offset:offset + length]
                if candidate in entries:
                    word = candidate
                    break
            offset += len(word)
            if word in seen:
                continue
            seen.add(word)
            if word in entries:
                lines.extend(f"{word} [{reading}]: {definition}" for reading, definition in entries[word])
            else:
                lines.append(f"{word}: No CC-CEDICT entry found.")
    return "CC-CEDICT word definitions:\n" + "\n".join(lines)
