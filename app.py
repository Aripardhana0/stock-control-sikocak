from flask import Flask, render_template, request, jsonify
import sqlite3, os, json
from datetime import datetime
import qrcode

app = Flask(__name__)
DB_FILE = "stock.db"

# --- DB Helper ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS stock (
        kode TEXT PRIMARY KEY,
        nama TEXT,
        stok INTEGER DEFAULT 0,
        kategori TEXT,
        lokasi TEXT,
        terakhir_update TEXT
    )""")
    conn.commit()
    conn.close()

def query_db(query, params=(), one=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# --- ROUTES ---
@app.route("/")
def index():
    items = query_db("SELECT * FROM stock")
    return render_template("index.html", items=items)

@app.route("/generate", methods=["POST"])
def generate_qr():
    data = request.json
    kode, nama, jumlah, kategori, lokasi = data["kode"], data["nama"], int(data["jumlah"]), data["kategori"], data["lokasi"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_db("""INSERT INTO stock (kode, nama, stok, kategori, lokasi, terakhir_update)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(kode) DO UPDATE SET nama=?, stok=stok+?, kategori=?, lokasi=?, terakhir_update=?""",
             (kode, nama, jumlah, kategori, lokasi, timestamp, nama, jumlah, kategori, lokasi, timestamp))
    
    # generate QR
    os.makedirs("static/qr", exist_ok=True)
    qr_data = json.dumps({"kode": kode})
    img = qrcode.make(qr_data)
    img.save(f"static/qr/{kode}.png")

    return jsonify({"message": "QR berhasil dibuat", "qr_path": f"/static/qr/{kode}.png"})

@app.route("/update-stock", methods=["POST"])
def update_stock():
    data = request.json
    kode, jumlah, mode = data["kode"], int(data["jumlah"]), data["mode"]
    row = query_db("SELECT * FROM stock WHERE kode=?", (kode,), one=True)
    if not row:
        return jsonify({"error": "Barang tidak ditemukan"}), 404

    stok = row["stok"] + jumlah if mode == "masuk" else row["stok"] - jumlah
    if stok < 0:
        return jsonify({"error": "Stok tidak mencukupi"}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query_db("UPDATE stock SET stok=?, terakhir_update=? WHERE kode=?", (stok, timestamp, kode))
    return jsonify({"message": f"Stok {mode} berhasil", "stok_baru": stok})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
