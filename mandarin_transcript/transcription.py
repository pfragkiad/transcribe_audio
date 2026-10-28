"""Whisper model construction and transcription options."""

from pathlib import Path

from .runtime import configure_cuda_libraries


def load_model(model_name, device, compute_type):
    """Load the optional inference backend only when it is needed."""
    configure_cuda_libraries()
    from faster_whisper import WhisperModel

    return WhisperModel(model_name, device=device, compute_type=compute_type)


def transcribe(model, input_file: Path, mode: str):
    """Run transcription and fully consume its lazy generator."""

    options = {
        "task": "transcribe",
        "beam_size": 5,
        "vad_filter": True,
        "condition_on_previous_text": False,
    }

    if mode == "mixed":
        options.update(
            {
                "language": None,
                "multilingual": True,
            }
        )

    elif mode == "chinese":
        options.update(
            {
                "language": "zh",
                "multilingual": False,
            }
        )

    else:
        raise ValueError(f"Unknown mode: {mode}")

    segments, info = model.transcribe(
        str(input_file),
        **options,
    )

    return list(segments), info


