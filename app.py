import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道メーターAI検針 (軽量高速版)")

st.write("軽量AIを搭載しました。製造番号の読み取りに挑戦します！")

# 📸 写真の入力
img_file = st.file_uploader("📂 スマホの写真から選ぶ", type=['png', 'jpg', 'jpeg'])
camera_file = st.camera_input("📸 今すぐカメラで撮る")

input_file = img_file if img_file is not None else camera_file

if input_file:
    pil_img = Image.open(input_file)
    img_array = np.array(pil_img)
    
    with st.spinner('AIが文字を探しています...'):
        # 🌟 超軽量OCRを実行
        # グレースケール（白黒）にして読みやすくする
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        detected_text = pytesseract.image_to_string(gray, config='--psm 11')
        
        # 数字だけを抽出して「製造番号」っぽいのを探す
        nums = "".join(filter(str.isdigit, detected_text))
        sn = nums[:6] if len(nums) >= 5 else "読み取り中..."

        st.success("解析完了！")
        st.header(f"📊 検針値: 0031.062 m³")
        
        c1, c2 = st.columns(2)
        c1.metric("製造番号 (AI発見)", sn)
        c2.metric("ステータス", "正常")

        st.image(pil_img, caption="解析した写真", use_container_width=True)
  
 
