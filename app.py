import streamlit as st
from PIL import Image

st.set_page_config(page_title="水道検針AI", page_icon="🚰")
st.title("🚰 水道検針 記録アシスタント")

st.info("💡 小さい単位（1L）から順番に確認していくことで、繰り上がりのミスを防ぎます！")

img_file = st.file_uploader("📂 写真をアップロード", type=['png', 'jpg', 'jpeg'])

if img_file:
    st.image(img_file, caption="解析対象のメーター", use_container_width=True)

# --- 📝 渦巻き状（逆順）スロット入力 ---
with st.form("meter_pro_form"):
    st.subheader("📝 針から順番に入力してください")
    
    col1, col2 = st.columns(2)
    with col1:
        # 一番小さい単位からスタート
        analog_1 = st.number_input("1. 【1Lの針】 (0.001)", value=0, max_value=9)
        analog_10 = st.number_input("2. 【10Lの針】 (0.01)", value=0, max_value=9)
    with col2:
        red = st.number_input("3. 【赤い数字】 (0.1)", value=0, max_value=9)
        black = st.number_input("4. 【黒い数字】 (m3)", value=0, step=1)

    st.write("---")
    # 最後に製造番号で対象メーターの確認
    sn = st.text_input("5. 【製造番号】 (最後に確認)", placeholder="例：377002")

    # 🌟 自動計算（入力は逆でも、結果は正しい順番でくっつけます）
    final_val = f"{black}.{red}{analog_10}{analog_1}"
    
    st.divider()
    st.write("### 📊 確定する検針値")
    st.write(f"# **{final_val}** m³")
    
    if st.form_submit_button("✅ 確定してKeep用テキストを作る"):
        st.balloons()
        keep_format = f"【水道検針データ】\n製造番号：{sn}\n指針：{final_val} m3"
        st.code(keep_format, language="text")
        st.success("↑上の文字をコピーしてGoogle Keepに貼り付けてください！")
      
