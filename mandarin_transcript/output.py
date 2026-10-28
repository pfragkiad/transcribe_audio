"""Serialize original transcript text and subtitle timing."""

from pathlib import Path
from collections.abc import Callable

def srt_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    secs, milliseconds = divmod(milliseconds, 1000)

    return f"{hours:02}:{minutes:02}:{secs:02}," f"{milliseconds:03}"


def save_results(
    input_file, mode, segments, *, output_dir: Path = Path("output"),
    output_format: str = "txt", text_transform: Callable[[str], str] | None = None,
):
    """Write exactly one UTF-8 file without modifying source segments."""
    if output_format not in {"txt", "srt"}:
        raise ValueError(f"Unknown output format: {output_format}")
    if mode not in {"mixed", "chinese"}:
        raise ValueError(f"Unknown transcription mode: {mode}")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    name = Path(input_file).stem
    output_path = destination / f"{name}.{output_format}"

    with output_path.open("w", encoding="utf-8") as output:
        index = 0
        for segment in segments:
            content = segment.text.strip()
            if not content:
                continue
            if text_transform is not None:
                content = text_transform(content)
            index += 1
            print(f"[{segment.start:7.2f} - {segment.end:7.2f}] {content}")
            if output_format == "txt":
                output.write(f"[{segment.start:.2f} - {segment.end:.2f}] {content}\n")
            else:
                output.write(
                    f"{index}\n"
                    f"{srt_timestamp(segment.start)} --> {srt_timestamp(segment.end)}\n"
                    f"{content}\n\n"
                )
    return output_path
