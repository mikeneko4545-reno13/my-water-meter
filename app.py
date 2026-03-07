import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import re

# --- 1. APIと通信の設定 ---
try:
    # StreamlitのSecretsからキーを自動読み込み
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Secretsの設定がまだのようです。Manage appから設定してください。")
    st.stop()

# 通信方式を安定した 'rest' に固定
genai.configure(api_key=GOOGLE_API_KEY, transport='rest')

# --- 2. 2026年最新モデルの自動選択 ---
# あなたのキーで今使える「一番いいモデル」をAIに直接聞きに行きます
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # 'flash' という名前が入っている最新モデルを優先的に選びます
    target_model = next((m for m in available_models if 'flash' in m), available_models[0])
    model = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"モデルの起動に失敗しました: {e}")
    st.stop()

# --- 3. アプリの画面構成 ---
st.set_page_config(page_title="最強検針AI Gemini 3", page_icon="🤖")
st.title("🤖 最強検針AI Gemini 3")
st.caption(f"稼働中のモデル: {target_model}")

st.info("💡 1L針 → 10L針 → 赤い数字 → 黒い数字 の順に読み取ります。")

img_file = st.file_uploader("📂 メーターの写真をアップ", type=['png', 'jpg', 'jpeg'])

# 解析結果を保持するセッション状態
if 'ai_results' not in st.session_state:
    st.session_state['ai_results'] = {'Black': 0, 'Red': 0, '10L': 0, '1L': 0}

if img_file:
    pil_img = Image.open(img_file)
    st.image(pil_img, caption="スキャン対象", use_container_width=True)

    if st.button("🔍 AI解析を実行"):
        with st.spinner('Geminiが画像を精査しています...'):
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='JPEG')
            img_data = img_byte_arr.getvalue()

            # --- 🧠 AIへの指示（隠れた数字ロジック搭載） ---
            prompt = """
            あなたはプロの水道検針員です。
            以下の『渦巻きロジック』と『隠れた数字ロジック』に従って数値を抽出してください。

            1. 1L Dial (右下の小さな赤い針)
            2. 10L Dial (その隣の赤い針)
            3. Red Digit (メイン表示の右端、赤い枠の数字)
            4. Black Digits (メイン表示の左側、黒い大きな数字)

            【隠れた数字ロジック（あなたのアイデア！）】
            アナログの針において、針が数字の真上にあってその数字が『見えにくい』場合、
            その見えにくい数字こそが正解である可能性が高いです。その視点で読み取ってください。

            回答形式：
            Black:[number]
            Red:[number]
            10L:[number]
            1L:[number]
            """

            try:
                response = model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': img_data}])
                raw_text = response.text
                st.markdown("### 🤖 AIの判定結果（生データ）")
                st.code(raw_text)

                # 数値を抽出してセッションに保存
                parsed = {}
                for key in ['Black', 'Red', '10L', '1L']:
                    # 繋がった文字(Black:118Red:3等)にも対応できる特殊な検索
                    match = re.search(f'{key}:\\s*(\\d+)', raw_text)
                    parsed[key] = int(match.group(1)) if match else 0
                
                st.session_state['ai_results'] = parsed
                st.success("解析完了！下のフォームで確認してください。")

            except Exception as e:
                st.error(f"解析エラー: {e}")

# --- 4. 最終確認フォーム ---
st.divider()
with st.form("input_form"):
    st.subheader("📝 数値の最終確認")
    c1, c2 = st.columns(2)
    with c1:
        v1 = st.number_input("① 1Lの針", 0, 9, st.session_state['ai_results']['1L'])
        v10 = st.number_input("② 10Lの針", 0, 9, st.session_state['ai_results']['10L'])
    with c2:
        v_red = st.number_input("③ 赤い数字", 0, 9, st.session_state['ai_results']['Red'])
        v_black = st.number_input("④ 黒い数字", 0, 999999, st.session_state['ai_results']['Black'])
    
    result_val = f"{v_black}.{v_red}{v10}{v1}"
    
    if st.form_submit_button("✅ この値で確定"):
        st.balloons()
        st.write("### 📊 最終確定値")
        st.success(f"指針： **{result_val}** m³")
        st.code(f"【検針記録】\n指針：{result_val} m3", language="text")
