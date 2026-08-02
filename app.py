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
        if not date_str or date_str == "nan":
            return ""
        if 'T' in date_str:
            clean_date = date_str.split('T')[0].strip()
            dt = datetime.strptime(clean_date, "%Y-%m-%d")
        elif '-' in date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            # ถ้าเป็นวันที่ภาษาไทยอยู่แล้ว ให้คืนค่าเดิมเพื่อแสดงผล
            return date_str
        
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

def convert_to_iso_date(date_str):
    try:
        date_str = str(date_str).strip()
        month_map = {"มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4, "พฤษภาคม": 5, "มิถุนายน": 6, 
                     "กรกฎาคม": 7, "สิงหาคม": 8, "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12}
        parts = date_str.split()
        if len(parts) == 3 and parts[1] in month_map:
            day = int(parts[0])
            month = month_map[parts[1]]
            year = int(parts[2])
            if year > 2500:
                year -= 543
            dt = datetime(year, month, day)
            return dt.strftime("%Y-%m-%d")
        return date_str
    except:
        return date_str

def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        if not data or len(data) <= 1:
            return pd.DataFrame(columns=columns_order)
        
        rows = data[1:]
        processed_rows = []
        for r in rows:
            row_data = []
            for i in range(len(columns_order)):
                if i < len(r):
                    val = r[i]
                    # แปลงคอลัมน์วันที่ให้เป็นไทยตอนแสดงผล
                    if i == 0:
                        val = format_thai_date(val)
                    row_data.append(val)
                else:
                    row_data.append("")
            processed_rows.append(row_data)
            
        df = pd.DataFrame(processed_rows, columns=columns_order)
        return df[columns_order]
    except Exception as e:
        return pd.DataFrame(columns=columns_order)

def save_data(df):
    try:
        # แปลงวันที่ภาษาไทยกลับเป็น YYYY-MM-DD ก่อนบันทึกลง Google Sheets
        df_to_save = df.copy()
        if 'วันที่' in df_to_save.columns:
            df_to_save['วันที่'] = df_to_save['วันที่'].apply(convert_to_iso_date)
            
        payload = {
            "action": "save",
            "rows": [df_to_save.columns.values.tolist()] + df_to_save.values.tolist()
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
        # บันทึกแบบสากลลงระบบหลังบ้าน
        iso_date_str = date_input.strftime("%Y-%m-%d")
        new_row = {
            "วันที่": iso_date_str,
            "เวลา / เหตุการณ์": time_event,
            "SYS": sys,
            "DIA": dia,
            "BPM": bpm,
            "FBS": fbs,
            "น้ำหนัก": weight,
            "บันทึกเพิ่มเติม": note
        }
        df_current_raw = get_data()
        # แปลงข้อมูลในตารางกลับเป็น ISO ก่อนต่อแถวใหม่
        df_current_raw['วันที่'] = df_current_raw['วันที่'].apply(convert_to_iso_date)
        new_df = pd.DataFrame([new_row])
        final_df = pd.concat([df_current_raw, new_df], ignore_index=True)
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