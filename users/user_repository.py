from app.db import get_connection

class UserRepository:

    @staticmethod
    def criar(email):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO users (email)
        VALUES (%s)
        ON CONFLICT (email) DO NOTHING;
        """, (email,))

        conn.commit()
        cur.close()
        conn.close()
