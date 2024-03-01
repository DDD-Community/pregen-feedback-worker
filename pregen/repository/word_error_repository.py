from pregen.entity.word_error import WordError
from pregen.utils.connection_factory import ConnectionFactory


class WordErrorRepository:
    def __init__(self):
        self.connection_factory = ConnectionFactory()

    def save(self, word_error: WordError):
        with self.connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO word_error (slide_id, start_index, end_index) VALUES (%s, %s, %s)""",
                    (word_error.slide_id, word_error.start_index, word_error.end_index),
                )

                conn.commit()
