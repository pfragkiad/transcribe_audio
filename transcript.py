"""Mandarin/English transcription CLI and main workflow."""

import argparse
import time
from pathlib import Path

from mandarin_transcript.device import select_device
from mandarin_transcript.output import save_results
from mandarin_transcript.pinyin import annotate_hanzi, hanzi_to_pinyin
from mandarin_transcript.runtime import configure_utf8_stdio
from mandarin_transcript.transcription import load_model, transcribe


def main():
    configure_utf8_stdio()

    parser = argparse.ArgumentParser(description="Mandarin/English transcription")

    parser.add_argument(
        "input_file",
        type=Path,
        help="Local audio or video file",
    )

    parser.add_argument(
        "--model",
        default="large-v3",
        help="Whisper model (default: large-v3)",
    )

    parser.add_argument(
        "--device",
        choices=["auto", "cuda", "cpu"],
        default="auto",
    )

    parser.add_argument(
        "--mode",
        choices=["mixed", "chinese"],
        default="mixed",
    )

    parser.add_argument(
        "--pinyin",
        action="store_true",
        help="Annotate Chinese words with Pinyin in the single output file",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Root directory for organized output files (default: output)",
    )

    parser.add_argument("--format", choices=["txt", "srt"], default="txt",
                        help="Single output format (default: txt)")

    args = parser.parse_args()

    if not args.input_file.is_file():
        parser.error(f"Input file not found: {args.input_file}")

    if args.pinyin:
        try:
            hanzi_to_pinyin("")
            annotate_hanzi("")
        except ModuleNotFoundError as exc:
            if exc.name not in {"pypinyin", "jieba"}:
                raise
            parser.error("Pinyin support requires pypinyin and jieba: pip install -r requirements.txt")

    device, compute_type = select_device(args.device)

    print(f"\nInput:   {args.input_file}")
    print(f"Model:   {args.model}")
    print(f"Device:  {device}")
    print(f"Compute: {compute_type}")
    print(f"Mode:    {args.mode}\n")

    start_total = time.perf_counter()

    # Load the model for the selected transcription pass.
    try:
        model = load_model(
            args.model,
            device=device,
            compute_type=compute_type,
        )

    except (RuntimeError, OSError) as exc:
        if device != "cuda" or args.device == "cuda":
            raise

        print(f"CUDA initialization failed: {exc}")
        print("Loading model on CPU...")

        device, compute_type = "cpu", "int8"
        model = load_model(
            args.model,
            device=device,
            compute_type=compute_type,
        )

    print(f"\n{'=' * 60}")
    print(f"TRANSCRIPTION MODE: {args.mode.upper()}")
    print(f"{'=' * 60}")

    start = time.perf_counter()

    try:
        segments, info = transcribe(model, args.input_file, args.mode)

    except (RuntimeError, OSError) as exc:
        if device != "cuda" or args.device == "cuda":
            raise

        print(f"CUDA inference failed: {exc}")
        print("Retrying on CPU...")

        del model
        device, compute_type = "cpu", "int8"

        model = load_model(
            args.model,
            device=device,
            compute_type=compute_type,
        )

        segments, info = transcribe(model, args.input_file, args.mode)

    elapsed = time.perf_counter() - start

    output_path = save_results(
        args.input_file, args.mode, segments,
        output_dir=args.output_dir,
        output_format=args.format,
        text_transform=annotate_hanzi if args.pinyin else None,
    )

    print(f"\nDetected language: {info.language}")
    print(f"Audio duration: {info.duration:.2f} s")
    print(f"Processing time: {elapsed:.2f} s")
    print(f"Device used: {device}")

    if elapsed > 0:
        print(f"Speed ratio: " f"{info.duration / elapsed:.2f}x realtime")

    print(f"Output: {output_path}")

    total_elapsed = time.perf_counter() - start_total

    print(f"\n{'=' * 60}")
    print("TRANSCRIPTION COMPLETE")
    print(f"Total time: {total_elapsed:.2f} s")
    print(f"Final device: {device}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
