from flask import Flask, request, Response
import sqlite3, html

app = Flask(__name__)
DB = "training.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, role TEXT)")
    cur.execute("DELETE FROM users")
    cur.executemany("INSERT INTO users VALUES (?, ?, ?)",
                    [(1,"alice","student"),(2,"bob","admin"),(3,"charlie","student")])
    cur.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT)")
    con.commit(); con.close()

@app.route("/")
def home():
    return """<h1>OWASP Training Sandbox</h1>
    <ul><li>/search?q=alice — SQLi lab</li>
    <li>/reflect?name=Alice — reflected XSS lab</li>
    <li>/comment — stored XSS lab</li>
    <li>/user?id=1 — BOLA/IDOR lab</li></ul>
    <p>Authorized localhost training only.</p>"""

@app.route("/search")
def search():
    q = request.args.get("q","")
    # INTENTIONALLY VULNERABLE: SQL string concatenation.
    sql = "SELECT id, username, role FROM users WHERE username = '" + q + "'"
    con = sqlite3.connect(DB)
    try:
        rows = con.execute(sql).fetchall()
        body = "<h2>Search results</h2><pre>" + html.escape(repr(rows)) + "</pre>"
    except Exception as e:
        body = "<h2>Database error</h2><pre>" + html.escape(str(e)) + "</pre>"
    con.close()
    return body

@app.route("/reflect")
def reflect():
    name = request.args.get("name","")
    # INTENTIONALLY VULNERABLE: raw HTML reflection.
    return Response(f"<h2>Hello {name}</h2>", mimetype="text/html")

@app.route("/comment", methods=["GET","POST"])
def comment():
    con = sqlite3.connect(DB)
    if request.method == "POST":
        body = request.form.get("body","")
        con.execute("INSERT INTO comments(body) VALUES (?)",(body,))
        con.commit()
    rows = con.execute("SELECT id, body FROM comments ORDER BY id DESC").fetchall()
    con.close()
    items = "".join(f"<li>{body}</li>" for _,body in rows)  # INTENTIONALLY UNSAFE
    return f"""<h2>Comments</h2>
    <form method="post"><input name="body"><button>Save</button></form>
    <ul>{items}</ul>"""

@app.route("/user")
def user():
    uid = request.args.get("id","1")
    con = sqlite3.connect(DB)
    row = con.execute("SELECT id, username, role FROM users WHERE id = ?",(uid,)).fetchone()
    con.close()
    if not row: return "User not found",404
    # INTENTIONALLY VULNERABLE: no authorization check.
    return f"<h2>User profile</h2><pre>{html.escape(repr(row))}</pre>"

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
