
import argparse
import time
from pathlib import Path

import ctranslate2
from faster_whisper import WhisperModel


def select_device(preference: str):
    """Select CUDA if available, otherwise CPU."""
    if preference == "cpu":
        return "cpu", "int8"

    try:
        count = ctranslate2.get_cuda_device_count()
        if count < 1:
            raise RuntimeError("No CUDA device detected")

        types = ctranslate2.get_supported_compute_types("cuda")

        if "float16" in types:
            compute_type = "float16"
        elif "int8_float16" in types:
            compute_type = "int8_float16"
        elif "float32" in types:
            compute_type = "float32"
        else:
            raise RuntimeError("No suitable CUDA compute type")

        print(f"CUDA devices: {count}")
        print(f"CUDA compute types: {sorted(types)}")
        return "cuda", compute_type

    except (RuntimeError, OSError) as exc:
        if preference == "cuda":
            raise

        print(f"CUDA unavailable: {exc}")
        print("Falling back to CPU.")
        return "cpu", "int8"


def srt_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    secs, milliseconds = divmod(milliseconds, 1000)

    return (
        f"{hours:02}:{minutes:02}:{secs:02},"
        f"{milliseconds:03}"
    )


def transcribe(model, input_file: Path, mode: str):
    """Run transcription and fully consume its lazy generator."""

    options = {
        "task": "transcribe",
        "beam_size": 5,
        "vad_filter": True,
        "condition_on_previous_text": False,
    }

    if mode == "mixed":
        options.update({
            "language": None,
            "multilingual": True,
        })

    elif mode == "chinese":
        options.update({
            "language": "zh",
            "multilingual": False,
        })

    else:
        raise ValueError(f"Unknown mode: {mode}")

    segments, info = model.transcribe(
        str(input_file),
        **options,
    )

    return list(segments), info


def save_results(input_file, mode, segments):
    """Write UTF-8 text and SRT subtitle files."""

    stem = input_file.with_suffix("")
    txt_path = Path(f"{stem}.{mode}.txt")
    srt_path = Path(f"{stem}.{mode}.srt")

    with (
        txt_path.open("w", encoding="utf-8") as txt,
        srt_path.open("w", encoding="utf-8") as srt,
    ):
        for index, segment in enumerate(segments, 1):
            content = segment.text.strip()

            if not content:
                continue

            print(
                f"[{segment.start:7.2f} - "
                f"{segment.end:7.2f}] {content}"
            )

            txt.write(
                f"[{segment.start:.2f} - "
                f"{segment.end:.2f}] {content}\n"
            )

            srt.write(
                f"{index}\n"
                f"{srt_timestamp(segment.start)} --> "
                f"{srt_timestamp(segment.end)}\n"
                f"{content}\n\n"
            )

    return txt_path, srt_path


def main():
    parser = argparse.ArgumentParser(
        description="Mandarin/English transcription"
    )

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
        choices=["mixed", "chinese", "both"],
        default="both",
    )

    args = parser.parse_args()

    if not args.input_file.is_file():
        parser.error(
            f"Input file not found: {args.input_file}"
        )

    device, compute_type = select_device(args.device)

    print(f"\nInput:   {args.input_file}")
    print(f"Model:   {args.model}")
    print(f"Device:  {device}")
    print(f"Compute: {compute_type}")
    print(f"Mode:    {args.mode}\n")

    start_total = time.perf_counter()

    # Load model once and reuse it for both passes.
    try:
        model = WhisperModel(
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
        model = WhisperModel(
            args.model,
            device=device,
            compute_type=compute_type,
        )

    modes = (
        ["mixed", "chinese"]
        if args.mode == "both"
        else [args.mode]
    )

    for mode in modes:
        print(f"\n{'=' * 60}")
        print(f"TRANSCRIPTION MODE: {mode.upper()}")
        print(f"{'=' * 60}")

        start = time.perf_counter()

        try:
            segments, info = transcribe(
                model, args.input_file, mode
            )

        except (RuntimeError, OSError) as exc:
            if device != "cuda" or args.device == "cuda":
                raise

            print(f"CUDA inference failed: {exc}")
            print("Retrying on CPU...")

            del model
            device, compute_type = "cpu", "int8"

            model = WhisperModel(
                args.model,
                device=device,
                compute_type=compute_type,
            )

            segments, info = transcribe(
                model, args.input_file, mode
            )

        elapsed = time.perf_counter() - start

        txt_path, srt_path = save_results(
            args.input_file, mode, segments
        )

        print(f"\nDetected language: {info.language}")
        print(f"Audio duration: {info.duration:.2f} s")
        print(f"Processing time: {elapsed:.2f} s")
        print(f"Device used: {device}")

        if elapsed > 0:
            print(
                f"Speed ratio: "
                f"{info.duration / elapsed:.2f}x realtime"
            )

        print(f"TXT output: {txt_path}")
        print(f"SRT output: {srt_path}")

    total_elapsed = time.perf_counter() - start_total

    print(f"\n{'=' * 60}")
    print("TRANSCRIPTION COMPLETE")
    print(f"Total time: {total_elapsed:.2f} s")
    print(f"Final device: {device}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
