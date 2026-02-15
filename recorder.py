"""Audio recording with sounddevice (16kHz, mono, WAV)."""

import io
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16_000  # 16 kHz - optimal for speech
CHANNELS = 1  # Mono
DTYPE = "int16"


class Recorder:
    """Toggle-based audio recorder.

    Usage:
        recorder = Recorder()
        recorder.start()   # Start recording
        ...
        audio_bytes = recorder.stop()  # Stop recording, returns WAV bytes
    """

    def __init__(self) -> None:
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        """Starts audio recording."""
        with self._lock:
            if self._recording:
                return
            self._frames = []
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._recording = True

    def stop(self) -> bytes | None:
        """Stops recording and returns the WAV data as bytes.

        Returns:
            WAV file as bytes, or None if no recording was active.
        """
        with self._lock:
            if not self._recording or self._stream is None:
                return None

            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._recording = False

            if not self._frames:
                return None

            # Concatenate all frames
            audio_data = np.concatenate(self._frames, axis=0)
            self._frames = []

        # Convert to WAV bytes (in-memory)
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        buffer.seek(0)
        return buffer.read()

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: object,
        status: sd.CallbackFlags,
    ) -> None:
        """Audio stream callback -- collects frames."""
        self._frames.append(indata.copy())
