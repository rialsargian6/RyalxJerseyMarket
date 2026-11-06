"""Semua urusan database (SQLite) dan penyimpanan foto."""
import sqlite3
import uuid
from pathlib import Path

from config import DB_PATH, UPLOAD_DIR


def _run(sql, params=(), fetch=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql, params)
        hasil = cur.fetchall() if fetch else None
        conn.commit()
        return hasil
    finally:
        conn.close()


def init_db():
    UPLOAD_DIR.mkdir(exist_ok=True)
    _run(
        """
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            kategori TEXT NOT NULL,
            ukuran TEXT NOT NULL,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL,
            deskripsi TEXT,
            foto TEXT,
            dibuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def simpan_foto(file_upload) -> str:
    """Simpan foto hasil upload ke folder uploads dan kembalikan path-nya."""
    ekstensi = Path(file_upload.name).suffix.lower() or ".jpg"
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ekstensi}"
    path.write_bytes(file_upload.getbuffer())
    return str(path)


def tambah_produk(nama, kategori, ukuran, harga, stok, deskripsi, foto):
    _run(
        "INSERT INTO produk (nama, kategori, ukuran, harga, stok, deskripsi, foto) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (nama, kategori, ukuran, harga, stok, deskripsi, foto),
    )


def ambil_produk(keyword="", kategori="Semua", ukuran="Semua", hanya_tersedia=False):
    sql = "SELECT * FROM produk WHERE 1=1"
    params = []
    if keyword:
        sql += " AND (nama LIKE ? OR deskripsi LIKE ?)"
        params += [f"%{keyword}%", f"%{keyword}%"]
    if kategori != "Semua":
        sql += " AND kategori = ?"
        params.append(kategori)
    if ukuran != "Semua":
        sql += " AND ukuran = ?"
        params.append(ukuran)
    if hanya_tersedia:
        sql += " AND stok > 0"
    sql += " ORDER BY id DESC"
    return _run(sql, params, fetch=True)


def ubah_produk(id_produk, harga, stok, kategori):
    _run("UPDATE produk SET harga = ?, stok = ?, kategori = ? WHERE id = ?", (harga, stok,kategori, id_produk))


def hapus_produk(id_produk):
    baris = _run("SELECT foto FROM produk WHERE id = ?", (id_produk,), fetch=True)
    if baris and baris[0]["foto"]:
        Path(baris[0]["foto"]).unlink(missing_ok=True)
    _run("DELETE FROM produk WHERE id = ?", (id_produk,))
