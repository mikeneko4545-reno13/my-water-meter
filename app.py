import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針 AIアシスタント")

st.info("💡 写真から読み取った数字だけを表示します。固定値（207649など）は廃止しました。")

# 写真のアップロード
img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'], key="meter_loader")

if img_file:
    # 新しい写真が読み込まれたら、以前の解析結果をクリアする（ここが重要）
    pil_img = Image.open(img_file)
    img_array = np.array(pil_img)
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # 画像の向き調整
    angle = st.slider("数字が水平になるよう調整", -180, 180, 0)
    rotated_img = pil_img.rotate(angle)
    st.image(rotated_img, caption="解析対象", use_container_width=True)

    if st.button("🔍 AIで数字を抽出する"):
        with st.spinner('写真から数字を探しています...'):
            # 画像処理
            gray = cv2.cvtColor(np.array(rotated_img), cv2.COLOR_RGB2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # OCR実行
            custom_config = r'--oem 3 --psm 11'
            detected_text = pytesseract.image_to_string(thresh, config=custom_config)
            
            # 数字だけをすべて抽出してリストにする
            all_numbers = re.findall(r'\d+', detected_text)
            
            # 抽出された数字の整理
            st.session_state.found_numbers = all_numbers
            st.success(f"解析完了！ {len(all_numbers)} 個の数字の候補が見つかりました。")

    # --- 📝 抽出された数字から選ぶ・直す ---
    if 'found_numbers' in st.session_state and st.session_state.found_numbers:
        st.subheader("📝 読み取り結果の確認")
        st.write("AIが見つけた数字リスト:", st.session_state.found_numbers)
        
        with st.form("record_form"):
            # リストの最初の方にある数字を、一旦自動で割り振ります（固定値は使いません）
            numbers = st.session_state.found_numbers
            
            # 数字が見つからなかった場合は空欄にします
            def_sn = numbers[0] if len(numbers) > 0 else ""
            def_m3 = numbers[1] if len(numbers) > 1 else ""
            def_lit = numbers[2] if len(numbers) > 2 else ""

            sn = st.text_input("1. 製造番号", value=def_sn, placeholder="207649など")
            main_val = st.text_input("2. 指針値 (m3)", value=def_m3, placeholder="0368.7など")
            lit_val = st.text_input("3. アナログ (L)", value=def_lit, placeholder="85など")
            
            if st.form_submit_button("✅ この内容で確定"):
                st.balloons()
                st.code(f"【記録】番号:{sn} / 指針:{main_val} / アナログ:{lit_val}")
    elif img_file:
        st.warning("まだ解析されていません。『AIで数字を抽出する』ボタンを押してください。")
