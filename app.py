import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image

st.set_page_config(page_title="水道検針レコーダー", page_icon="🚰")
st.title("🚰 水道検針プロ・アシスタント")

st.info("💡 AIが黒い数字を下読みします。針は手入力で完璧に仕上げましょう！")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    
    # --- ✂️ AIの視界を絞る（超重要！） ---
    st.subheader("1. AIの視界を合わせる")
    st.write("製造番号などの余計な数字が入らないよう、上下をカットしてください。")
    
    # 画像の回転と切り抜き
    angle = st.slider("🔄 数字を水平に回転", -180, 180, 0)
    rotated_img = pil_img.rotate(angle)
    
    # 上下のカットスライダー
    img_height = rotated_img.height
    crop_top = st.slider("✂️ 上をカット（製造番号を隠す）", 0, int(img_height/2), 0)
    crop_bottom = st.slider("✂️ 下をカット", 0, int(img_height/2), 0)
    
    # 画像を切り抜く
    cropped_img = rotated_img.crop((0, crop_top, rotated_img.width, img_height - crop_bottom))
    st.image(cropped_img, caption="AIにはこの範囲だけを見せます", use_container_width=True)

    # AIの予測値を入れる変数
    ai_black_val = 0

    if st.button("🔍 黒い数字をAIでスキャン"):
        with st.spinner('AIがメインの数字を読んでいます...（少し重いです）'):
            img_array = np.array(cropped_img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            # 白黒をはっきりさせる
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # OCR実行
            custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
            detected_text = pytesseract.image_to_string(thresh, config=custom_config)
            
            # 見つかった数字の中で一番長いもの（=メインのm³の数字）を探す
            numbers = re.findall(r'\d+', detected_text)
            if numbers:
                longest_num = max(numbers, key=len)
                try:
                    ai_black_val = int(longest_num)
                    st.success(f"スキャン完了！ 黒い数字を【{ai_black_val}】と予測しました。下のフォームを確認してください。")
                except:
                    st.warning("うまく読めませんでした。手入力でお願いします。")
            else:
                st.warning("数字が見つかりませんでした。手入力でお願いします。")

    # --- 📝 渦巻き状スロット入力（AI予測値との連携） ---
    with st.form("hybrid_meter_form"):
        st.subheader("📝 針から順番に入力（繰り上がり防止）")
        
        col1, col2 = st.columns(2)
        with col1:
            analog_1 = st.number_input("1. 【1Lの針】 (0.001)", value=0, max_value=9)
            analog_10 = st.number_input("2. 【10Lの針】 (0.01)", value=0, max_value=9)
        with col2:
            red = st.number_input("3. 【赤い数字】 (0.1)", value=0, max_value=9)
            # 🌟 AIが見つけた数字が最初からここに入ります！
            black = st.number_input("4. 【黒い数字】 (m3)", value=ai_black_val, step=1)

        # 自動計算
        final_val = f"{black}.{red}{analog_10}{analog_1}"
        
        st.write("---")
        st.write("### 📊 確定する検針値")
        st.write(f"# **{final_val}** m³")
        
        if st.form_submit_button("✅ 確定してKeep用テキストを作る"):
            st.balloons()
            keep_format = f"【水道検針データ】\n指針：{final_val} m³"
            st.code(keep_format, language="text")
            st.success("↑上の文字をコピーしてGoogle Keepに貼り付けてください！")
