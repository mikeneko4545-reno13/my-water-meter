import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 🔑 Gemini APIの設定 ---
GOOGLE_API_KEY = "AIzaSyBQHs3k78USv4mum1gWNPcQnR2IvLUk2dY"
genai.configure(api_key=GOOGLE_API_KEY)

# モデル名を 'models/gemini-1.5-flash' に変更（これが一番確実です）
model = genai.GenerativeModel('models/gemini-1.5-flash')

st.set_page_config(page_title="Gemini 水道検針AI", page_icon="🤖")
st.title("🤖 Gemini 3 搭載・高精度検針")

st.info("💡 1L針から順番に読み取る「渦巻きロジック」をAIに教えてあります！")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    st.image(pil_img, caption="解析対象の画像", use_container_width=True)

    if st.button("🔍 Gemini 3 で解析実行"):
        with st.spinner('Geminiがメーターを熟考中...'):
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='JPEG')
            img_data = img_byte_arr.getvalue()

            # AIへの詳細な指示
            prompt = """
            You are a professional water meter reader. 
            Analyze the image and extract the following 4 values:
            1. 1L Dial (Smallest red needle): 0-9
            2. 10L Dial (Red needle): 0-9
            3. Red Digit (0.1 position): 0-9
            4. Black Digits (Main m3 reading): 4 or 5 digits

            Rules:
            - Ignore the engraved serial number.
            - Focus on the circular dials and the rotating numbers.
            - If a digit is between two numbers, pick the smaller one unless it's a clear carry-over.

            Format your response exactly like this:
            Black: [number]
            Red: [number]
            10L: [number]
            1L: [number]
            """

            response = model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': img_data}])
            st.markdown("### 🤖 AIの判定結果")
            st.code(response.text)
            st.success("↑この結果を下のフォームに入力・確認してください。")

# --- 📝 最終確認フォーム（渦巻きロジック） ---
with st.form("final_confirm"):
    st.subheader("📝 最終確認（小さい単位から順に）")
    col1, col2 = st.columns(2)
    with col1:
        v1 = st.number_input("1. 【1Lの針】", value=0, max_value=9)
        v10 = st.number_input("2. 【10Lの針】", value=0, max_value=9)
    with col2:
        v_red = st.number_input("3. 【赤い数字】", value=0, max_value=9)
        v_black = st.number_input("4. 【黒い数字】", value=0, step=1)
    
    final_val = f"{v_black}.{v_red}{v10}{v1}"
    st.write(f"## 📊 確定指針: **{final_val}** m³")
    
    if st.form_submit_button("✅ 確定して保存用テキスト作成"):
        st.balloons()
        st.code(f"【水道検針データ】\n指針：{final_val} m3", language="text")
