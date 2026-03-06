import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針プロトタイプ")

st.info("💡 撮影のコツ：メーターの蓋で影を作り、正面から大きく撮ってください。")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])
camera_file = st.camera_input("📸 製造番号を撮影")

input_file = img_file if img_file is not None else camera_file

if input_file:
    pil_img = Image.open(input_file)
    img_array = np.array(pil_img)
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    with st.spinner('複数のAIアルゴリズムで照合中...'):
        # --- 画像処理の3パターン ---
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 1. 適応型二値化（光ムラ対策）
        proc1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # 2. 大津の二値化（コントラスト重視）
        _, proc2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 解析（代表してproc1を表示）
        st.image(proc1, caption="AIの解析視界（スキャン中）", use_container_width=True)
        
        # OCR実行
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        res1 = pytesseract.image_to_string(proc1, config=custom_config)
        res2 = pytesseract.image_to_string(proc2, config=custom_config)
        
        # より「もっともらしい（6桁に近い）」方を選ぶ
        nums1 = "".join(filter(str.isdigit, res1))
        nums2 = "".join(filter(str.isdigit, res2))
        
        ai_sn = nums1[:6] if len(nums1) >= 6 else (nums2[:6] if len(nums2) >= 6 else nums1)

        st.success("スキャン完了！内容を確認してください。")

        # --- 📋 入力・修正フォーム ---
        with st.form("result_form"):
            st.subheader("📝 検針データの記録")
            
            final_sn = st.text_input("1. 製造番号（AI判定）", value=ai_sn)
            
            col1, col2 = st.columns(2)
            with col1:
                main_val = st.number_input("2. 指針値 ($m^3$)", value=31)
            with col2:
                lit_val = st.number_input("3. アナログ (L)", value=62, max_value=99)
            
            submitted = st.form_submit_button("✅ この内容で保存・送信")
            
            if submitted:
                st.balloons()
                st.write(f"### 【記録完了】\n**製造番号:** {final_sn}  \n**検針値:** {main_val}.0{lit_val} $m^3$")
                st.write("※このデータは現在デモとして表示されています。")
