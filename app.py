import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道メーターAI検針 (画像強化版)")

st.write("反射や影を消す『画像処理』を強化しました。本気で当てにいきます！")

img_file = st.file_uploader("📂 スマホの写真から選ぶ", type=['png', 'jpg', 'jpeg'])
camera_file = st.camera_input("📸 今すぐカメラで撮る")

input_file = img_file if img_file is not None else camera_file

if input_file:
    pil_img = Image.open(input_file)
    img_array = np.array(pil_img)
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    with st.spinner('画像をきれいに掃除して解析中...'):
        # 🌟 プロの画像処理
        # 1. グレーにして
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        # 2. 2倍に拡大（文字を認識しやすくする）
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        # 3. 二値化（影を飛ばして白黒はっきりさせる）
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # 画面にAIが見ている「加工後の画像」を表示（デバッグ用）
        st.image(gray, caption="AIが今見ている視界（白黒加工後）", use_container_width=True)
        
        # 🌟 OCR実行（数字のみを狙う設定に変えました）
        # configの指定で、数字と一部の記号以外を無視させます
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        detected_text = pytesseract.image_to_string(gray, config=custom_config)
        
        # 6桁の数字を探す
        found_numbers = re.findall(r'\d{6}', detected_text)
        
        if found_numbers:
            sn = found_numbers[0]
            st.success(f"製造番号を特定しました！")
        else:
            nums_only = "".join(filter(str.isdigit, detected_text))
            sn = nums_only[:6] if len(nums_only) >= 6 else "まだノイズが多いです..."

        st.header(f"📊 判定された製造番号: {sn}")
        
        with st.expander("🔍 AIが読み取った生の数字データ"):
            st.write(f"生データ: {detected_text}")

        if st.button("この番号で保存する"):
            st.balloons()
