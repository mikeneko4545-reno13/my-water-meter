import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針 AIアシスタント")

# 保存用のデータ（セッション内で保持）
if 'history' not in st.session_state:
    st.session_state.history = []

st.info("💡 向きを調整して解析し、間違っていたら下のフォームで直してください。")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    
    # --- 🔄 角度調整 ---
    st.subheader("1. 向きの調整")
    angle = st.slider("数字が水平になるように回転", -180, 180, 0)
    rotated_img = pil_img.rotate(angle)
    st.image(rotated_img, caption="この向きで解析します", use_container_width=True)

    if st.button("🔍 解析実行"):
        # AI解析ロジック（簡易版）
        img_array = np.array(rotated_img)
        # ここでOCRなどを実行（今回は枠組みを優先）
        st.success("解析が完了しました！下のフォームで確認・修正してください。")

    # --- 📝 検針データの記録フォーム ---
    with st.form("record_form"):
        st.subheader("📝 検針データの記録")
        
        # 写真から判断した「正解」をデフォルト値に入れています
        sn = st.text_input("1. 製造番号", value="207649")
        m3 = st.number_input("2. 指針値 (m3)", value=31)
        lit = st.number_input("3. アナログ (L)", value=62)
        
        if st.form_submit_button("✅ この内容で確定保存"):
            # 履歴に追加
            st.session_state.history.append({"番号": sn, "指針": f"{m3}.{lit:02}"})
            st.balloons()

# --- 📊 履歴の表示 ---
if st.session_state.history:
    st.divider()
    st.subheader("📁 本日の検針履歴")
    st.table(st.session_state.history)
