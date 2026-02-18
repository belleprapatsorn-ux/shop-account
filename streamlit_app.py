import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="ระบบบัญชีร้าน Bell", layout="wide")

# สร้างโฟลเดอร์เก็บข้อมูลและรูปภาพถ้ายังไม่มี
if not os.path.exists("uploaded_images"):
    os.makedirs("uploaded_images")
if not os.path.exists("data"):
    os.makedirs("data")

CSV_FILE = "data/transactions.csv"

# --- 2. ฟังก์ชันช่วยทำงาน ---

# โหลดข้อมูลเก่า (ถ้ามี)
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Type", "Category", "SubCategory", "Amount", "Image_Path", "Timestamp"])

# บันทึกข้อมูลลงไฟล์ CSV (กันข้อมูลหาย)
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# ฟังก์ชันเซฟรูป
def save_uploaded_image(uploaded_file):
    if uploaded_file is not None:
        # ตั้งชื่อไฟล์ใหม่ด้วยเวลา (กันชื่อซ้ำ)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = uploaded_file.name.split('.')[-1]
        filename = f"{timestamp}_{uploaded_file.name}" # เก็บชื่อเดิมไว้บ้างจะได้จำได้
        file_path = os.path.join("uploaded_images", filename)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return filename # คืนค่าเป็นชื่อไฟล์
    return None

# --- 3. ส่วนหน้าจอหลัก (UI) ---
st.title("💰 ระบบบันทึกรายรับ-รายจ่าย (ฉบับแก้ไข)")

# โหลดข้อมูลเข้า Session State
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# สร้าง Tabs
tab1, tab2, tab3, tab4 = st.tabs(["บันทึกรายรับ", "บันทึกรายจ่าย", "สรุปยอด (Dashboard)", "ประวัติ & Export"])

# ================= TAB 1: บันทึกรายรับ =================
with tab1:
    st.header("📥 บันทึกรายรับประจำวัน")
    
    # ใช้ st.form เพื่อแก้ปัญหากดเบิ้ลแล้วข้อมูลซ้ำ
    with st.form("revenue_form", clear_on_submit=True):
        date_rev = st.date_input("วันที่", datetime.now())
        
        # จัด 6 คอลัมน์ตามที่ขอ
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1:
            st.markdown("**🏦 เงินโอน**")
            amt_transfer = st.number_input("ยอดโอน", min_value=0.0, key="rev_trans")
            img_transfer = st.file_uploader("สลิป", type=["jpg","png","jpeg"], key="img_trans")
            
        with c2:
            st.markdown("**💵 เงินสด**")
            amt_cash = st.number_input("ยอดสด", min_value=0.0, key="rev_cash")
            # เงินสดไม่มีรูป
            
        with c3:
            st.markdown("**🟢 LineMan**")
            amt_lm = st.number_input("ยอด LM", min_value=0.0, key="rev_lm")
            img_lm = st.file_uploader("หลักฐาน", type=["jpg","png"], key="img_lm")
            
        with c4:
            st.markdown("**✳️ Grab**")
            amt_grab = st.number_input("ยอด Grab", min_value=0.0, key="rev_grab")
            img_grab = st.file_uploader("หลักฐาน", type=["jpg","png"], key="img_grab")
            
        with c5:
            st.markdown("**🟠 Shopee**")
            amt_shopee = st.number_input("ยอด Shopee", min_value=0.0, key="rev_shopee")
            img_shopee = st.file_uploader("หลักฐาน", type=["jpg","png"], key="img_shopee")
            
        with c6:
            st.markdown("**⚪ อื่นๆ**")
            amt_other = st.number_input("ยอดอื่นๆ", min_value=0.0, key="rev_other")
            img_other = st.file_uploader("หลักฐาน", type=["jpg","png"], key="img_other")

        submitted_rev = st.form_submit_button("💾 บันทึกรายรับ (กดทีเดียว)", type="primary")
        
        if submitted_rev:
            new_rows = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # ฟังก์ชันย่อยสำหรับเช็คและเพิ่มรายการ
            def add_rev_item(subcat, amount, img_file):
                if amount > 0:
                    path = save_uploaded_image(img_file)
                    new_rows.append({
                        "Date": date_rev, "Type": "รายรับ", "Category": "รายรับขายของ", 
                        "SubCategory": subcat, "Amount": amount, "Image_Path": path, "Timestamp": timestamp
                    })

            add_rev_item("เงินโอน", amt_transfer, img_transfer)
            add_rev_item("เงินสด", amt_cash, None)
            add_rev_item("LineMan", amt_lm, img_lm)
            add_rev_item("Grab", amt_grab, img_grab)
            add_rev_item("Shopee", amt_shopee, img_shopee)
            add_rev_item("อื่นๆ", amt_other, img_other)
            
            if new_rows:
                new_df = pd.DataFrame(new_rows)
                st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                save_data(st.session_state.df) # บันทึกลงไฟล์ทันที
                st.success("✅ บันทึกรายรับเรียบร้อย!")
            else:
                st.warning("⚠️ กรุณากรอกยอดเงินอย่างน้อย 1 ช่อง")

# ================= TAB 2: บันทึกรายจ่าย =================
with tab2:
    st.header("📤 บันทึกค่าใช้จ่าย")
    
    with st.form("expense_form", clear_on_submit=True):
        date_exp = st.date_input("วันที่จ่าย", datetime.now())
        
        # เลือกหมวดหมู่หลัก (แก้ให้ Shopee/Lazada มาอยู่ซื้อของเข้าร้าน)
        cat_option = st.selectbox("หมวดหมู่หลัก", [
            "1. ซื้อของเข้าร้าน (Online Marts)",
            "2. วัตถุดิบ & ต้นทุนผลิต",
            "3. ค่าดำเนินการ & อื่นๆ"
        ])
        
        sub_options = []
        if "1. ซื้อของเข้าร้าน" in cat_option:
            sub_options = ["Shopee (ซื้อของ)", "Lazada (ซื้อของ)", "Grab Mart", "LineMan Mart"]
        elif "2. วัตถุดิบ" in cat_option:
            sub_options = ["ไก่สด", "ตีนไก่", "เส้น", "ผักสด", "แก๊ส", "ค่าจ้างทำน้ำก๋วยเตี๋ยว", "แมคโคร", "วัตถุดิบอื่นๆ"]
        else:
            sub_options = ["ค่าจ้างลูกน้องหน้าร้าน", "ค่าเช่า", "ค่าส่งของคืนลูกค้า", "ค่าธรรมเนียม Shopee (Fee)", "ค่าธรรมเนียม Lazada (Fee)", "ค่าไฟ/ค่าน้ำ", "อื่นๆ"]
            
        sub_cat = st.selectbox("ระบุรายการ", sub_options)
        amount_exp = st.number_input("จำนวนเงิน", min_value=0.0)
        img_exp = st.file_uploader("รูปใบเสร็จ/หลักฐาน", type=["jpg","png","jpeg"])
        
        submitted_exp = st.form_submit_button("💾 บันทึกค่าใช้จ่าย", type="primary")
        
        if submitted_exp:
            if amount_exp > 0:
                path = save_uploaded_image(img_exp)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = {
                    "Date": date_exp, "Type": "รายจ่าย", "Category": cat_option, 
                    "SubCategory": sub_cat, "Amount": amount_exp, "Image_Path": path, "Timestamp": timestamp
                }
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.df)
                st.success("✅ บันทึกค่าใช้จ่ายเรียบร้อย!")
            else:
                st.error("⚠️ กรุณาระบุจำนวนเงิน")

# ================= TAB 3: Dashboard =================
with tab3:
    st.header("📊 ภาพรวมร้าน")
    
    if not st.session_state.df.empty:
        df = st.session_state.df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Filter เดือน
        col_ym1, col_ym2 = st.columns(2)
        with col_ym1:
            sel_year = st.selectbox("เลือกปี", df['Date'].dt.year.unique())
        with col_ym2:
            sel_month = st.selectbox("เลือกเดือน", df['Date'].dt.month.unique())
            
        mask = (df['Date'].dt.year == sel_year) & (df['Date'].dt.month == sel_month)
        df_month = df[mask]
        
        total_rev = df_month[df_month['Type']=="รายรับ"]['Amount'].sum()
        total_exp = df_month[df_month['Type']=="รายจ่าย"]['Amount'].sum()
        net = total_rev - total_exp
        
        k1, k2, k3 = st.columns(3)
        k1.metric("รายรับรวม", f"฿{total_rev:,.2f}")
        k2.metric("รายจ่ายรวม", f"฿{total_exp:,.2f}")
        k3.metric("กำไรสุทธิ", f"฿{net:,.2f}", delta_color="normal")
        
        st.divider()
        
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.subheader("ที่มาของรายได้")
            rev_grp = df_month[df_month['Type']=="รายรับ"].groupby("SubCategory")['Amount'].sum()
            if not rev_grp.empty:
                st.bar_chart(rev_grp, color="#00CC96")
            else:
                st.info("ไม่มีข้อมูลรายรับ")
                
        with c_chart2:
            st.subheader("รายจ่ายแยกตามหมวดหมู่")
            exp_grp = df_month[df_month['Type']=="รายจ่าย"].groupby("Category")['Amount'].sum()
            if not exp_grp.empty:
                st.bar_chart(exp_grp, color="#EF553B")
            else:
                st.info("ไม่มีข้อมูลรายจ่าย")

# ================= TAB 4: Export =================
with tab4:
    st.header("🗂️ ประวัติรายการ & Export Excel")
    
    if not st.session_state.df.empty:
        # โชว์ตาราง
        st.dataframe(st.session_state.df)
        
        # ปุ่มโหลด Excel
        # ใช้ to_csv เพื่อความง่ายและรวดเร็ว (เปิดใน Excel ได้เหมือนกัน)
        csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig') # ใช้ utf-8-sig เพื่อให้อ่านภาษาไทยออก
        
        st.download_button(
            label="📥 ดาวน์โหลดเป็นไฟล์ Excel (CSV)",
            data=csv,
            file_name=f"บัญชีร้าน_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.info("💡 หมายเหตุ: ไฟล์ Excel จะแสดงชื่อรูปภาพในช่อง Image_Path ท่านสามารถนำชื่อไฟล์ไปค้นหาในโฟลเดอร์ 'uploaded_images' ได้")
        
        # ส่วนแสดงรูปภาพ (Gallery)
        st.divider()
        st.subheader("🖼️ แกลเลอรีรูปใบเสร็จล่าสุด")
        # โชว์ 5 รูปล่าสุด
        recent_imgs = st.session_state.df[st.session_state.df['Image_Path'].notna()].tail(5)
        if not recent_imgs.empty:
            cols = st.columns(5)
            for idx, (index, row) in enumerate(recent_imgs.iterrows()):
                img_path = os.path.join("uploaded_images", row['Image_Path'])
                if os.path.exists(img_path):
                    with cols[idx]:
                        st.image(img_path, caption=f"{row['SubCategory']} ({row['Amount']}บ.)")
    else:
        st.info("ยังไม่มีข้อมูล")
