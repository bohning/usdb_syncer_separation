"""Runner for demucs audio separation."""

import contextlib
import logging
from io import StringIO
from pathlib import Path

logger = logging.getLogger(__name__)


def separate_audio(
    input_file: str, output_dir: str, model: str = "htdemucs"
) -> tuple[str, str]:
    """Separates input_file into vocals and instrumental tracks.

    Returns absolute paths to (output_vocals, output_instrumental).

    Logs and progress bars from Demucs are suppressed
    """
    from demucs.api import Separator

    with contextlib.redirect_stdout(StringIO()), contextlib.redirect_stderr(StringIO()):
        # progress=False to suppress tqdm
        separator = Separator(model=model, progress=False)

        _origin, separated = separator.separate_audio_file(Path(input_file))

    vocals_tensor = separated.get("vocals")

    if vocals_tensor is None:
        raise RuntimeError("Demucs did not output a 'vocals' stem.")  # noqa: TRY003

    # Compute instrumental by summing the rest
    other_keys = [k for k in separated if k != "vocals"]
    if not other_keys:
        raise RuntimeError("Demucs did not output any non-vocal stems.")  # noqa: TRY003

    instrumental_tensor = separated[other_keys[0]].clone()
    for k in other_keys[1:]:
        instrumental_tensor += separated[k]

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    vocals_path = str(Path(output_dir) / "vocals.wav")
    instrumental_path = str(Path(output_dir) / "instrumental.wav")

    # separate_audio_file standardizes to the samplerate of the separator
    samplerate = separator.samplerate

    import torchaudio

    torchaudio.save(vocals_path, vocals_tensor, samplerate, backend="soundfile")
    torchaudio.save(instrumental_path, instrumental_tensor, samplerate, backend="soundfile")

    return vocals_path, instrumental_path
