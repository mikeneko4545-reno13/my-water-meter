import streamlit as st
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針 記録アシスタント")

st.info("💡 1181.283 のような複雑な数字も、見たまま入れるだけで自動計算します！")

# 写真のアップロード（固定値に惑わされないよう毎回クリア）
img_file = st.file_uploader("📂 写真をアップロード", type=['png', 'jpg', 'jpeg'], key="meter_up")

if img_file:
    st.image(img_file, caption="解析対象のメーター", use_container_width=True)

# --- 📝 5項目スロット入力 ---
with st.form("meter_pro_form"):
    st.subheader("📝 メーターの見た目通りに入力")
    
    # 1. 製造番号（固定値 207649 はもう出ません）
    sn = st.text_input("1. 製造番号", placeholder="例：377002")
    
    st.write("--- 指針値の入力 ---")
    col1, col2 = st.columns(2)
    with col1:
        # 1181 の部分
        black = st.number_input("2. 黒い数字 (m3)", value=0, step=1)
        # 2 の部分
        red = st.number_input("3. 赤い数字 (0.1)", value=0, max_value=9)
    with col2:
        # 8 の部分
        analog_10 = st.number_input("4. 10Lの針 (0.01)", value=0, max_value=9)
        # 3 の部分
        analog_1 = st.number_input("5. 1Lの針 (0.001)", value=0, max_value=9)

    # 🌟 自動計算： 1181 + .2 + .08 + .003 = 1181.283
    final_val = f"{black}.{red}{analog_10}{analog_1}"
    
    st.divider()
    st.write("### 📊 確定する検針値")
    st.write(f"# **{final_val}** m³")
    
    if st.form_submit_button("✅ 確定してKeep用テキストを作る"):
        st.balloons()
        # Google Keepにそのまま貼れる形式
        keep_format = f"【水道検針データ】\n製造番号：{sn}\n指針：{final_val} m3"
        st.code(keep_format, language="text")
        st.success("↑上の文字をコピーしてGoogle Keepに貼り付けてください！")
                
