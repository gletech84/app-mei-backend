from backend.database.db import get_conn


class UserRepository:

    @staticmethod
    def criar(email):
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (email)
            VALUES (%s)
            ON CONFLICT (email) DO NOTHING;
        """, (email,))

        conn.commit()

        cur.close()
        conn.close()
