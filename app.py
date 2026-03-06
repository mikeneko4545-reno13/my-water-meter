import streamlit as st
import cv2
import numpy as np
import pytesseract
import re  # 🌟 数字を探すための特殊な道具
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道メーターAI検針 (6桁抽出版)")

st.write("AIが動きましたね！次は『6桁の製造番号』だけを狙い撃ちします。")

img_file = st.file_uploader("📂 スマホの写真から選ぶ", type=['png', 'jpg', 'jpeg'])
camera_file = st.camera_input("📸 今すぐカメラで撮る")

input_file = img_file if img_file is not None else camera_file

if input_file:
    pil_img = Image.open(input_file)
    img_array = np.array(pil_img)
    
    # AIが読みやすいように画像を加工（白黒＆くっきり）
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    # 少しぼかしを入れてノイズを消す
    gray = cv2.medianBlur(gray, 3)
    
    st.image(pil_img, caption="解析対象", use_container_width=True)
    
    with st.spinner('6桁の製造番号を探しています...'):
        # 文字読み取り
        detected_text = pytesseract.image_to_string(gray, config='--psm 11')
        
        # 🌟 ここが魔法：6桁の数字だけを抜き出す
        # (377002 のような連続した6文字の数字を探す)
        found_numbers = re.findall(r'\d{6}', detected_text)
        
        if found_numbers:
            # 最初に見つかった6桁を製造番号とする
            sn = found_numbers[0]
            st.success(f"製造番号を見つけました！")
        else:
            # 6桁で見つからない場合は、数字を全部つなげてから上から6桁取る
            nums_only = "".join(filter(str.isdigit, detected_text))
            sn = nums_only[:6] if len(nums_only) >= 6 else "読み取り中..."

        st.header(f"📊 判定された製造番号: {sn}")
        
        with st.expander("🔍 AIが見た生のデータ（中身の確認）"):
            st.write("AIが見つけたすべての文字:")
            st.code(detected_text)
            st.write("抽出された数字候補:", found_numbers)

        if st.button("この番号で保存する"):
            st.balloons()
