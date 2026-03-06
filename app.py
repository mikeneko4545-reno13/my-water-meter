import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 🔑 Gemini APIの設定 ---
# 先ほど保存したキーをここに入れてください
GOOGLE_API_KEY = "AIzaSyBQHs3k78USv4mum1gWNPcQnR2IvLUk2dY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # Gemini 3相当の最新モデル

st.set_page_config(page_title="Gemini 水道検針AI", page_icon="🤖")
st.title("🤖 Gemini 3 搭載・高精度検針")

st.info("💡 OPPO Reno13のカメラで撮った写真をGeminiがプロの目で解析します。")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    st.image(pil_img, caption="解析中の画像", use_container_width=True)

    if st.button("🔍 Gemini 3 で超高精度スキャン"):
        with st.spinner('Geminiがメーターを熟考しています...'):
            # 画像をAIが読める形式に変換
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='JPEG')
            img_data = img_byte_arr.getvalue()

            # --- 🧠 AIへの指示（プロンプト） ---
            # あなたの「渦巻きロジック」をAIに命令として組み込みました！
            prompt = """
            # --- 🧠 AIへの指示（プロンプトをより具体的に！） ---
            prompt = """
            あなたは超一流の水道検針員です。画像から数値を【正確に】読み取ってください。
            
            【読み取りのルール】
            - 黒い回転数字（m3単位）: 左側の大きな5桁（または4桁）の数字です。
            - 赤い回転数字（0.1の位）: 黒い数字の右隣にある、赤い枠の数字1桁です。
            - 10Lの赤い針（0.01の位）: 右下にある小さな円形メーターの針が指す数字です。
            - 1Lの赤い針（0.001の位）: さらに右下にある、一番小さな円形メーターの針が指す数字です。
            
            【注意】
            - 金属部分に彫られた「製造番号」は、指針値ではないので絶対に無視してください。
            - 繰り上がり（数字が半分しか見えない場合）は、針の位置から判断してください。

            【回答形式】※必ずこの形式を守ってください
            黒数字:xxxx
            赤数字:x
            10L針:x
            1L針:x
            

            # AIに解析を依頼
            response = model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': img_data}])
            res_text = response.text
            st.write("--- AIの解析思考 ---")
            st.write(res_text)

            # --- 📝 自動入力フォームへの反映（簡易抽出） ---
            # 解析結果から数字を抜き出す処理（後ほどさらに洗練させましょう）
            st.success("解析完了！下のフォームで最終確認してください。")

# --- 📝 確定入力フォーム（昨日作った使いやすい形を維持） ---
with st.form("final_confirm"):
    st.subheader("📝 最終確認と修正")
    col1, col2 = st.columns(2)
    with col1:
        v1 = st.number_input("1. 【1Lの針】", value=0, max_value=9)
        v10 = st.number_input("2. 【10Lの針】", value=0, max_value=9)
    with col2:
        v_red = st.number_input("3. 【赤い数字】", value=0, max_value=9)
        v_black = st.number_input("4. 【黒い数字】", value=0, step=1)
    
    final_val = f"{v_black}.{v_red}{v10}{v1}"
    st.write(f"### 📊 確定検針値: **{final_val}** m³")
    
    if st.form_submit_button("✅ 確定して保存"):
        st.balloons()
        st.code(f"【検針完了】\n指針：{final_val} m3")
