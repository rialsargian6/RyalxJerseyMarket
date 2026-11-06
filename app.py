"""Tampilan aplikasi (Streamlit). Jalankan dengan: streamlit run app.py"""
from pathlib import Path
from urllib.parse import quote

import streamlit as st

import database as db
from config import (
    password_admin,
    deskripsi_toko,
    kategorii,
    nama_toko,
    nomor_wa,
    ukurann,
    format_rupiah,
)

st.set_page_config(page_title=nama_toko, layout="wide")
db.init_db()


# ---------- Halaman ----------
def halaman_dashboard():
    st.title("Store")
    st.caption(deskripsi_toko)

    c1, c2, c3 = st.columns([2, 1, 1])
    keyword = c1.text_input("Cari baju", placeholder="contoh: Jersey .....")
    kategori = c2.selectbox("Kategori", ["Semua"] + kategorii)
    ukuran = c3.selectbox("Ukuran", ["Semua"] + ukurann)

    produk = db.ambil_produk(keyword, kategori, ukuran, hanya_tersedia=True)
    if not produk:
        st.info("Belum ada baju yang cocok.")
        return

    kolom_per_baris = 3
    for i in range(0, len(produk), kolom_per_baris):
        kolom = st.columns(kolom_per_baris)
        for kol, p in zip(kolom, produk[i : i + kolom_per_baris]):
            with kol, st.container(border=True):
                if p["foto"] and Path(p["foto"]).exists():
                    st.image(p["foto"], use_container_width=True)
                else:
                    st.caption("(tanpa foto)")
                st.subheader(p["nama"])
                st.markdown(f"**{format_rupiah(p['harga'])}**")
                st.caption(f"{p['kategori']} • Ukuran {p['ukuran']} • Stok {p['stok']}")
                if p["deskripsi"]:
                    st.write(p["deskripsi"])
                pesan = (
                    f"Halo, saya mau pesan {p['nama']} "
                    f"(ukuran {p['ukuran']}) seharga {format_rupiah(p['harga'])}."
                )
                st.link_button(
                    "Pesan via WhatsApp",
                    f"https://wa.me/{nomor_wa}?text={quote(pesan)}",
                    use_container_width=True,
                )


def halaman_tambah():
    st.title("Tambah Baju")
    with st.form("form_tambah", clear_on_submit=True):
        nama = st.text_input("Nama baju")
        c1, c2 = st.columns(2)
        kategori = c1.selectbox("Kategori", kategorii)
        ukuran = c2.selectbox("Ukuran", ukurann)
        c3, c4 = st.columns(2)
        harga = c3.number_input("Harga (Rp)", min_value=0, step=5000, value=50000)
        stok = c4.number_input("Stok", min_value=0, step=1, value=1)
        deskripsi = st.text_area("Deskripsi (kondisi, bahan, dll)")
        foto = st.file_uploader("Foto", type=["jpg", "jpeg", "png", "webp"])
        simpan = st.form_submit_button("Simpan", type="primary")

    if simpan:
        if not nama.strip():
            st.error("Nama baju wajib diisi.")
            return
        path_foto = db.simpan_foto(foto) if foto else None
        db.tambah_produk(nama.strip(), kategori, ukuran, int(harga), int(stok), deskripsi, path_foto)
        st.success(f"'{nama}' berhasil ditambahkan.")


def halaman_kelola():
    st.title("Kelola Produk")
    produk = db.ambil_produk()
    if not produk:
        st.info("Belum ada produk.")
        return

    for p in produk:
        label = f"{p['nama']} • {format_rupiah(p['harga'])} • stok {p['stok']}"
        with st.expander(label):
            with st.form(f"form_{p['id']}"):
                c1, c2, c3 = st.columns(3)
                harga = c1.number_input("Harga (Rp)", min_value=0, step=5000, value=int(p["harga"]))
                stok = c2.number_input("Stok", min_value=0, step=1, value=int(p["stok"]))
                kategori=c3.selectbox("Kategori", kategorii)
                b1, b2 = st.columns(2)
                simpan = b1.form_submit_button("Simpan perubahan", type="secondary")
                hapus = b2.form_submit_button("Hapus produk")
            if simpan:
                db.ubah_produk(p["id"], int(harga), int(stok),(kategori))
                st.rerun()
            if hapus:
                db.hapus_produk(p["id"])
                st.rerun()

def sidebar_admin():
    st.sidebar.title(nama_toko)
    if st.session_state.get("admin"):
        menu = st.sidebar.radio("Menu", ["Dashboard", "Tambah Baju", "Kelola Produk"])
        if st.sidebar.button("Keluar admin"):
            st.session_state["admin"] = False
            st.rerun()
        return menu

    st.sidebar.write("Menu: Dashboard")
    with st.sidebar.expander("Login admin"):
        password = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if password == password_admin:
                st.session_state["admin"] = True
                st.rerun()
            else:
                st.error("Password salah.")
    return "Dashboard"


menu = sidebar_admin()
if menu == "Dashboard":
    halaman_dashboard()
elif menu == "Tambah Baju":
    halaman_tambah()
else:
    halaman_kelola()
