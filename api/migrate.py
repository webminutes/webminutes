import sys
import pymysql

DB_HOST = "127.0.0.1"
DB_USER = "webmyqog_admin"
DB_PASSWORD = "7c}D5hXTpqG+"
DB_NAME = "webmyqog_webminutes"

# ssh -f webmyqog@server903.web-hosting.com -p21098 -L 3306:127.0.0.1:3306 -N       8AWX3n4ox123
def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )


def up():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                title       VARCHAR(255) NOT NULL,
                completed   TINYINT(1)   NOT NULL DEFAULT 0,
                created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                  ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conn.commit()
    conn.close()
    print("Migration UP complete — todos table created.")


def down():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS todos")
        conn.commit()
    conn.close()
    print("Migration DOWN complete — todos table dropped.")


if __name__ == "__main__":
    commands = {"up": up, "down": down}
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd not in commands:
        print(f"Usage: python migrate.py [{'|'.join(commands)}]")
        sys.exit(1)
    commands[cmd]()
