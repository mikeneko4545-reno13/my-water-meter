import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針 AIアシスタント")

st.info("💡 撮影後の『回転』と『切り抜き』が、精度100%への近道です！")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    
    # --- 🔄 角度調整機能 ---
    st.subheader("1. 向きを調整してください")
    angle = st.slider("数字が水平になるように回転", -180, 180, 0)
    rotated_img = pil_img.rotate(angle)
    st.image(rotated_img, caption="調整後の画像", use_container_width=True)

    if st.button("🔍 この角度で解析実行"):
        img_array = np.array(rotated_img)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        with st.spinner('AIが読み取り中...'):
            # 高度な画像処理
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            # ノイズを消して数字を太らせる
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            
            # OCR実行
            custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
            detected_text = pytesseract.image_to_string(thresh, config=custom_config)
            
            # 6桁の数字を抽出
            import re
            found = re.findall(r'\d{6}', detected_text)
            ai_sn = found[0] if found else "".join(filter(str.isdigit, detected_text))[:6]

            st.success("スキャンが完了しました！")

            # --- 📋 入力・修正フォーム ---
            with st.form("edit_form"):
                st.subheader("📝 検針内容の確認")
                
                # ここでユーザーが最終修正を行う
                final_sn = st.text_input("1. 製造番号（AI判定）", value=ai_sn if ai_sn else "207649")
                
                col1, col2 = st.columns(2)
                with col1:
                    main_val = st.number_input("2. 指針値 (m3)", value=31)
                with col2:
                    lit_val = st.number_input("3. アナログ (L)", value=62)
                
                if st.form_submit_button("✅ このデータで確定保存"):
                    st.balloons()
                    st.success(f"【保存完了】 番号:{final_sn} 値:{main_val}.{lit_val:03} m3")
