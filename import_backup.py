"""
Script para migrar tu respaldo .json (exportado desde la versión anterior)
hacia la base de datos MySQL, guardando las imágenes como archivos reales.

Uso:
    python import_backup.py respaldo-bitacora-fotsi-2026-07-22.json
"""

import sys
import os
import re
import base64
import time
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bitacora_fotsi",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


def import_backup(json_path):
    import json
    with open(json_path, encoding="utf-8") as f:
        trades = json.load(f)

    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    for t in trades:
        trade_id = t.get("id") or f"t{int(time.time()*1000)}"
        cur.execute("""
            INSERT INTO trades (id, date, pair, tf, broker, time_entry, time_tp1, time_tp2,
                dir, div_fuerte, div_debil, atr, sl, entry_price, ema50, ema100, close1, close2,
                capital, risk_pct, status, tp1_desc, tp2_desc, pnl, breakeven, sesion, notes, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE pair=VALUES(pair)
        """, (
            trade_id, t.get("date") or None, t.get("pair"), t.get("tf"), t.get("broker","Saxo"),
            t.get("timeEntry"), t.get("timeTp1"), t.get("timeTp2"), t.get("dir"),
            t.get("divFuerte"), t.get("divDebil"), t.get("atr"), t.get("sl"), t.get("entry"),
            t.get("ema50"), t.get("ema100"), t.get("close1"), t.get("close2"),
            t.get("capital"), t.get("risk","2"), t.get("status","open"),
            t.get("tp1"), t.get("tp2"),
            t.get("pnl") if t.get("pnl") not in ("", None) else None,
            t.get("breakeven","no"), t.get("sesion"), t.get("notes"),
            t.get("createdAt") or int(time.time()*1000)
        ))

        # Migrar imágenes (vienen en base64 dentro de "images": [{"name":..., "dataUrl": "data:image/png;base64,...."}])
        images = t.get("images") or []
        if images:
            folder = os.path.join(UPLOAD_DIR, trade_id)
            os.makedirs(folder, exist_ok=True)
            for idx, img in enumerate(images):
                data_url = img.get("dataUrl", "")
                match = re.match(r"data:image/(\w+);base64,(.+)", data_url)
                if not match:
                    continue
                ext, b64data = match.groups()
                filename = f"{trade_id}_{idx}.{ext}"
                filepath = os.path.join(folder, filename)
                with open(filepath, "wb") as imgf:
                    imgf.write(base64.b64decode(b64data))
                cur.execute(
                    "INSERT INTO trade_images (trade_id, filename, original_name, created_at) VALUES (%s,%s,%s,%s)",
                    (trade_id, filename, img.get("name", filename), int(time.time()*1000))
                )
        print(f"Importada: {t.get('pair')} ({t.get('date')}) - {len(images)} imagen(es)")

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nListo. Se importaron {len(trades)} operaciones.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python import_backup.py <archivo_respaldo.json>")
        sys.exit(1)
    import_backup(sys.argv[1])
