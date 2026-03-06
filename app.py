import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道メーターAI検針 (軽量安定版)")

st.write("軽量AI（Tesseract）に切り替えました。これならサクサク動きます！")

# 📸 写真の入力
img_file = st.file_uploader("📂 スマホの写真から選ぶ", type=['png', 'jpg', 'jpeg'])
camera_file = st.camera_input("📸 今すぐカメラで撮る")

input_file = img_file if img_file is not None else camera_file

if input_file:
    pil_img = Image.open(input_file)
    img_array = np.array(pil_img)
    
    # AIが読みやすいように画像を加工
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    st.image(pil_img, caption="解析対象の写真", use_container_width=True)
    
    with st.spinner('AIが文字を読み取っています...'):
        # 🌟 軽量OCR（Tesseract）を実行
        detected_text = pytesseract.image_to_string(gray, config='--psm 11')
        
        # 数字だけを抽出
        nums = "".join(filter(str.isdigit, detected_text))
        sn = nums if len(nums) >= 5 else "数字が見つかりません"

        st.success("解析完了！")
        st.header(f"📊 判定された製造番号: {sn}")
        
        with st.expander("🔍 AIが見た生のデータ"):
            st.code(detected_text if detected_text.strip() else "文字が検出されませんでした")
