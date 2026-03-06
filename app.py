import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針プロ・アシスタント")

st.info("💡 読み取りたい場所（デジタル文字か、真鍮の番号か）を選んでから解析してください。")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    
    # --- 🎯 解析モードの選択 ---
    mode = st.radio("何を読み取りますか？", 
                    ["製造番号 (真鍮)", "デジタル数字 (0368.7)", "アナログ針 (85)"])

    # --- 🔄 画像の回転 ---
    angle = st.slider("数字が水平になるよう調整", -180, 180, 0)
    rotated_img = pil_img.rotate(angle)
    st.image(rotated_img, caption="この画像を解析します", use_container_width=True)

    if st.button("🔍 AI解析実行"):
        img_array = np.array(rotated_img)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # --- モード別に画像処理を変える（これが精度の鍵です） ---
        if mode == "デジタル数字 (0368.7)":
            # デジタル数字はコントラストを極限まで上げる
            processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.'
        else:
            # 製造番号や針は輪郭を強調する
            processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
            
        st.image(processed, caption="AIが今見ている視界", use_container_width=True)
        detected = pytesseract.image_to_string(processed, config=config)
        st.session_state.last_result = "".join(filter(str.isprintable, detected)).strip()

    # --- 📝 修正と確定（ここで 0368.7 や 85 を入力） ---
    with st.form("confirm_form"):
        st.subheader("📝 検針データの最終確認")
        
        col1, col2 = st.columns(2)
        with col1:
            sn = st.text_input("1. 製造番号", value="207649")
            main_val = st.text_input("2. デジタル指針", value="0368.7")
        with col2:
            lit_val = st.number_input("3. アナログ値", value=85)
            
        if st.form_submit_button("✅ 確定して履歴へ保存"):
            st.balloons()
            st.success(f"保存しました: {main_val} m3 / {lit_val} L")
            # Google Keep用のテキスト作成
            st.code(f"【水道検針】\n番号: {sn}\n指針: {main_val} m3\nアナログ: {lit_val} L")
