"""Select the inference device and numeric precision."""

from .runtime import configure_cuda_libraries

def select_device(preference: str):
    """Select CUDA if available, otherwise CPU."""
    if preference == "cpu":
        return "cpu", "int8"

    configure_cuda_libraries()
    import ctranslate2

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


