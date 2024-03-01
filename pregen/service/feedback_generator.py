import re
from math import fabs, pow

from pregen.infrastructure.chat_gpt_client import ChatGptClient
from pregen.repository.feedback_repository import FeedbackRepository
from pregen.repository.slide_repository import SlideRepository
from pregen.repository.word_error_repository import WordErrorRepository
from pregen.utils.logging import logger


def calculate_memorization_score(
    matching_word_count: int, total_word_count: int
) -> float:
    return matching_word_count / total_word_count


def calculate_speed_score(
    total_word_count: int, actual_presentation_time: int
) -> float:
    presentation_speed = total_word_count / actual_presentation_time
    return max(
        0.0,
        min(
            -(1 / 150) * pow(presentation_speed, 2) + (5 / 3) * presentation_speed, 100
        ),
    )


def calculate_time_score(
    set_presentation_time: int, actual_presentation_time: int
) -> float:
    return max(
        0.0, (60 * 10) - fabs(set_presentation_time - actual_presentation_time)
    ) / (60 * 10)


def calculate_total_score(
    memorization_score: float, speed_score: float, time_score: float
) -> float:
    return (memorization_score * 0.7) + (speed_score * 0.2) + (time_score * 0.1)


class FeedbackGenerator:
    def __init__(self):
        self.chatgpt_client = ChatGptClient()
        self.word_error_repository = WordErrorRepository()
        self.slide_repository = SlideRepository()
        self.feedback_repository = FeedbackRepository()

    def generate(self, slide_id: int):
        (
            practice_id,
            script,
            practiced_script,
            time_limit,
            practice_time,
        ) = self.slide_repository.find_practice_by_slide_id(slide_id)

        total_word_count = len(re.findall(r"\w+", script))
        matching_word_count = max(
            0,
            total_word_count
            - self.slide_repository.count_word_errors_of_practice(practice_id),
        )

        mem_score = calculate_memorization_score(
            matching_word_count=matching_word_count, total_word_count=total_word_count
        )
        speed_score = calculate_speed_score(
            total_word_count=total_word_count, actual_presentation_time=practice_time
        )
        time_score = calculate_time_score(
            set_presentation_time=time_limit, actual_presentation_time=practice_time
        )
        total_score = calculate_total_score(
            memorization_score=mem_score, speed_score=speed_score, time_score=time_score
        )

        report = f"""
========== End Feedback Generation. Report ==========
memorization_score = {mem_score}
speed_score = {speed_score}
time_score = {time_score}
total_score = {total_score}
====================================================="""

        logger.info(report)

        self.feedback_repository.update_scores(
            memorization_score=mem_score,
            speed_score=speed_score,
            time_score=time_score,
            total_score=total_score,
            practice_id=practice_id,
        )
