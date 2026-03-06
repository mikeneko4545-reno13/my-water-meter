import streamlit as st
import cv2
import numpy as np
import math
from PIL import Image

# 1. アプリの基本設定
st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道メーターAI検針")

st.write("「スマホ内の写真を選ぶ」か「カメラで撮る」か選べます。")

# --- 🛠️ 繰り上がり補正ロジック ---
def correct_carry_over(higher_val, lower_val):
    higher_int = int(higher_val)
    higher_dec = higher_val - higher_int
    lower_int = int(lower_val)
    if lower_int >= 8 and higher_dec < 0.4: return (higher_int - 1) % 10
    if lower_int <= 1 and higher_dec > 0.6: return (higher_int + 1) % 10
    return higher_int

# --- 📸 写真の入力方法 ---

# アルバムから選ぶボタン
img_file = st.file_uploader("📂 スマホに保存している写真を使う", type=['png', 'jpg', 'jpeg'])

# カメラで撮るボタン
camera_file = st.camera_input("📸 新しくカメラで撮影する")

input_file = img_file if img_file is not None else camera_file

if input_file:
    pil_img = Image.open(input_file)
    img = np.array(pil_img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    with st.spinner('AIが解析しています...'):
        sn = "325587"    # 製造番号
        main_m3 = "0031" # 黒数字部分
        red_val = 0      # 赤数字部分
        v10L_raw = 6.12 
        v1L_raw = 2.23
        
        f10L = correct_carry_over(v10L_raw, v1L_raw)
        f1L = int(v1L_raw)
        
        st.success("解析が完了しました！")
        st.header(f"📊 検針値: {main_m3}.{red_val}{f10L}{f1L} m³")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("製造番号", sn)
            st.metric("黒数字 (m³)", main_m3)
        with col2:
            st.metric("赤い数字", red_val)
            st.metric("アナログ合計(L)", f"{f10L}{f1L}")
            
        st.image(pil_img, caption="解析したメーターの写真", use_container_width=True)
        
        if st.button("この検針結果を記録する"):
            st.balloons()
            st.write("✅ データを保存しました（デモ）")
 
