from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)

CORS(app, origins=["https://webminutes.it.com"])

DB_HOST = "localhost"
DB_USER = "webmyqog_admin"
DB_PASSWORD = "7c}D5hXTpqG+"
DB_NAME = "webmyqog_webminutes"


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def home():
    return "WebMinutes API running 🚀"


@app.route("/api")
def api():
    return jsonify({"message": "API working"})


@app.route("/db-test")
def db_test():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        conn.close()
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users")
def get_users():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM test_table")
            rows = cursor.fetchall()
        conn.close()
        return jsonify({"data": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Todos
# ---------------------------------------------------------------------------

@app.route("/todos", methods=["GET"])
def list_todos():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, completed, created_at, updated_at FROM todos ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
        conn.close()
        for row in rows:
            row["completed"] = bool(row["completed"])
            if row.get("created_at"):
                row["created_at"] = row["created_at"].isoformat()
            if row.get("updated_at"):
                row["updated_at"] = row["updated_at"].isoformat()
        return jsonify({"data": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, completed, created_at, updated_at FROM todos WHERE id = %s",
                (todo_id,),
            )
            row = cursor.fetchone()
        conn.close()
        if row is None:
            return jsonify({"error": "Todo not found"}), 404
        row["completed"] = bool(row["completed"])
        if row.get("created_at"):
            row["created_at"] = row["created_at"].isoformat()
        if row.get("updated_at"):
            row["updated_at"] = row["updated_at"].isoformat()
        return jsonify({"data": row})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/todos", methods=["POST"])
def create_todo():
    body = request.get_json(silent=True) or {}
    title = (body.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO todos (title, completed) VALUES (%s, 0)", (title,)
            )
            new_id = cursor.lastrowid
            conn.commit()
            cursor.execute(
                "SELECT id, title, completed, created_at, updated_at FROM todos WHERE id = %s",
                (new_id,),
            )
            row = cursor.fetchone()
        conn.close()
        row["completed"] = bool(row["completed"])
        if row.get("created_at"):
            row["created_at"] = row["created_at"].isoformat()
        if row.get("updated_at"):
            row["updated_at"] = row["updated_at"].isoformat()
        return jsonify({"data": row}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    body = request.get_json(silent=True) or {}
    fields = {}
    if "title" in body:
        title = (body["title"] or "").strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        fields["title"] = title
    if "completed" in body:
        fields["completed"] = 1 if body["completed"] else 0
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [todo_id]
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                f"UPDATE todos SET {set_clause} WHERE id = %s", values
            )
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({"error": "Todo not found"}), 404
            conn.commit()
            cursor.execute(
                "SELECT id, title, completed, created_at, updated_at FROM todos WHERE id = %s",
                (todo_id,),
            )
            row = cursor.fetchone()
        conn.close()
        row["completed"] = bool(row["completed"])
        if row.get("created_at"):
            row["created_at"] = row["created_at"].isoformat()
        if row.get("updated_at"):
            row["updated_at"] = row["updated_at"].isoformat()
        return jsonify({"data": row})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({"error": "Todo not found"}), 404
            conn.commit()
        conn.close()
        return jsonify({"message": "Todo deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)