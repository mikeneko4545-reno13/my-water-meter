import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針 AIアシスタント")

st.info("💡 AIが間違えた『4』や『9』は無視して、正しい数字を打ち込んでください。")

img_file = st.file_uploader("📂 写真をアップロード", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    
    # 🔄 回転調整
    angle = st.slider("数字を水平に回転", -180, 180, 0)
    rotated_img = pil_img.rotate(angle)
    st.image(rotated_img, caption="解析対象", use_container_width=True)

    if st.button("🔍 AIで数字をスキャン"):
        # 画像処理（エッジ強調）
        gray = cv2.cvtColor(np.array(rotated_img), cv2.COLOR_RGB2GRAY)
        processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # OCR実行
        detected = pytesseract.image_to_string(processed, config='--psm 11')
        st.session_state.raw_nums = re.findall(r'\d+', detected)
        st.write("AIが見つけた数字の破片:", st.session_state.raw_nums)

    # --- 📝 確定入力フォーム ---
    with st.form("meter_form"):
        st.subheader("📝 正しい検針値を入力")
        
        # 製造番号
        sn = st.text_input("1. 製造番号 (例: 377002)", value="")
        
        # 指針値の分解入力
        col1, col2 = st.columns(2)
        with col1:
            black_digit = st.number_input("2. 黒数字 (m3)", value=0, step=1)
            red_digit = st.number_input("3. 赤い字 (.1)", value=0, max_value=9)
        with col2:
            ten_l = st.number_input("4. 10L針 (8)", value=0, max_value=9)
            one_l = st.number_input("5. 1L針 (3)", value=0, max_value=9)
            
        # 計算結果のプレビュー
        total_val = f"{black_digit}.{red_digit}{ten_l}{one_l}"
        st.markdown(f"### 📊 今回の確定値: **{total_val}** $m^3$")
        
        if st.form_submit_button("✅ この内容でGoogle Keepへ送信形式で保存"):
            st.balloons()
            # 整理されたテキストをコードブロックで表示
            result_text = f"【水道検針完了】\n■製造番号: {sn}\n■検針値: {total_val} m3\n(内訳: {black_digit}.{red_digit} + {ten_l}{one_l}L)"
            st.code(result_text, language="text")
            st.success("上の文字をコピーしてGoogle Keepに貼り付けてください！")
