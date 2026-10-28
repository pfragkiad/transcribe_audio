import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from mandarin_transcript.output import save_results
from mandarin_transcript.pinyin import annotate_hanzi, hanzi_to_pinyin


class PinyinTests(unittest.TestCase):
    def test_word_annotations_preserve_mixed_text(self):
        self.assertEqual(
            annotate_hanzi("你好世界，English 123!\n谢谢。"),
            "你好(nǐ hǎo) 世界(shì jiè)，English 123!\n谢谢(xiè xiè)。",
        )
        self.assertEqual(annotate_hanzi(""), "")
        self.assertEqual(annotate_hanzi("Hello!"), "Hello!")

    def test_dictionary_tones_without_sandhi(self):
        self.assertEqual(hanzi_to_pinyin("你好"), "nǐ hǎo")

    def test_phrase_reading_and_traditional_hanzi(self):
        self.assertEqual(hanzi_to_pinyin("重庆"), "chóng qìng")
        self.assertEqual(hanzi_to_pinyin("中國"), "zhōng guó")

    def test_preserves_non_hanzi(self):
        self.assertEqual(
            hanzi_to_pinyin("你好，English 123!\n谢谢。"),
            "nǐ hǎo，English 123!\nxiè xiè。",
        )
        self.assertEqual(hanzi_to_pinyin(""), "")
        self.assertEqual(hanzi_to_pinyin("Hello, world!"), "Hello, world!")

    def test_each_configuration_writes_exactly_one_file(self):
        segment = SimpleNamespace(start=1.25, end=3.5, text="你好，world!")
        for mode in ("mixed", "chinese"):
            for output_format in ("txt", "srt"):
                for pinyin in (False, True):
                    with self.subTest(mode=mode, format=output_format, pinyin=pinyin):
                        with tempfile.TemporaryDirectory() as directory:
                            root = Path(directory)
                            with contextlib.redirect_stdout(io.StringIO()):
                                path = save_results(
                                    root / "lesson.mp3", mode, [segment],
                                    output_dir=root / "output",
                                    output_format=output_format,
                                    text_transform=annotate_hanzi if pinyin else None,
                                )
                            self.assertEqual(list(root.rglob("*.*")), [path])
                            self.assertEqual(path, root / "output" / f"lesson.{output_format}")
                            content = "你好(nǐ hǎo)，world!" if pinyin else segment.text
                            expected = (
                                f"[1.25 - 3.50] {content}\n" if output_format == "txt" else
                                f"1\n00:00:01,250 --> 00:00:03,500\n{content}\n\n"
                            )
                            self.assertEqual(path.read_text(encoding="utf-8"), expected)
                            self.assertEqual(segment.text, "你好，world!")


if __name__ == "__main__":
    unittest.main()
