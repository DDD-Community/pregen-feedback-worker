from pregen.entity.word_error import WordError
from pregen.infrastructure.chat_gpt_client import ChatGptClient
from pregen.infrastructure.whisper_client import WhisperClient
from pregen.pojo.data.feedback_status import FeedbackStatus
from pregen.pojo.message.slide_message import SlideMessage
from pregen.repository.feedback_repository import FeedbackRepository
from pregen.repository.slide_repository import SlideRepository
from pregen.repository.word_error_repository import WordErrorRepository
from pregen.service.feedback_generator import FeedbackGenerator
from pregen.utils.environment import get_envs
from pregen.utils.logging import logger


class ScriptGenerator:
    def __init__(self):
        self.chat_gpt_client = ChatGptClient()
        self.whisper_client = WhisperClient()
        self.slide_repository = SlideRepository()
        self.word_error_repository = WordErrorRepository()
        self.feedback_generator = FeedbackGenerator()
        self.feedback_repository = FeedbackRepository()

    def generate(self, message: SlideMessage):
        slide_id = message.slideId
        is_finished = self.slide_repository.is_finished_practice(slide_id)
        practice_id = self.slide_repository.find_practice_id_by_slide_id(slide_id)

        if is_finished:
            self.feedback_repository.update_status(
                status=FeedbackStatus.IN_PROGRESS, practice_id=practice_id
            )

        logger.info(f"Start Audio Transcription with slide_id = `{slide_id}`")
        audio_file_path = get_envs().file["base_url"] + message.audioFilePath
        transcription_result = self.whisper_client.transcribe(audio_file_path)
        logger.info("End Audio Transcription")

        original_script = message.originalScript
        spoken_script = transcription_result.spoke_script
        practice_time = transcription_result.audio_duration

        self.slide_repository.update_script(
            slide_id=slide_id,
            practiced_script=spoken_script,
        )
        self.slide_repository.update_practice_time(
            practice_id=practice_id,
            practice_time=practice_time,
        )

        logger.info(f"Start Word Error Detection with slide_id = `{slide_id}`")
        error_detection_result = self.chat_gpt_client.call(
            original_script, spoken_script
        )
        logger.info("End Word Error Detection")

        for result in error_detection_result.results:
            start, end = self._interpolate_result(
                original_script, result.original_word, result.word_start_index
            )
            word_error = WordError(slide_id=slide_id, start_index=start, end_index=end)
            self.word_error_repository.save(word_error)

        if is_finished:
            logger.info(f"Start Feedback Generation with practice_id = `{practice_id}`")
            self.feedback_generator.generate(slide_id)

    @staticmethod
    def _interpolate_result(
        original_script: str, original_word: str, start_index_of_word: int
    ) -> tuple[int, int]:
        end_index_of_word = min(
            start_index_of_word + len(original_word), len(original_script)
        )

        if original_word == original_script[start_index_of_word:end_index_of_word]:
            corrected_start_index = start_index_of_word
            corrected_end_index = end_index_of_word
        else:
            if original_script.count(original_word) < 2 or len(original_word) > 10:
                corrected_start_index = original_script.find(original_word)
                corrected_end_index = corrected_start_index + len(original_word)
            else:
                sliding_window_start = max(0, start_index_of_word - 40)
                sliding_window_end = min(end_index_of_word + 40, len(original_script))

                target = original_script[sliding_window_start:sliding_window_end]

                start_index_of_word_in_target = target.find(original_word)
                if start_index_of_word_in_target == -1:
                    corrected_start_index = 0
                    corrected_end_index = 0
                else:
                    corrected_start_index = (
                        sliding_window_start + start_index_of_word_in_target
                    )
                    corrected_end_index = min(
                        corrected_start_index + len(original_word), len(original_script)
                    )

        return corrected_start_index, corrected_end_index
