from flask import Flask, request, Response, abort
import sqlite3, html

app = Flask(__name__)
DB = "training.db"

@app.route("/search")
def secure_search():
    q = request.args.get("q","")
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id, username, role FROM users WHERE username = ?", (q,)
    ).fetchall()
    con.close()
    return "<pre>" + html.escape(repr(rows)) + "</pre>"

@app.route("/reflect")
def secure_reflect():
    name = request.args.get("name","")
    return Response(
        f"<h2>Hello {html.escape(name, quote=True)}</h2>",
        mimetype="text/html"
    )

@app.route("/user")
def secure_user():
    current_user_id = 1
    requested_id = request.args.get("id","1")
    if requested_id != str(current_user_id):
        abort(403, description="Authorization check failed")
    con = sqlite3.connect(DB)
    row = con.execute(
        "SELECT id, username, role FROM users WHERE id = ?", (requested_id,)
    ).fetchone()
    con.close()
    if not row: abort(404)
    return "<pre>" + html.escape(repr(row)) + "</pre>"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
