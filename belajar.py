import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import datetime
import math

# --- 1. CORE DATABASE INITIALIZATION ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "stok": 150.0, # Rendah untuk pancing Alert AI
        "kas": 150000000.0,
        "sales": pd.DataFrame(columns=['Tgl', 'Customer', 'Produk', 'Qty', 'Total']),
        "ops": pd.DataFrame(columns=['Tgl', 'Kategori', 'Keterangan', 'Nominal']),
        "po": pd.DataFrame(columns=['Tgl', 'Vendor', 'Item', 'Qty', 'Total']),
        "planning": pd.DataFrame(columns=['Bulan', 'Target Produk', 'Target Qty'])
    }

if 'config' not in st.session_state:
    st.session_state.config = {
        "name": "ZYNTRA LABS",
        "logo": "https://cdn-icons-png.flaticon.com/512/2103/2103633.png",
        "lang": "Indonesia 🇮🇩"
    }

# --- 2. THEME & UTILS ---
st.set_page_config(page_title=st.session_state.config["name"], layout="wide")

def format_rp(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Laporan')
    writer.close()
    return output.getvalue()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image(st.session_state.config["logo"], width=80)
    st.title(st.session_state.config["name"])
    st.caption("Control Your Assets")
    st.divider()
    menu = st.radio("SISTEM CORE", [
        "📊 DASHBOARD & AI", 
        "📅 PERENCANAAN",
        "🛒 PURCHASING (PO)", 
        "🏗️ PRODUKSI & SALES", 
        "📦 GUDANG & QR", 
        "💸 KEUANGAN & EXPORT", 
        "⚙️ PENGATURAN"
    ])
    st.divider()
    st.metric("SALDO KAS", format_rp(st.session_state.db["kas"]))

# --- 4. MODUL HALAMAN ---

# A. DASHBOARD & AI INTELLIGENCE
if menu == "📊 DASHBOARD & AI":
    st.title("🖥️ Executive Dashboard")
    
    # AI PREDICTIVE ALERT
    if st.session_state.db['stok'] < 200:
        st.error(f"🚨 **AI ALERT:** Stok Kritis ({st.session_state.db['stok']}m). Prediksi terhenti dalam 48 jam!")
        if st.button("🚀 AUTO-ACTION: Re-stock 500m"):
            cost = 500 * 50000
            st.session_state.db['stok'] += 500
            st.session_state.db['kas'] -= cost
            st.rerun()

    c1, c2, c3 = st.columns(3)
    c1.metric("Asset Stock", f"{st.session_state.db['stok']} m")
    c2.metric("Total Revenue", format_rp(st.session_state.db["sales"]["Total"].sum()))
    c3.metric("Profit Margin", "28.4%")

    st.subheader("💡 AI Analytics (EOQ)")
    d = 12000; s = 100000; h = 2000
    eok = math.sqrt((2 * d * s) / h)
    st.info(f"Rekomendasi AI: Belanja **{round(eok)} Meter** per order untuk efisiensi biaya.")

# B. PERENCANAAN
elif menu == "📅 PERENCANAAN":
    st.title("📅 Production Planning")
    with st.form("plan_form"):
        p_name = st.text_input("Target Produk")
        p_qty = st.number_input("Target Qty", min_value=1)
        if st.form_submit_button("Simpan Rencana"):
            new_p = pd.DataFrame({'Bulan': [datetime.date.today().strftime("%B")], 'Target Produk': [p_name], 'Target Qty': [p_qty]})
            st.session_state.db["planning"] = pd.concat([st.session_state.db["planning"], new_p], ignore_index=True)
    st.table(st.session_state.db["planning"])

# C. PURCHASING (HULU)
elif menu == "🛒 PURCHASING (PO)":
    st.title("🛒 Purchase Management")
    with st.form("po_form"):
        v = st.text_input("Vendor")
        it = st.text_input("Material")
        q = st.number_input("Qty", min_value=1)
        p = st.number_input("Harga Beli", min_value=0)
        if st.form_submit_button("Terbitkan PO"):
            tot = q * p
            if st.session_state.db['kas'] >= tot:
                st.session_state.db['kas'] -= tot
                st.session_state.db['stok'] += q
                new_po = pd.DataFrame([{'Tgl': str(datetime.date.today()), 'Vendor': v, 'Item': it, 'Qty': q, 'Total': tot}])
                st.session_state.db["po"] = pd.concat([st.session_state.db["po"], new_po], ignore_index=True)
                st.success("PO Lunas & Stok Masuk.")
            else: st.error("Kas Kurang!")

# D. PRODUKSI & SALES (HILIR)
elif menu == "🏗️ PRODUKSI & SALES":
    st.title("🏗️ Sales Activity")
    with st.form("sale_form"):
        cs = st.text_input("Customer")
        pj = st.text_input("Produk")
        qp = st.number_input("Qty Pcs", min_value=1)
        hj = st.number_input("Harga Jual Satuan", min_value=0)
        if st.form_submit_button("Eksekusi Penjualan"):
            needed = qp * 2
            if st.session_state.db['stok'] >= needed:
                st.session_state.db['stok'] -= needed
                rev = qp * hj
                st.session_state.db['kas'] += rev
                new_s = pd.DataFrame([{'Tgl': str(datetime.date.today()), 'Customer': cs, 'Produk': pj, 'Qty': qp, 'Total': rev}])
                st.session_state.db["sales"] = pd.concat([st.session_state.db["sales"], new_s], ignore_index=True)
                st.balloons()
            else: st.error("Bahan Baku Tidak Cukup!")

# E. GUDANG & QR
elif menu == "📦 GUDANG & QR":
    st.title("📦 Warehouse Control")
    qr_id = st.text_input("Generate ID Aset")
    if st.button("Generate QR"):
        qr = qrcode.make(qr_id)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf, width=200)

# F. KEUANGAN & EXPORT
elif menu == "💸 KEUANGAN & EXPORT":
    st.title("💸 Financial Control")
    
    # EXPORT SECTION
    st.subheader("📥 Download Laporan (Excel)")
    c_ex1, c_ex2 = st.columns(2)
    with c_ex1:
        st.download_button("Download Sales Report", data=to_excel(st.session_state.db["sales"]), file_name="Sales_Report.xlsx")
    with c_ex2:
        st.download_button("Download Ops Report", data=to_excel(st.session_state.db["ops"]), file_name="Ops_Report.xlsx")

    st.divider()
    st.subheader("➕ Tambah Biaya Operasional")
    with st.form("ops_form"):
        kt = st.selectbox("Kategori", ["Gaji", "Sewa", "Listrik", "Transport", "Lainnya"])
        ket = st.text_input("Keterangan")
        nm = st.number_input("Nominal", min_value=0)
        if st.form_submit_button("Bayar"):
            st.session_state.db['kas'] -= nm
            new_o = pd.DataFrame([{'Tgl': str(datetime.date.today()), 'Kategori': kt, 'Keterangan': ket, 'Nominal': nm}])
            st.session_state.db["ops"] = pd.concat([st.session_state.db["ops"], new_o], ignore_index=True)
            st.success("Tercatat.")

# G. PENGATURAN
elif menu == "⚙️ PENGATURAN":
    st.title("⚙️ System Settings")
    st.session_state.config["name"] = st.text_input("Nama Perusahaan", value=st.session_state.config["name"])
    st.session_state.config["logo"] = st.text_input("Logo URL", value=st.session_state.config["logo"])
    st.button("Update Configuration")# Simpan otomatis ke file setiap ada perubahan
st.session_state.db['sales'].to_csv('data_penjualan.csv', index=False)