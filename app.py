import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io
import requests

# --- ตั้งค่าหน้าจอและ CSS ธีมเขียวสดใส สไตล์ 3D ---
st.set_page_config(page_title="บันทึกสุขภาพเพื่อคุณหมอ 2026", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #fef9c3 100%);
    }
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    h1 {
        font-size: 2.8rem !important;
        color: #15803d !important;
        text-shadow: 2px 2px 4px rgba(21, 128, 61, 0.15);
    }
    h2, h3 {
        font-size: 1.8rem !important;
        color: #166534 !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%);
        box-shadow: 6px 0 20px rgba(34, 197, 94, 0.15);
        min-width: 360px !important;
        border-right: 2px solid #bbf7d0;
    }
    section[data-testid="stSidebar"] h2 {
        color: #15803d !important;
        font-weight: 800 !important;
        border-bottom: 3px solid #22c55e;
        padding-bottom: 8px;
    }
    section[data-testid="stSidebar"] label {
        font-size: 19px !important;
        font-weight: bold !important;
        color: #14532d !important;
    }
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    div[data-testid="stSidebar"] div[data-baseweb="base-input"] {
        background-color: #f7fee7 !important;
        border: 2.5px solid #22c55e !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        color: #166534 !important;
        font-size: 18px !important;
    }
    /* ปุ่มสไตล์ 3D นูนสวยงาม */
    div.stButton > button {
        color: white !important;
        border: none;
        padding: 18px 28px;
        text-align: center;
        font-size: 20px !important;
        font-weight: 900 !important;
        cursor: pointer;
        border-radius: 14px;
        background: linear-gradient(135deg, #22c55e 0%, #15803d 100%);
        box-shadow: 0 6px #166534, 0 10px 20px rgba(34, 197, 94, 0.4);
        width: 100%;
        letter-spacing: 1px;
        transition: all 0.1s ease;
    }
    div.stButton > button:active {
        box-shadow: 0 2px #166534;
        transform: translateY(4px);
    }
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #047857 100%) !important;
        box-shadow: 0 5px #065f46 !important;
        width: auto;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        padding: 14px 24px;
    }
    div[data-testid="stDataEditor"] {
        border-radius: 12px;
        box-shadow: 0 6px 16px rgba(34, 197, 94, 0.12);
        border: 2px solid #bbf7d0;
    }
    </style>
""", unsafe_allow_html=True)

columns_order = ["วันที่", "เวลา / เหตุการณ์", "ความดันตัวบน (SYS)", "ความดันตัวล่าง (DIA)", "ชีพจร (BPM)", "น้ำตาลในเลือด (FBS)", "น้ำหนัก (kg)", "บันทึกเพิ่มเติม"]

# ⚠️ ลิงก์ Web App ของ Google Sheets สุขภาพ
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxA_6LR6KN7dfd2_4CjaGSE1_OPc9YzAr9V9z0YdHyXJcX_Cnyy9Ter0MpzRhtF0uZ1/exec"

def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        if not data or len(data) <= 1:
            return pd.DataFrame(columns=columns_order)
        
        header = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=header)
        for col in columns_order:
            if col not in df.columns:
                df[col] = 0 if col in ["ความดันตัวบน (SYS)", "ความดันตัวล่าง (DIA)", "ชีพจร (BPM)", "น้ำตาลในเลือด (FBS)", "น้ำหนัก (kg)"] else ""
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

st.title("🩺 บันทึกสุขภาพ & แนวโน้มเพื่อคุณหมอ 🌿")

def format_thai_date(dt_obj):
    try:
        if isinstance(dt_obj, str):
            dt_obj = pd.to_datetime(dt_obj)
        day = dt_obj.day
        month_idx = dt_obj.month
        year_th = dt_obj.year + 543
        thai_month_names = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        return f"{day} {thai_month_names[month_idx]} {year_th}"
    except:
        return str(dt_obj)

with st.sidebar.form("health_form", clear_on_submit=True):
    st.header("✨ จดบันทึกประจำวัน ✨")
    date_input = st.date_input("📅 วันที่วัด", datetime.now())
    time_label = st.text_input("⏰ เวลา / เหตุการณ์ (เช่น เช้า, เย็น, หน้ามืดฉุกเฉิน)", value="เช้า")
    sys_bp = st.number_input("❤️ ความดันตัวบน (SYS)", min_value=0, max_value=300, value=120, step=1)
    dia_bp = st.number_input("💙 ความดันตัวล่าง (DIA)", min_value=0, max_value=200, value=80, step=1)
    pulse = st.number_input("💓 ชีพจร (BPM)", min_value=0, max_value=200, value=72, step=1)
    fbs = st.number_input("🩸 น้ำตาลในเลือด (FBS)", min_value=0.0, max_value=500.0, value=100.0, step=1.0)
    weight = st.number_input("⚖️ น้ำหนัก (kg)", min_value=0.0, max_value=300.0, value=65.0, step=0.1)
    note = st.text_input("📝 หมายเหตุเพิ่มเติม")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.form_submit_button("🚀 บันทึกข้อมูลสุขภาพ 3D"):
        formatted_date = format_thai_date(date_input)
        new_row = {
            "วันที่": formatted_date,
            "เวลา / เหตุการณ์": time_label,
            "ความดันตัวบน (SYS)": sys_bp,
            "ความดันตัวล่าง (DIA)": dia_bp,
            "ชีพจร (BPM)": pulse,
            "น้ำตาลในเลือด (FBS)": fbs,
            "น้ำหนัก (kg)": weight,
            "บันทึกเพิ่มเติม": note
        }
        df_current = get_data()
        new_df = pd.DataFrame([new_row])
        final_df = pd.concat([df_current, new_df], ignore_index=True)
        save_data(final_df)
        st.success("บันทึกข้อมูลสุขภาพลง Google Sheets เรียบร้อยครับ!")
        st.rerun()

df = get_data()

for col in ["ความดันตัวบน (SYS)", "ความดันตัวล่าง (DIA)", "ชีพจร (BPM)", "น้ำตาลในเลือด (FBS)", "น้ำหนัก (kg)"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

st.subheader("📊 สรุปค่าเฉลี่ยสุขภาพล่าสุด")
if not df.empty:
    avg_sys = df["ความดันตัวบน (SYS)"].mean()
    avg_dia = df["ความดันตัวล่าง (DIA)"].mean()
    avg_fbs = df["น้ำตาลในเลือด (FBS)"].mean()
    avg_wt = df["น้ำหนัก (kg)"].mean()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="❤️ ค่าเฉลี่ยความดัน", value=f"{avg_sys:.0f}/{avg_dia:.0f} mmHg")
    kpi2.metric(label="🩸 ค่าเฉลี่ยน้ำตาล", value=f"{avg_fbs:.1f} mg/dL")
    kpi3.metric(label="⚖️ น้ำหนักเฉลี่ย", value=f"{avg_wt:.1f} kg")
    kpi4.metric(label="📋 จำนวนครั้งที่บันทึก", value=f"{len(df)} ครั้ง")
else:
    st.info("ยังไม่มีข้อมูลสุขภาพ ลองบันทึกรายการแรกทางซ้ายมือได้เลยครับ!")

st.divider()

st.subheader("📋 ตารางบันทึกข้อมูล (แก้ไข/ลบได้)")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="health_editor")
column_config = {
    "วันที่": st.column_config.TextColumn("วันที่", disabled=True),
    "เวลา / เหตุการณ์": st.column_config.TextColumn("เวลา / เหตุการณ์", disabled=True),
    "ความดันตัวบน (SYS)": st.column_config.NumberColumn("ความดันตัวบน (SYS)"),
    "ความดันตัวล่าง (DIA)": st.column_config.NumberColumn("ความดันตัวล่าง (DIA)"),
    "ชีพจร (BPM)": st.column_config.NumberColumn("ชีพจร (BPM)"),
    "น้ำตาลในเลือด (FBS)": st.column_config.NumberColumn("น้ำตาลในเลือด (FBS)"),
    "น้ำหนัก (kg)": st.column_config.NumberColumn("น้ำหนัก (kg)"),
    "บันทึกเพิ่มเติม": st.column_config.TextColumn("บันทึกเพิ่มเติม"),
}

edited_df = st.data_editor(
    df, 
    column_config=column_config,
    num_rows="dynamic", 
    use_container_width=True, 
    key="health_editor"
)

if st.button("🔄 อัปเดตและบันทึกข้อมูลใหม่"):
    for col in ["ความดันตัวบน (SYS)", "ความดันตัวล่าง (DIA)", "ชีพจร (BPM)", "น้ำตาลในเลือด (FBS)", "น้ำหนัก (kg)"]:
        edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce').fillna(0)
    
    save_data(edited_df[columns_order])
    st.success("อัปเดตข้อมูลออนไลน์เรียบร้อย!")
    st.rerun()

if not df.empty:
    st.divider()
    st.subheader("📈 กราฟแสดงแนวโน้มสุขภาพ (ให้คุณหมอดูการเปลี่ยนแปลง)")
    
    df['จุดบันทึก'] = df['วันที่'] + " [" + df['เวลา / เหตุการณ์'] + "]"
    
    tab1, tab2, tab3 = st.tabs(["❤️ ความดันโลหิต & ชีพจร", "🩸 น้ำตาลในเลือด", "⚖️ น้ำหนักตัว"])
    
    with tab1:
        fig_bp = px.line(df, x="จุดบันทึก", y=["ความดันตัวบน (SYS)", "ความดันตัวล่าง (DIA)"], markers=True, title="แนวโน้มความดันโลหิต (รวมรอบปกติและช่วงมีอาการ)")
        st.plotly_chart(fig_bp, use_container_width=True)
        
    with tab2:
        fig_fbs = px.line(df, x="จุดบันทึก", y="น้ำตาลในเลือด (FBS)", markers=True, title="แนวโน้มระดับน้ำตาลในเลือด (FBS)")
        st.plotly_chart(fig_fbs, use_container_width=True)
        
    with tab3:
        fig_wt = px.line(df, x="จุดบันทึก", y="น้ำหนัก (kg)", markers=True, title="แนวโน้มน้ำหนักตัว")
        st.plotly_chart(fig_wt, use_container_width=True)

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.drop(columns=['จุดบันทึก'], errors='ignore').to_excel(writer, index=False, sheet_name='Health_Report')
st.download_button(label="🖨️ พิมพ์รายงานสุขภาพส่งคุณหมอ (Excel)", data=buffer.getvalue(), file_name="health_report_2026.xlsx", mime="application/vnd.ms-excel")