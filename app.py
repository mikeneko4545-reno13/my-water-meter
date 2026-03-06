import streamlit as st
import cv2
import numpy as np
import easyocr
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道メーターAI検針 (精度向上版)")

# AIモデルの読み込み（一度だけ実行）
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

st.write("光の反射を抑えて、正面から撮った写真が一番当たりやすいです！")

# 📸 写真の入力
img_file = st.file_uploader("📂 スマホの写真から選ぶ", type=['png', 'jpg', 'jpeg'])
camera_file = st.camera_input("📸 今すぐカメラで撮る")

input_file = img_file if img_file is not None else camera_file

if input_file:
    pil_img = Image.open(input_file)
    img_array = np.array(pil_img)
    
    # 🌟 AIが見やすいように画像を加工（コントラスト調整）
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    # 明るい部分と暗い部分をはっきりさせる
    enhanced_img = cv2.detailEnhance(img_cv, sigma_s=10, sigma_r=0.15)
    
    st.image(pil_img, caption="解析中の画像", use_container_width=True)
    
    with st.spinner('AIが必死に数字を探しています...'):
        # 🌟 OCR実行
        results = reader.readtext(enhanced_img)
        
        # 読み取ったすべての文字をリストにする
        all_detected_texts = [res[1] for res in results]
        
        # 製造番号（数字のみ）を探すロジック
        final_sn = "見つかりません"
        for text in all_detected_texts:
            # 記号などを消して数字だけにする
            clean_num = "".join(filter(str.isdigit, text))
            if len(clean_num) >= 5: # 5桁以上の数字があれば製造番号とみなす
                final_sn = clean_num
                break
        
        st.success("解析が終わりました！")
        
        # 📊 結果表示
        st.header(f"📊 判定された製造番号: {final_sn}")
        
        with st.expander("🔍 AIが読み取った全データ（デバッグ用）"):
            st.write("AIは写真から以下の文字を見つけました：")
            st.write(all_detected_texts)

        if st.button("この番号で記録する"):
            st.balloons()
 
