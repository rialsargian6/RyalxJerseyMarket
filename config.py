"""Konfigurasi toko. Ubah nilai di sini sesuai kebutuhan."""
from pathlib import Path

nama_toko = "RyalMarketX"
deskripsi_toko = "Baju pilihan, harga bersahabat."

# Nomor WhatsApp penjual, format internasional tanpa tanda + (contoh: 62812...)
nomor_wa = "6285362442395"

# Password untuk masuk ke menu admin (tambah & kelola produk)
password_admin = "rial"

DB_PATH = "toko.db"
UPLOAD_DIR = Path("uploads")

kategorii = ["Jersey"]
ukurann = ["S", "M", "L", "XL", "XXL", "All Size"]


def format_rupiah(angka: int) -> str:
    return "Rp " + f"{int(angka):,}".replace(",", ".")
