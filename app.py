import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. APIと通信の設定 ---
# あなたのキーをここに貼り付けてください
GOOGLE_API_KEY = "AIzaSyChDJ1Ai_DSioph8ZYC8teioO718uROmKA" 

# 通信方式を安定した 'rest' に固定
genai.configure(api_key=GOOGLE_API_KEY, transport='rest')

# --- 2. 利用可能なモデルの自動検出 ---
# エラーを回避するため、あなたの環境で動くモデルを自動で見つけます
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # 'gemini-1.5-flash' か 'gemini-2.0-flash'、あるいはリストの先頭を選択
    target = ""
    for m in available_models:
        if "gemini-1.5-flash" in m: target = m; break
    if not target: target = available_models[0]
    
    model = genai.GenerativeModel(target)
except Exception as e:
    st.error(f"API接続エラー: {e}")
    st.stop()

# --- 3. アプリの画面構成 ---
st.set_page_config(page_title="最強検針AI Gemini 3", page_icon="🤖")
st.title("🤖 最強検針AI Gemini 3")
st.caption(f"現在稼働中のモデル: {target}")

st.info("💡 1L針 → 10L針 → 赤い数字 → 黒い数字 の順に読み取ります。")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

if img_file:
    pil_img = Image.open(img_file)
    st.image(pil_img, caption="スキャン対象", use_container_width=True)

    if st.button("🔍 AI解析を実行"):
        with st.spinner('Geminiが画像を精査しています...'):
            # 画像の変換
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='JPEG')
            img_data = img_byte_arr.getvalue()

          # --- 🧠 AIへの指示（思考プロセス・ステップアップ版） ---
            prompt = """
            あなたは世界一正確な水道検針員です。
            画像から、以下の手順で『思考を整理してから』数値を抽出してください。

            【思考の手順（Internal Thought Process）】
            1. 1L針の円を確認：針の先端が指している数字は？ (0-9)
            2. 10L針の円を確認：針の先端が指している数字は？ (0-9)
            3. 赤い回転数字を確認：赤い枠の中にしっかり見えている数字は？ (0.1の位)
            4. 黒い回転数字を確認：左側の大きなメイン数字は？ (m3の位)
            
            【読み取りの鉄則】
            - 針や数字が『2と3の間』にあるような場合は、原則として【小さい方の数字】を答えてください。
            - 10Lの針が指す方向を、円の目盛り（0が上、5が下）に基づいて慎重に判断してください。
            - 金属部分の製造番号（Serial Number）は、読み取り対象から除外してください。

            【最終回答形式】※必ずこの形式のみで答えてください
            Black:[数値]
            Red:[数値]
            10L:[数値]
            1L:[数値]
            """

            try:
                response = model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': img_data}])
                st.markdown("### 🤖 AIの判定結果")
                st.code(response.text)
                st.success("解析成功！下のフォームで数値を最終確認してください。")
            except Exception as e:
                st.error(f"解析中にエラーが発生しました: {e}")

# --- 4. 最終確認フォーム ---
st.divider()
with st.form("input_form"):
    st.subheader("📝 数値の最終確認")
    c1, c2 = st.columns(2)
    with c1:
        v1 = st.number_input("① 1Lの針", 0, 9, 0)
        v10 = st.number_input("② 10Lの針", 0, 9, 0)
    with c2:
        v_red = st.number_input("③ 赤い数字", 0, 9, 0)
        v_black = st.number_input("④ 黒い数字", 0, 999999, 0)
    
    # 検針値の計算
    result_val = f"{v_black}.{v_red}{v10}{v1}"
    
    if st.form_submit_button("✅ この値で確定"):
        st.balloons()
        st.write("### 📊 最終確定値")
        st.success(f"指針： **{result_val}** $m^3$")
        st.code(f"【検針記録】\n指針：{result_val} m3", language="text")
