import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบบันทึกรายรับ-รายจ่าย", layout="wide")

# สร้างโฟลเดอร์เก็บรูป (ถ้ายังไม่มี)
if not os.path.exists("uploaded_images"):
    os.makedirs("uploaded_images")

# ฟังก์ชันโหลดข้อมูล
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Date', 'Type', 'Category', 'SubCategory', 'Amount', 'Image', 'Note'])

def save_image(uploaded_file):
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join("uploaded_images", f"{timestamp}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

st.title("💰 ระบบบันทึกรายรับ-รายจ่ายร้าน")

# สร้าง Tabs
tab1, tab2, tab3, tab4 = st.tabs(["บันทึกรายรับ", "บันทึกรายจ่าย", "สรุปยอด (Dashboard)", "ประวัติ & Export"])

# --- TAB 1: รายรับ ---
with tab1:
    st.header("บันทึกรายรับประจำวัน")
    date_rev = st.date_input("วันที่", datetime.now())
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.subheader("🏦 เงินโอน")
        rev_transfer = st.number_input("จำนวนเงิน (โอน)", min_value=0.0)
        img_transfer = st.file_uploader("สลิปโอน", key="img_trans")
        
    with col2:
        st.subheader("💵 เงินสด")
        rev_cash = st.number_input("จำนวนเงิน (สด)", min_value=0.0)
        # เงินสดไม่ต้องมีรูป
        
    with col3:
        st.subheader("🟢 LineMan")
        rev_lm = st.number_input("ยอด LineMan", min_value=0.0)
        img_lm = st.file_uploader("รูปยอด LM", key="img_lm")

    with col4:
        st.subheader("✳️ Grab")
        rev_grab = st.number_input("ยอด Grab", min_value=0.0)
        img_grab = st.file_uploader("รูปยอด Grab", key="img_grab")

    with col5:
        st.subheader("🟠 Shopee")
        rev_shopee = st.number_input("ยอด Shopee", min_value=0.0)
        img_shopee = st.file_uploader("รูปยอด Shopee", key="img_shopee")

    with col6:
        st.subheader("⚪ อื่นๆ")
        rev_other = st.number_input("รายรับอื่นๆ", min_value=0.0)
        img_other = st.file_uploader("รูปอื่นๆ", key="img_other")

    if st.button("💾 บันทึกรายรับ", use_container_width=True, type="primary"):
        new_records = []
        # ฟังก์ชันช่วยบันทึก
        def add_record(subcat, amount, img):
            if amount > 0:
                path = save_image(img)
                new_records.append({'Date': date_rev, 'Type': 'รายรับ', 'Category': 'รายรับ', 'SubCategory': subcat, 'Amount': amount, 'Image': path, 'Note': '-'})

        add_record("เงินโอน", rev_transfer, img_transfer)
        add_record("เงินสด", rev_cash, None)
        add_record("LineMan", rev_lm, img_lm)
        add_record("Grab", rev_grab, img_grab)
        add_record("Shopee", rev_shopee, img_shopee)
        add_record("อื่นๆ", rev_other, img_other)
        
        if new_records:
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame(new_records)], ignore_index=True)
            st.success("บันทึกรายรับเรียบร้อย!")
        else:
            st.warning("กรุณากรอกยอดเงินอย่างน้อย 1 ช่อง")

# --- TAB 2: รายจ่าย ---
with tab2:
    st.header("บันทึกค่าใช้จ่าย")
    date_exp = st.date_input("วันที่จ่าย", datetime.now(), key="d_exp")
    
    # Dropdown หมวดหมู่
    main_cat = st.selectbox("หมวดหมู่หลัก", ["ซื้อของเข้าร้าน (Online Marts)", "วัตถุดิบ & ต้นทุนผลิต", "ค่าดำเนินการ & ค่าธรรมเนียม"])
    
    sub_options = []
    if main_cat == "ซื้อของเข้าร้าน (Online Marts)":
        sub_options = ["Shopee", "Lazada", "Grab Mart", "LineMan Mart"]
    elif main_cat == "วัตถุดิบ & ต้นทุนผลิต":
        sub_options = ["ไก่สด", "ตีนไก่", "เส้น", "ผักสด", "แก๊ส", "ค่าจ้างทำน้ำก๋วยเตี๋ยว", "แมคโคร", "อื่นๆ"]
    else:
        sub_options = ["ค่าจ้างลูกน้องหน้าร้าน", "ค่าเช่า", "ค่าส่งของคืนลูกค้า", "ค่าธรรมเนียม Shopee", "ค่าธรรมเนียม Lazada", "อื่นๆ"]
        
    sub_cat = st.selectbox("รายการย่อย", sub_options)
    amount_exp = st.number_input("จำนวนเงินที่จ่าย", min_value=0.0)
    img_exp = st.file_uploader("รูปใบเสร็จ/หลักฐาน", key="img_exp")
    
    if st.button("💾 บันทึกรายจ่าย", use_container_width=True, type="primary"):
        if amount_exp > 0:
            path = save_image(img_exp)
            new_row = {'Date': date_exp, 'Type': 'รายจ่าย', 'Category': main_cat, 'SubCategory': sub_cat, 'Amount': amount_exp, 'Image': path, 'Note': '-'}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("บันทึกรายจ่ายเรียบร้อย!")
        else:
            st.error("กรุณาระบุจำนวนเงิน")

# --- TAB 3: Dashboard ---
with tab3:
    st.header("ภาพรวมเดือนนี้")
    if not st.session_state.data.empty:
        # แปลงวันที่เพื่อคำนวณ
        df = st.session_state.data.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Filter เดือน
        selected_month = st.date_input("เลือกเดือนที่ต้องการดู", datetime.now()).month
        df_month = df[df['Date'].dt.month == selected_month]
        
        total_rev = df_month[df_month['Type'] == 'รายรับ']['Amount'].sum()
        total_exp = df_month[df_month['Type'] == 'รายจ่าย']['Amount'].sum()
        profit = total_rev - total_exp
        
        c1, c2, c3 = st.columns(3)
        c1.metric("รายรับรวม", f"{total_rev:,.2f} บาท")
        c2.metric("รายจ่ายรวม", f"{total_exp:,.2f} บาท")
        c3.metric("กำไรสุทธิ", f"{profit:,.2f} บาท", delta_color="normal")
        
        st.divider()
        
        # กราฟ
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("สัดส่วนรายรับ")
            rev_data = df_month[df_month['Type'] == 'รายรับ']
            if not rev_data.empty:
                st.bar_chart(rev_data.groupby('SubCategory')['Amount'].sum())
            else:
                st.info("ไม่มีข้อมูลรายรับเดือนนี้")
                
        with col_chart2:
            st.subheader("สัดส่วนรายจ่าย")
            exp_data = df_month[df_month['Type'] == 'รายจ่าย']
            if not exp_data.empty:
                st.bar_chart(exp_data.groupby('SubCategory')['Amount'].sum(), color="#FF4B4B")
            else:
                st.info("ไม่มีข้อมูลรายจ่ายเดือนนี้")

# --- TAB 4: Export ---
with tab4:
    st.header("ประวัติรายการ & Export")
    if not st.session_state.data.empty:
        st.dataframe(st.session_state.data)
        
        # ปุ่ม Export CSV
        csv = st.session_state.data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 ดาวน์โหลดเป็น Excel (CSV)",
            data=csv,
            file_name='transaction_report.csv',
            mime='text/csv',
        )
    else:
        st.info("ยังไม่มีข้อมูลในระบบ")
