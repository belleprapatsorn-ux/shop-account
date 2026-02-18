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
        return pd.DataFrame(columns=["Date", "Type", "Category", "SubCategory", "Amount", "Image_Path", "Timestamp", "Note"])

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
st.title("🍜 บัญชีร้านก๋วยเตี๋ยวไก่นายโจ")

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'last_submit_time' not in st.session_state:
    st.session_state.last_submit_time = 0

# สร้าง Tabs
tab1, tab2, tab3, tab4 = st.tabs(["บันทึกรายรับ", "บันทึกรายจ่าย", "สรุปยอด (Dashboard)", "ประวัติ & Export"])

# ================= TAB 1: บันทึกรายรับ =================
with tab1:
    st.header("📥 บันทึกรายรับ")
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
            st.markdown("**✳️ Grab**")
            amt_grab = st.number_input("ยอด Grab", min_value=0.0, key="rev_grab")
            img_grab = st.file_uploader("รูปยอด", type=["jpg","png"], key="img_grab")
        with c5:
            st.markdown("**🟠 Shopee**")
            amt_shopee = st.number_input("ยอด Shopee", min_value=0.0, key="rev_shopee")
            img_shopee = st.file_uploader("รูปยอด", type=["jpg","png"], key="img_shopee")
        with c6:
            st.markdown("**⚪ อื่นๆ**")
            amt_other = st.number_input("ยอดอื่นๆ", min_value=0.0, key="rev_other")
            img_other = st.file_uploader("รูปหลักฐาน", type=["jpg","png"], key="img_other")

        if st.form_submit_button("💾 บันทึกรายรับ", type="primary"):
            if time.time() - st.session_state.last_submit_time < 2:
                st.warning("⏳ ใจเย็นๆ ครับ กำลังบันทึก...")
            else:
                st.session_state.last_submit_time = time.time()
                new_rows = []
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                def add_rev(subcat, amount, img):
                    if amount > 0:
                        path = save_uploaded_image(img)
                        new_rows.append({"Date": date_rev, "Type": "รายรับ", "Category": "รายได้จากการขาย", "SubCategory": subcat, "Amount": amount, "Image_Path": path, "Timestamp": timestamp, "Note": ""})
                
                add_rev("เงินโอน", amt_transfer, img_transfer)
                add_rev("เงินสด", amt_cash, None)
                add_rev("LineMan", amt_lm, img_lm)
                add_rev("Grab", amt_grab, img_grab)
                add_rev("Shopee", amt_shopee, img_shopee)
                add_rev("อื่นๆ", amt_other, img_other)
                
                if new_rows:
                    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame(new_rows)], ignore_index=True)
                    save_data(st.session_state.df)
                    st.success("✅ บันทึกรายรับแล้ว")
                else:
                    st.warning("⚠️ ไม่มียอดเงิน")

# ================= TAB 2: บันทึกรายจ่าย (แก้ Bug Dropdown ไม่เปลี่ยน) =================
with tab2:
    st.header("📤 บันทึกรายจ่าย")
    
    # --- ส่วนเลือกหมวดหมู่ (อยู่นอก Form เพื่อให้เปลี่ยนรายการได้ทันที) ---
    expense_structure = {
        "🥬 จ่ายตลาดสด": ["ร้านไก่สด", "ร้านตีนไก่", "เลือดไก่", "ร้านเส้นก๋วยเตี๋ยว", "ผักสด", ""],
        "📦 สั่งของเข้าร้าน": ["แมคโคร (Makro)", "Shopee (ซื้อของ)", "Lazada (ซื้อของ)", "Grab Mart", "LineMan Mart", "เครื่องปรุงซอง"],
        "🔥 ต้นทุนผลิต & แรงงาน": ["ค่าแก๊ส", "ค่าจ้างทำน้ำซุป", "ค่าจ้างลูกน้องหน้าร้าน"],
        "🏠 ค่าใช้จ่ายอื่น ๆ": ["ค่าเช่า", "ค่าน้ำ/ค่าไฟ", "ค่าส่งคืนสินค้า", "อื่น ๆ"]
    }
    # Selectbox อยู่นอก Form -> พอเลือกปุ๊บ หน้าเว็บจะโหลดใหม่และเปลี่ยนตัวเลือกย่อยทันที
    main_cat = st.selectbox("เลือกหมวดหมู่หลัก", list(expense_structure.keys()))
    sub_cat = st.selectbox("ระบุรายการย่อย", expense_structure[main_cat])
    
    # --- ส่วนกรอกข้อมูลเงิน (อยู่ใน Form เพื่อให้กดบันทึกทีเดียว) ---
    with st.form("expense_form", clear_on_submit=True):
        date_exp = st.date_input("วันที่จ่าย", datetime.now())
        note_exp = st.text_input("รายละเอียดเพิ่มเติม (เช่น ซื้อผักบุ้ง 5 กำ)")
        amount_exp = st.number_input("จำนวนเงิน", min_value=0.0)
        img_exp = st.file_uploader("รูปใบเสร็จ", type=["jpg","png","jpeg"])
        
        if st.form_submit_button("💾 บันทึกค่าใช้จ่าย", type="primary"):
            if time.time() - st.session_state.last_submit_time < 2:
                st.warning("⏳ กำลังบันทึก...")
            else:
                st.session_state.last_submit_time = time.time()
                if amount_exp > 0:
                    path = save_uploaded_image(img_exp)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_row = {
                        "Date": date_exp, 
                        "Type": "รายจ่าย", 
                        "Category": main_cat, 
                        "SubCategory": sub_cat, 
                        "Amount": amount_exp, 
                        "Image_Path": path, 
                        "Timestamp": timestamp,
                        "Note": note_exp
                    }
                    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(st.session_state.df)
                    st.success(f"✅ บันทึก '{sub_cat}' ({amount_exp} บาท) เรียบร้อย")
                else:
                    st.error("⚠️ ลืมใส่จำนวนเงิน")

# ================= TAB 3: Dashboard =================
with tab3:
    st.header("📊 Overall ร้านก๋วยเตี๋ยวไก่นายโจ")
    if not st.session_state.df.empty:
        df = st.session_state.df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        
        c1, c2 = st.columns(2)
        sel_year = c1.selectbox("ปี", sorted(df['Date'].dt.year.unique(), reverse=True))
        sel_month = c2.selectbox("เดือน", sorted(df['Date'].dt.month.unique()))
        
        df_m = df[(df['Date'].dt.year == sel_year) & (df['Date'].dt.month == sel_month)]
        
        rev = df_m[df_m['Type']=="รายรับ"]['Amount'].sum()
        exp = df_m[df_m['Type']=="รายจ่าย"]['Amount'].sum()
        
        k1, k2, k3 = st.columns(3)
        k1.metric("รายรับ", f"฿{rev:,.0f}")
        k2.metric("รายจ่าย", f"฿{exp:,.0f}")
        k3.metric("กำไร", f"฿{rev-exp:,.0f}")
        
        st.divider()
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.subheader("หมดเงินไปกับหมวดไหน?")
            if not df_m[df_m['Type']=="รายจ่าย"].empty:
                st.bar_chart(df_m[df_m['Type']=="รายจ่าย"].groupby("Category")['Amount'].sum(), color="#FF4B4B")
        with c_chart2:
            st.subheader("เจาะลึกรายจ่าย")
            if not df_m[df_m['Type']=="รายจ่าย"].empty:
                st.dataframe(df_m[df_m['Type']=="รายจ่าย"][['Date','SubCategory', 'Note', 'Amount']])

# ================= TAB 4: Export =================
with tab4:
    st.header("🗂️ Export")
    if not st.session_state.df.empty:
        st.dataframe(st.session_state.df)
        csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ดาวน์โหลด Excel (CSV)", csv, f"NaiJo_Account_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        st.info("💡 ไฟล์ Excel จะมีชื่อรูปบอกในช่อง Image_Path ครับ")
