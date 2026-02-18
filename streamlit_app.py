import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="บัญชีร้านก๋วยเตี๋ยวไก่นายโจ", layout="wide")

# สร้างโฟลเดอร์
if not os.path.exists("uploaded_images"):
    os.makedirs("uploaded_images")
if not os.path.exists("data"):
    os.makedirs("data")

CSV_FILE = "data/transactions.csv"

# --- 2. ฟังก์ชันช่วยทำงาน ---
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Type", "Category", "SubCategory", "Amount", "Image_Path", "Timestamp"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def save_uploaded_image(uploaded_file):
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join("uploaded_images", filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return filename
    return None

# --- 3. ส่วนหน้าจอหลัก (UI) ---
st.title("🍜 ระบบบัญชี ร้านก๋วยเตี๋ยวไก่นายโจ")

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'last_submit_time' not in st.session_state:
    st.session_state.last_submit_time = 0

# สร้าง Tabs
tab1, tab2, tab3, tab4 = st.tabs(["บันทึกรายรับ", "บันทึกรายจ่าย", "สรุปยอด (Dashboard)", "ประวัติ & Export"])

# ================= TAB 1: บันทึกรายรับ =================
with tab1:
    st.header("📥 บันทึกรายรับประจำวัน")
    with st.form("revenue_form", clear_on_submit=True):
        date_rev = st.date_input("วันที่", datetime.now())
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1:
            st.markdown("**🏦 เงินโอน**")
            amt_transfer = st.number_input("ยอดโอน", min_value=0.0, key="rev_trans")
            img_transfer = st.file_uploader("สลิป", type=["jpg","png"], key="img_trans")
        with c2:
            st.markdown("**💵 เงินสด**")
            amt_cash = st.number_input("ยอดสด", min_value=0.0, key="rev_cash")
        with c3:
            st.markdown("**🟢 LineMan**")
            amt_lm = st.number_input("ยอด LM", min_value=0.0, key="rev_lm")
            img_lm = st.file_uploader("รูปยอด", type=["jpg","png"], key="img_lm")
        with c4:
