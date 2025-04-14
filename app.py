import streamlit as st
from PIL import Image
import pytesseract
import re
import gspread
from google.oauth2.service_account import Credentials
import json

# ========== CẤU HÌNH GOOGLE SHEET QUA SECRETS ==========
creds_dict = json.loads(st.secrets["credentials"])
sheet_id = st.secrets["GOOGLE_SHEET_ID"]

creds = Credentials.from_service_account_info(creds_dict, scopes=[
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id).sheet1

# ========== TRÍCH THÔNG TIN TỪ ẢNH ==========
def trich_thong_tin(text):
    ma_gui = re.search(r'(EC\s?\d{2,}\s?\d+\s?\d+\s?VN)', text, re.IGNORECASE)
    nguoi_nhan = re.search(r'TO[:\-]?\s*([A-Za-zÀ-ỹ\s]+)-', text)
    sdt = re.search(r'(\d{4}[\s\-]?\d{3}[\s\-]?\d{3})', text)
    cong_ty = re.search(r'(?i)cong ty.*', text)
    dia_chi = re.search(r'\d{2,}.*Tp.*', text)

    return {
        'Mã gửi': ma_gui.group(1).strip() if ma_gui else '',
        'Người nhận': nguoi_nhan.group(1).strip() if nguoi_nhan else '',
        'SĐT': sdt.group(1).strip() if sdt else '',
        'Công ty': cong_ty.group(0).strip() if cong_ty else '',
        'Địa chỉ': dia_chi.group(0).strip() if dia_chi else ''
    }

# ========== GIAO DIỆN WEB ==========
st.title("📦 Quản lý đơn hàng từ ảnh")

uploaded_file = st.file_uploader("Tải ảnh gói hàng lên", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh bạn vừa tải lên", use_column_width=True)

    with st.spinner("🔍 Đang trích xuất thông tin..."):
        text = pytesseract.image_to_string(image, lang='vie+eng')
        data = trich_thong_tin(text)

    st.subheader("📋 Thông tin trích xuất:")
    st.json(data)

    if st.button("✅ Ghi vào Google Sheet"):
        sheet.append_row([data['Mã gửi'], data['Người nhận'], data['SĐT'], data['Công ty'], data['Địa chỉ']])
        st.success("Đã ghi dữ liệu vào Google Sheet thành công!")