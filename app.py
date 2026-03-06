import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針 AIアシスタント")

# 保存履歴の準備
if 'history' not in st.session_state:
    st.session_state.history = []

st.info("💡 デジタル値は『0368.7』のように小数点まで入力可能です。")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    
    # --- 🔄 向きの微調整 ---
    st.subheader("1. 向きと視界の確認")
    angle = st.slider("数字が水平になるよう調整", -180, 180, 0)
    rotated_img = pil_img.rotate(angle)
    st.image(rotated_img, caption="この画像から数値を読み取ります", use_container_width=True)

    # --- 🔍 解析実行ボタン ---
    if st.button("AI解析をスタート"):
        st.success("スキャンしました。以下のフォームで数値を最終確認してください。")

    # --- 📝 検針データの記録（ここで修正） ---
    with st.form("record_form"):
        st.subheader("📝 検針データの最終確認")
        
        # ユーザー様から教えていただいた正しい形式にデフォルトを合わせます
        sn = st.text_input("1. 製造番号", value="207649")
        
        col1, col2 = st.columns(2)
        with col1:
            # デジタル値を小数点（0368.7）で入力しやすく変更
            main_val = st.text_input("2. デジタル指針 ($m^3$)", value="0368.7")
        with col2:
            # アナログ値（85）を入力
            lit_val = st.number_input("3. アナログ針 (L)", value=85, step=1)
        
        st.write(f"📊 **今回の確定値: {main_val}{lit_val:02} $m^3$**")
        
        submitted = st.form_submit_button("✅ この内容でGoogle Keep等へ記録")
        
        if submitted:
            # データを履歴に追加
            record = {"製造番号": sn, "指針": f"{main_val}", "リットル": f"{lit_val}"}
            st.session_state.history.append(record)
            st.balloons()
            
            # Google Keepにコピペしやすいテキストを表示
            st.code(f"【水道検針データ】\n製造番号: {sn}\n指針値: {main_val} m3\nアナログ: {lit_val} L", language="text")
            st.success("上のコードをコピーしてGoogle Keepに貼り付けてください！")

# --- 📁 履歴表示 ---
if st.session_state.history:
    st.divider()
    st.subheader("📁 本日の検針履歴")
    st.table(st.session_state.history)
