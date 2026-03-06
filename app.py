import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道メーターAI検針 (プロ仕様版)")

st.write("AIの誤認を人間が修正できる機能を付けました。これで完璧なデータが残せます！")

img_file = st.file_uploader("📂 メーターの真鍮部分をアップ", type=['png', 'jpg', 'jpeg'])
camera_file = st.camera_input("📸 製造番号を正面から撮影")

input_file = img_file if img_file is not None else camera_file

if input_file:
    pil_img = Image.open(input_file)
    img_array = np.array(pil_img)
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    with st.spinner('最高精度で解析中...'):
        # 🌟 高度な画像処理
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 1. 鮮明化（シャープネス）
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharp = cv2.filter2D(gray, -1, kernel)
        
        # 2. 適応型二値化（光のムラに強い加工）
        binary = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # 3. ノイズ除去
        denoised = cv2.fastNlMeansDenoising(binary, h=30)
        
        st.image(denoised, caption="AIが読み取っている映像（加工後）", use_container_width=True)
        
        # 🌟 OCR実行（1行読み取りモード）
        # 数字と一部の記号以外を無視させます
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        detected_text = pytesseract.image_to_string(denoised, config=custom_config)
        
        # 数字だけを抽出
        nums_only = "".join(filter(str.isdigit, detected_text))
        ai_sn = nums_only[:6] if len(nums_only) >= 6 else nums_only

        st.success("解析完了！")

        # 🌟 ここが「売り物」のポイント：人間による最終確認
        st.subheader("📋 検針結果の確認・修正")
        final_sn = st.text_input("製造番号（AIの読み間違いはここで直せます）", value=ai_sn)
        
        # ダミーの検針値
        m3_val = st.number_input("メインメーター ($m^3$)", value=31)
        
        if st.button("✅ この内容で確定して保存"):
            st.balloons()
            st.info(f"保存完了：製造番号[{final_sn}] / 指針[{m3_val}]")
            # ここに将来、Excel保存やメール送信の機能を付け足せます！
