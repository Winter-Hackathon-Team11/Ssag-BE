from sqlalchemy import text
from db.database import engine

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ DB 연결 성공:", result.scalar())
    except Exception as e:
        print("❌ DB 연결 실패")
        print(e)

if __name__ == "__main__":
    test_connection()