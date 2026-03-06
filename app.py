import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 🔑 Gemini APIの設定（503エラー対策版） ---
GOOGLE_API_KEY = "AIzaSyBQHs3k78USv4mum1gWNPcQnR2IvLUk2dY" # ここはそのまま
# 🌟 'transport="rest"' を追加するのが解決の決め手です！
genai.configure(api_key=GOOGLE_API_KEY,transport='rest')

model = genai.GenerativeModel('gemini-1.5-flash')
st.set_page_config(page_title="Gemini 水道検針AI", page_icon="🤖")
st.title("🤖 Gemini 3 搭載・高精度検針")

st.info("💡 あなたの『渦巻きロジック』をAIに完全伝承しました！")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    st.image(pil_img, caption="解析対象の画像", use_container_width=True)

    if st.button("🔍 Gemini 3 で解析実行"):
        with st.spinner('Geminiがメーターを熟考中...'):
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='JPEG')
            img_data = img_byte_arr.getvalue()

            # --- 🧠 AIへの最強の指示（プロンプト） ---
            prompt = """
            You are a professional water meter reader. 
            Analyze the image carefully and extract exactly these 4 values using 'Vortex Logic' (Smallest to Largest):

            1. 1L Dial (Smallest analog needle at the bottom right)
            2. 10L Dial (The other analog needle)
            3. Red Digit (The first digit to the right of the main display, 0.1 position)
            4. Black Digits (The main large counter in m3)

            IMPORTANT RULES:
            - IGNORE the engraved Serial Number (it often looks like 377002 or 207649).
            - Focus only on the rotating digits and needles.
            - If a digit is between numbers, choose the lower one.

            FORMAT (Return this only):
            Black:[number]
            Red:[number]
            10L:[number]
            1L:[number]
            """

            try:
                response = model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': img_data}])
                st.markdown("### 🤖 AIの判定結果")
                st.code(response.text)
                st.success("スキャン成功！結果を下のフォームで確認してください。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- 📝 確定フォーム（渦巻きロジック） ---
with st.form("final_confirm"):
    st.subheader("📝 最終確認（小さい単位から順に）")
    col1, col2 = st.columns(2)
    with col1:
        v1 = st.number_input("1. 【1Lの針】", value=0, max_value=9)
        v10 = st.number_input("2. 【10Lの針】", value=0, max_value=9)
    with col2:
        v_red = st.number_input("3. 【赤い数字】", value=0, max_value=9)
        v_black = st.number_input("4. 【黒い数字】", value=0, step=1)
    
    # 計算式
    final_val = f"{v_black}.{v_red}{v10}{v1}"
    st.write(f"## 📊 確定指針: **{final_val}** $m^3$")
    
    if st.form_submit_button("✅ 確定して保存"):
        st.balloons()
        st.code(f"【水道検針データ】\n指針：{final_val} m3", language="text")
