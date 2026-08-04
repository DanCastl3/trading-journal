"""
Backend de la Bitácora FOTSI (Magalà)
--------------------------------------
Servidor Flask que conecta con MySQL y sirve el frontend.

Antes de correrlo:
  1. Instala las dependencias:  pip install -r requirements.txt
  2. Crea la base de datos ejecutando schema.sql en tu MySQL (ver README.md)
  3. Ajusta los datos de conexión en DB_CONFIG más abajo si es necesario
  4. Corre:  python server.py
  5. Abre en el navegador:  http://localhost:5000
"""

import os
import time
import base64
import uuid
from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
from mysql.connector import pooling

# ============== CONFIGURACIÓN DE LA BASE DE DATOS ==============
# La contraseña NO va escrita aquí — se lee de una variable de entorno,
# para poder subir este código a GitHub sin exponer tus credenciales.
# Antes de correr el servidor, define la variable DB_PASSWORD con TU contraseña real:
#   Windows (PowerShell):  $env:DB_PASSWORD="tu_contraseña_de_mysql"
#   Windows (CMD):         set DB_PASSWORD=tu_contraseña_de_mysql
#   Mac/Linux:              export DB_PASSWORD=tu_contraseña_de_mysql
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": "bitacora_fotsi",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder=None)

cnx_pool = pooling.MySQLConnectionPool(pool_name="fotsi_pool", pool_size=5, **DB_CONFIG)


def get_conn():
    return cnx_pool.get_connection()


# ============== SERVIR EL FRONTEND ==============
@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "diario_magala.html")


@app.route("/uploads/<trade_id>/<filename>")
def serve_upload(trade_id, filename):
    folder = os.path.join(UPLOAD_DIR, trade_id)
    return send_from_directory(folder, filename)


# ============== HELPERS ==============
def trade_row_to_dict(row, images):
    return {
        "id": row["id"],
        "strategy": row.get("strategy") or "fotsi",
        "date": row["date"].isoformat() if row["date"] else "",
        "pair": row["pair"] or "",
        "tf": row["tf"] or "",
        "broker": row["broker"] or "Saxo",
        "timeEntry": row["time_entry"] or "",
        "timeTp1": row["time_tp1"] or "",
        "timeTp2": row["time_tp2"] or "",
        "dir": row["dir"] or "",
        "divFuerte": row["div_fuerte"] or "",
        "divDebil": row["div_debil"] or "",
        "atr": row["atr"] or "",
        "sl": row["sl"] or "",
        "entry": row["entry_price"] or "",
        "ema50": row["ema50"] or "",
        "ema100": row["ema100"] or "",
        "close1": row["close1"] or "",
        "close2": row["close2"] or "",
        "stopAdjust": row.get("stop_adjust") or "",
        "smaTrendOk": row.get("sma_trend_ok") or "",
        "avgPctChange": row.get("avg_pct_change") or "",
        "exitReason": row.get("exit_reason") or "",
        "capital": row["capital"] or "",
        "risk": row["risk_pct"] or "2",
        "status": row["status"] or "open",
        "tp1": row["tp1_desc"] or "",
        "tp2": row["tp2_desc"] or "",
        "pnl": "" if row["pnl"] is None else str(row["pnl"]),
        "breakeven": row["breakeven"] or "no",
        "sesion": row["sesion"] or "",
        "notes": row["notes"] or "",
        "createdAt": row["created_at"] or 0,
        "images": images,
    }


# ============== API: TRADES ==============
@app.route("/api/trades", methods=["GET"])
def list_trades():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM trades ORDER BY created_at DESC")
    rows = cur.fetchall()

    cur2 = conn.cursor(dictionary=True)
    cur2.execute("SELECT * FROM trade_images")
    all_images = cur2.fetchall()
    images_by_trade = {}
    for img in all_images:
        images_by_trade.setdefault(img["trade_id"], []).append({
            "name": img["original_name"],
            "url": f"/uploads/{img['trade_id']}/{img['filename']}"
        })

    result = [trade_row_to_dict(r, images_by_trade.get(r["id"], [])) for r in rows]
    cur.close(); cur2.close(); conn.close()
    return jsonify(result)


@app.route("/api/trades", methods=["POST"])
def create_trade():
    data = request.get_json(force=True)
    trade_id = data.get("id") or f"t{int(time.time()*1000)}{uuid.uuid4().hex[:6]}"
    created_at = data.get("createdAt") or int(time.time()*1000)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO trades (id, strategy, date, pair, tf, broker, time_entry, time_tp1, time_tp2,
            dir, div_fuerte, div_debil, atr, sl, entry_price, ema50, ema100, close1, close2, stop_adjust,
            sma_trend_ok, avg_pct_change, exit_reason,
            capital, risk_pct, status, tp1_desc, tp2_desc, pnl, breakeven, sesion, notes, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        trade_id, data.get("strategy","fotsi"), data.get("date") or None, data.get("pair"), data.get("tf"), data.get("broker","Saxo"),
        data.get("timeEntry"), data.get("timeTp1"), data.get("timeTp2"), data.get("dir"),
        data.get("divFuerte"), data.get("divDebil"), data.get("atr"), data.get("sl"), data.get("entry"),
        data.get("ema50"), data.get("ema100"), data.get("close1"), data.get("close2"), data.get("stopAdjust"),
        data.get("smaTrendOk"), data.get("avgPctChange"), data.get("exitReason"),
        data.get("capital"), data.get("risk","2"), data.get("status","open"),
        data.get("tp1"), data.get("tp2"),
        data.get("pnl") if data.get("pnl") not in ("", None) else None,
        data.get("breakeven","no"), data.get("sesion"), data.get("notes"), created_at
    ))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"id": trade_id, "ok": True})


@app.route("/api/trades/<trade_id>", methods=["PUT"])
def update_trade(trade_id):
    data = request.get_json(force=True)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE trades SET strategy=%s, date=%s, pair=%s, tf=%s, broker=%s, time_entry=%s, time_tp1=%s, time_tp2=%s,
            dir=%s, div_fuerte=%s, div_debil=%s, atr=%s, sl=%s, entry_price=%s, ema50=%s, ema100=%s,
            close1=%s, close2=%s, stop_adjust=%s, sma_trend_ok=%s, avg_pct_change=%s, exit_reason=%s,
            capital=%s, risk_pct=%s, status=%s, tp1_desc=%s, tp2_desc=%s,
            pnl=%s, breakeven=%s, sesion=%s, notes=%s
        WHERE id=%s
    """, (
        data.get("strategy","fotsi"), data.get("date") or None, data.get("pair"), data.get("tf"), data.get("broker","Saxo"),
        data.get("timeEntry"), data.get("timeTp1"), data.get("timeTp2"), data.get("dir"),
        data.get("divFuerte"), data.get("divDebil"), data.get("atr"), data.get("sl"), data.get("entry"),
        data.get("ema50"), data.get("ema100"), data.get("close1"), data.get("close2"), data.get("stopAdjust"),
        data.get("smaTrendOk"), data.get("avgPctChange"), data.get("exitReason"),
        data.get("capital"), data.get("risk","2"), data.get("status","open"),
        data.get("tp1"), data.get("tp2"),
        data.get("pnl") if data.get("pnl") not in ("", None) else None,
        data.get("breakeven","no"), data.get("sesion"), data.get("notes"),
        trade_id
    ))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"ok": True})


@app.route("/api/trades/<trade_id>", methods=["DELETE"])
def delete_trade(trade_id):
    # Borra también las imágenes físicas del disco
    folder = os.path.join(UPLOAD_DIR, trade_id)
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))
        os.rmdir(folder)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM trades WHERE id=%s", (trade_id,))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"ok": True})


# ============== API: IMÁGENES ==============
@app.route("/api/upload/<trade_id>", methods=["POST"])
def upload_images(trade_id):
    folder = os.path.join(UPLOAD_DIR, trade_id)
    os.makedirs(folder, exist_ok=True)

    conn = get_conn()
    cur = conn.cursor()
    saved = []
    for file in request.files.getlist("files"):
        ext = os.path.splitext(file.filename)[1] or ".png"
        filename = f"{uuid.uuid4().hex}{ext}"
        file.save(os.path.join(folder, filename))
        cur.execute(
            "INSERT INTO trade_images (trade_id, filename, original_name, created_at) VALUES (%s,%s,%s,%s)",
            (trade_id, filename, file.filename, int(time.time()*1000))
        )
        saved.append({"name": file.filename, "url": f"/uploads/{trade_id}/{filename}"})
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"images": saved})


@app.route("/api/images", methods=["DELETE"])
def delete_image():
    url = request.args.get("url", "")
    # url viene como /uploads/<trade_id>/<filename>
    parts = url.strip("/").split("/")
    if len(parts) != 3:
        return jsonify({"ok": False, "error": "url inválida"}), 400
    _, trade_id, filename = parts

    path = os.path.join(UPLOAD_DIR, trade_id, filename)
    if os.path.exists(path):
        os.remove(path)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM trade_images WHERE trade_id=%s AND filename=%s", (trade_id, filename))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"ok": True})


# ============== API: PLAN DE TRADING ==============
@app.route("/api/plan", methods=["GET"])
def get_plan():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM trading_plan")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({r["key"]: r["value"] for r in rows})


@app.route("/api/plan", methods=["POST"])
def save_plan():
    data = request.get_json(force=True)
    conn = get_conn()
    cur = conn.cursor()
    for key, value in data.items():
        cur.execute("""
            INSERT INTO trading_plan (`key`, value) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE value=%s
        """, (key, value, value))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"ok": True})


# ============== API: CONFIGURACIÓN (capital inicial) ==============
@app.route("/api/settings", methods=["GET"])
def get_settings():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM settings")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({r["key"]: r["value"] for r in rows})


@app.route("/api/settings", methods=["POST"])
def save_settings():
    data = request.get_json(force=True)
    conn = get_conn()
    cur = conn.cursor()
    for key, value in data.items():
        cur.execute("""
            INSERT INTO settings (`key`, value) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE value=%s
        """, (key, value, value))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Bitácora FOTSI corriendo en http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
