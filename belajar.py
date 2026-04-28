import streamlit as st  # <--- INI WAJIB DI NOMOR 1, BOS!
import pandas as pd
import qrcode
from io import BytesIO
import datetime
import math

# --- 1. SETTING RESPONSIVE HP (WAJIB SETELAH IMPORT) ---
st.set_page_config(
    page_title="ZYNTRA LABS", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# CSS biar tampilan gak kepotong di HP temen lu
st.markdown("""
<style>
    .stTable, .stDataFrame { overflow-x: auto !important; }
    @media (max-width: 640px) {
        .main .block-container { padding: 10px !important; }
        h1 { font-size: 20px !important; }
        div[data-testid="stMetric"] { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. FUNGSI PENDUKUNG ---
def format_rp(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Laporan')
    writer.close()
    return output.getvalue()

# --- 3. DATABASE (SESSION STATE) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "stok": 500.0, 
        "kas": 150000000.0,
        "sales": pd.DataFrame(columns=['Tgl', 'Customer', 'Produk', 'Qty', 'Total']),
        "ops": pd.DataFrame(columns=['Tgl', 'Kategori', 'Keterangan', 'Nominal']),
        "po": pd.DataFrame(columns=['Tgl', 'Vendor', 'Item', 'Qty', 'Total']),
        "planning": pd.DataFrame(columns=['Bulan', 'Target Produk', 'Target Qty'])
    }
if 'config' not in st.session_state:
    st.session_state.config = {"name": "ZYNTRA LABS", "logo": "https://cdn-icons-png.flaticon.com/512/2103/2103633.png"}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image(st.session_state.config["logo"], width=80)
    st.title(st.session_state.config["name"])
    st.metric("CASH", format_rp(st.session_state.db["kas"]))
    st.divider()
    menu = st.radio("MENU", ["📊 DASHBOARD", "📅 PLANNING", "🛒 PURCHASING", "🏗️ PRODUKSI", "📦 GUDANG", "💸 FINANCE", "⚙️ SETTINGS"])

# --- 5. HALAMAN UTAMA ---
if menu == "📊 DASHBOARD":
    st.title("🖥️ Dashboard Utama")
    c1, c2 = st.columns(2)
    c1.metric("Stok Bahan", f"{st.session_state.db['stok']} m")
    c2.metric("Total Revenue", format_rp(st.session_state.db["sales"]["Total"].sum()))
    st.line_chart([10, 25, 20, 45, 30])

elif menu == "📅 PLANNING":
    st.title("📅 Rencana Produksi")
    with st.form("f_plan"):
        prd = st.text_input("Produk")
        qty = st.number_input("Qty", min_value=1)
        if st.form_submit_button("Simpan"):
            new_p = pd.DataFrame({'Bulan': [datetime.date.today().strftime("%B")], 'Target Produk': [prd], 'Target Qty': [qty]})
            st.session_state.db["planning"] = pd.concat([st.session_state.db["planning"], new_p], ignore_index=True)
            st.success("Tersimpan!")
    st.dataframe(st.session_state.db["planning"], use_container_width=True)

elif menu == "🛒 PURCHASING":
    st.title("🛒 Beli Bahan Baku")
    with st.form("f_po"):
        v = st.text_input("Vendor"); q = st.number_input("Meter", min_value=1); p = st.number_input("Harga/m", min_value=0)
        if st.form_submit_button("Proses PO"):
            st.session_state.db['stok'] += q
            st.session_state.db['kas'] -= (q*p)
            st.success("Bahan Masuk Gudang!")

elif menu == "🏗️ PRODUKSI":
    st.title("🏗️ Jual Hasil Produksi")
    with st.form("f_sale"):
        cs = st.text_input("Nama Pembeli"); pj = st.text_input("Nama Barang"); qp = st.number_input("Pcs", min_value=1); hj = st.number_input("Harga Jual", value=150000)
        if st.form_submit_button("Cetak Nota & Jual"):
            st.session_state.db['stok'] -= (qp*2)
            st.session_state.db['kas'] += (qp*hj)
            new_s = pd.DataFrame([{'Tgl': str(datetime.date.today()), 'Customer': cs, 'Produk': pj, 'Qty': qp, 'Total': qp*hj}])
            st.session_state.db["sales"] = pd.concat([st.session_state.db["sales"], new_s], ignore_index=True)
            st.balloons()

elif menu == "📦 GUDANG":
    st.title("📦 Scan & QR Label")
    qr_id = st.text_input("Masukkan ID Barang")
    if st.button("Bikin QR Code"):
        qr = qrcode.make(qr_id)
        buf = BytesIO(); qr.save(buf)
        st.image(buf, width=200)

elif menu == "💸 FINANCE":
    st.title("💸 Laporan Keuangan")
    st.download_button("📥 Download Laporan (Excel)", data=to_excel(st.session_state.db["sales"]), file_name="Laporan_Sales.xlsx")
    st.write("Riwayat Penjualan:")
    st.dataframe(st.session_state.db["sales"], use_container_width=True)

elif menu == "⚙️ SETTINGS":
    st.title("⚙️ Pengaturan")
    st.session_state.config["name"] = st.text_input("Nama Bisnis", value=st.session_state.config["name"])
    if st.button("Save"): st.rerun()
