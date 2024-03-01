from pregen.utils.connection_factory import ConnectionFactory


class SlideRepository:
    def __init__(self):
        self.connection_factory = ConnectionFactory()

    def update_script(self, slide_id: int, practiced_script: str):
        with self.connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE slide SET practiced_script = %s WHERE slide_id = %s""",
                    (practiced_script, slide_id),
                )

                conn.commit()

    def update_practice_time(self, practice_id: int, practice_time: int):
        with self.connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE practice SET practice_time = practice_time + %s WHERE practice_id = %s""",
                    (practice_time, practice_id),
                )

                conn.commit()

    def is_finished_practice(self, slide_id: int) -> bool:
        with self.connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    (
                        """SELECT p.practice_id
                        FROM practice p
                        JOIN slide s ON p.practice_id = s.practice_id
                        WHERE s.slide_id = %s AND s.status != 'DONE'"""
                    ),
                    (slide_id,),
                )

                results = cursor.fetchall()

        return len(results) == 0

    def find_practice_id_by_slide_id(self, slide_id: int) -> int:
        with self.connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT p.practice_id
                        FROM practice p
                        JOIN slide s ON p.practice_id = s.practice_id
                        WHERE s.slide_id = %s""",
                    (slide_id,),
                )

                practice_id = cursor.fetchone()[0]

        return practice_id

    def find_practice_by_slide_id(self, slide_id: int) -> tuple:
        with self.connection_factory.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT p.practice_id, p.time_limit, p.practice_time
                        FROM practice p
                        JOIN slide s ON p.practice_id = s.practice_id
                        WHERE s.slide_id = %s""",
                    (slide_id,),
                )

                practice_id, time_limit, practice_time = cursor.fetchone()

                cursor.execute(
                    """SELECT GROUP_CONCAT(script separator ' '),
                                GROUP_CONCAT(practiced_script separator ' ')
                        FROM slide s
                        WHERE s.practice_id = %s""",
                    (practice_id,),
                )

                original_script, practiced_script = cursor.fetchone()

        return practice_id, original_script, practiced_script, time_limit, practice_time

    def count_word_errors_of_practice(self, practice_id: int):
        with self.connection_factory.get_connection() as conn:
            if conn and conn.is_connected():
                with conn.cursor() as cursor:
                    cursor.execute(
                        """SELECT p.practice_id
                            FROM practice p
                            JOIN slide s ON p.practice_id = s.practice_id
                            JOIN word_error we ON s.slide_id = we.slide_id
                            WHERE p.practice_id = %s""",
                        (practice_id,),
                    )

                    result = cursor.fetchall()

        return len(result)
