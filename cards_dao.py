import sqlite3


def connect_db(db_path):
    rv = sqlite3.connect(db_path, check_same_thread=False)
    rv.row_factory = sqlite3.Row
    return rv


class CardsDao:
    def __init__(self, db_path):
        self.connection = connect_db(db_path)

    def get_all(self):
        all_query = 'SELECT * FROM cards'
        cur = self.connection.execute(all_query)
        return cur.fetchall()

    def get_random_question(self):
        query = '''
                SELECT
                    id, front
                FROM cards
                WHERE
                    known = 0
                ORDER BY RANDOM()
                LIMIT 1
        '''
        cur = self.connection.execute(query)
        row = cur.fetchone()
        return row[0], row[1]

    def get_card_back_by_id(self, last_id):
        query = '''
                SELECT
                    back
                FROM cards
                WHERE
                    id = ?
                ORDER BY RANDOM()
                LIMIT 1
        '''
        cur = self.connection.execute(query, [last_id])
        row = cur.fetchone()
        return row[0]
