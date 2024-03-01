from pregen.pojo.data.feedback_status import FeedbackStatus
from pregen.utils.connection_factory import ConnectionFactory


class FeedbackRepository:
    def __init__(self):
        self.connection_factory = ConnectionFactory()

    def update_status(self, status: FeedbackStatus, practice_id: int):
        with self.connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE feedback SET status = %s WHERE practice_id = %s""",
                    (status.name, practice_id),
                )

                conn.commit()

    def update_scores(
        self,
        memorization_score: float,
        speed_score: float,
        time_score: float,
        total_score: float,
        practice_id: int,
    ):
        with self.connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE feedback
                        SET memorization_score = %s, speed_score = %s, time_score = %s, total_score = %s, status = %s
                        WHERE practice_id = %s""",
                    (
                        memorization_score,
                        speed_score,
                        time_score,
                        total_score,
                        FeedbackStatus.DONE.name,
                        practice_id,
                    ),
                )

                conn.commit()
