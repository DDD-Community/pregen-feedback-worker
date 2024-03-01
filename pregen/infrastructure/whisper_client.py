import audioread
from audioread.macca import ExtAudioFile
from openai import OpenAI

from pregen.pojo.response.transcription_response import TranscriptionResponse
from pregen.utils.environment import get_envs
from pregen.utils.singleton import singleton


@singleton
class WhisperClient:
    def __init__(self):
        self.client = OpenAI(**get_envs().openai["transcript"])

    def transcribe(self, audio_path: str) -> TranscriptionResponse:
        with audioread.audio_open(audio_path) as f:
            f: ExtAudioFile
            audio_duration = f.duration

            audio_file = open(audio_path, "rb")

            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )

            audio_file.close()

        return TranscriptionResponse(
            spoke_script=transcription.text,
            word_count=len(transcription.model_extra["words"]),
            audio_duration=audio_duration,
        )
