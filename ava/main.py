import tempfile
import wave

import numpy as np
import pyaudio
import whisper

# Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
SILENCE_THRESHOLD = 500  # Adjust this threshold based on your environment
SILENCE_DURATION = 2  # Duration of silence in seconds to trigger stopping the recording

model = whisper.load_model("large")


def _is_silent(data_chunk, threshold=SILENCE_THRESHOLD):
    """Returns 'True' if below the silence threshold."""
    audio_data = np.frombuffer(data_chunk, dtype=np.int16)
    return np.abs(audio_data).mean() < threshold


def _record_audio(output_file: str, silence_duration: int = SILENCE_DURATION):
    """Record audio from the microphone and save it to a WAV file, stopping on silence detection."""
    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    print("Recording...")

    frames = []
    silence_count = 0
    silence_limit = int(RATE / CHUNK * silence_duration)

    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        if _is_silent(data):
            silence_count += 1
        else:
            silence_count = 0

        if silence_count > silence_limit:
            break

    print("Finished recording due to silence detection.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(output_file, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


def _get_transcribe(audio: str, language: str = "en"):
    return model.transcribe(audio=audio, language=language)


def _main():
    with tempfile.TemporaryDirectory() as tmpdirname:
        audio_path = f"{tmpdirname}/audio.wav"
        _record_audio(output_file=audio_path, silence_duration=SILENCE_DURATION)
        result = _get_transcribe(audio=audio_path)
        if result:
            print("-" * 50)
            print(result.get("text", "No transcription text found."))
        else:
            print("Transcription failed.")


if __name__ == "__main__":
    _main()
