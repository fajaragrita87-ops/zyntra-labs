# --- 1. CONFIG & MOBILE OPTIMIZATION ---
st.set_page_config(
    page_title="ZYNTRA LABS", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Di HP, sidebar otomatis sembunyi biar lega
)

# CSS tambahan biar tabel bisa di-scroll di HP
st.markdown("""
<style>
    .stTable { overflow-x: auto; }
    div[data-testid="column"] { width: 100% !important; flex: 1 1 auto !important; }
    @media (max-width: 640px) {
        .main .block-container { padding: 10px; }
        h1 { font-size: 20px !important; }
    }
</style>
""", unsafe_allow_html=True)