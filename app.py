import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io
import requests

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="บันทึกสุขภาพเพื่อคุณหมอ 2026", page_icon="🩺", layout="wide")

columns_order = ["วันที่", "เวลา / เหตุการณ์", "SYS", "DIA", "BPM", "FBS", "น้ำหนัก", "บันทึกเพิ่มเติม"]
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxA_6LR6KN7dfd2_4CjaGSE1_OPc9YzAr9V9z0YdHyXJcX_Cnyy9Ter0MpzRhtF0uZ1/exec"

def format_thai_date(date_input):
    try:
        date_str = str(date_input).strip()
        if 'T' in date_str:
            clean_date = date_str.split('T')[0].strip()
            dt = datetime.strptime(clean_date, "%Y-%m-%d")
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        
        if dt.year > 2500:
            year_th = dt.year
        elif dt.year > 2200:
            year_th = 2026 + 543
        else:
            year_th = dt.year + 543
            
        day = dt.day
        month_names = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        month_str = month_names[dt.month]
        return f"{day} {month_str} {year_th}"
    except:
        return str(date_input)

def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        if not data or len(data) <= 1:
            return pd.DataFrame(columns=columns_order)
        
        # ใช้ตำแหน่งคอลัมน์ตรงๆ เพื่อป้องกันปัญหาชื่อหัวข้อไม่ตรงกัน
        rows = data[1:]
        processed_rows = []
        for r in rows:
            row_data = []
            for i in range(len(columns_order)):
                if i < len(r):
                    row_data.append(r[i])
                else:
                    row_data.append("")
            processed_rows.append(row_data)
            
        df = pd.DataFrame(processed_rows, columns=columns_order)
        
        if 'วันที่' in df.columns:
            df['วันที่'] = df['วันที่'].apply(format_thai_date)
            
        return df[columns_order]
    except Exception as e:
        return pd.DataFrame(columns=columns_order)

def save_data(df):
    try:
        payload = {
            "action": "save",
            "rows": [df.columns.values.tolist()] + df.values.tolist()
        }
        requests.post(WEB_APP_URL, json=payload)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")

st.title("🩺 บันทึกสุขภาพเพื่อคุณหมอ 2026 💖")

with st.sidebar.form("health_form", clear_on_submit=True):
    st.header("✨ บันทึกข้อมูลสุขภาพ ✨")
    date_input = st.date_input("📅 วันที่วัด", datetime.now())
    time_event = st.text_input("⏰ เวลา / เหตุการณ์ (เช่น เช้า, เย็น)", "เช้า")
    sys = st.number_input("❤️ ความดันตัวบน (SYS)", min_value=0, value=120)
    dia = st.number_input("💙 ความดันตัวล่าง (DIA)", min_value=0, value=80)
    bpm = st.number_input("💓 ชีพจร (BPM)", min_value=0, value=72)
    fbs = st.number_input("🩸 น้ำตาลในเลือด (FBS)", min_value=0.0, value=100.0)
    weight = st.number_input("⚖️ น้ำหนัก (kg)", min_value=0.0, value=60.0)
    note = st.text_input("📝 บันทึกเพิ่มเติม")
    
    if st.form_submit_button("🚀 บันทึกข้อมูลสุขภาพ"):
        formatted_date_str = format_thai_date(date_input)
        new_row = {
            "วันที่": formatted_date_str,
            "เวลา / เหตุการณ์": time_event,
            "SYS": sys,
            "DIA": dia,
            "BPM": bpm,
            "FBS": fbs,
            "น้ำหนัก": weight,
            "บันทึกเพิ่มเติม": note
        }
        df_current = get_data()
        new_df = pd.DataFrame([new_row])
        final_df = pd.concat([df_current, new_df], ignore_index=True)
        save_data(final_df)
        st.success("บันทึกข้อมูลสุขภาพเรียบร้อยครับ!")
        st.rerun()

df = get_data()

st.subheader("📋 ตารางบันทึกข้อมูล (แก้ไข/ลบได้)")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="health_editor")

if st.button("🔄 อัปเดตและบันทึกข้อมูลใหม่"):
    save_data(edited_df[columns_order])
    st.success("อัปเดตข้อมูลออนไลน์เรียบร้อย!")
    st.rerun()