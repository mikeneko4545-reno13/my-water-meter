import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import re

# --- 1. APIと通信の設定（安全・安定版） ---
# StreamlitのSecretsからキーを読み込みます
try:
    GOOGLE_API_KEY = st.secrets["AIzaSyChDJ1Ai_DSioph8ZYC8teioO718uROmKA"]
except KeyError:
    st.error("StreamlitのSecretsに 'GOOGLE_API_KEY' が設定されていません。")
    st.stop()

# 通信方式を安定した 'rest' に固定
genai.configure(api_key=GOOGLE_API_KEY, transport='rest')

# モデルを固定（安定している1.5-flashを使用）
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"モデルの起動に失敗しました: {e}")
    st.stop()

# --- 2. アプリの画面構成 ---
st.set_page_config(page_title="最強検針AI Gemini 3", page_icon="🤖")
st.title("🤖 最強検針AI Gemini 3")
st.caption("見えにくい数字ロジック搭載")

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
            # 画像の変換
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='JPEG')
            img_data = img_byte_arr.getvalue()

            # --- 🧠 AIへの指示（【重要】見えにくい数字ロジックを追加！） ---
            prompt = """
            あなたはプロの水道検針員です。
            以下の『渦巻きロジック』と『隠れた数字ロジック』に従って、画像から数値を抽出してください。

            【渦巻きロジック（読み取り順序）】
            1. 1L Dial (一番右下の小さな赤い針)
            2. 10L Dial (その隣の赤い針)
            3. Red Digit (メイン表示の右端、赤い枠の数字)
            4. Black Digits (メイン表示の左側、黒い大きな数字)

            【隠れた数字ロジック（あなたのアイデア！）】
            アナログの針（1L, 10L）において、針が数字の真上にあってその数字が『見えにくい』場合、
            その見えにくい数字こそが針が指している正解である可能性が非常に高いです。
            例えば、10L針の円で『1』の数字が針に隠れて見えにくい場合、値は『1』と判断してください。

            ※注意：金属に彫られた製造番号（Serial Number）は絶対に無視してください。
            回答は以下の形式のみで出力してください。余計な説明は不要です。

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

                # --- 📝 解析結果のパージ（エラーに強くする） ---
                # 繋がってしまった文字（例: Black:118Red:3）も分離して読み取れるように正規表現を使用
                parsed_results = {}
                patterns = {
                    'Black': r'Black:\s*(\d+)',
                    'Red': r'Red:\s*(\d+)',
                    '10L': r'10L:\s*(\d+)',
                    '1L': r'1L:\s*(\d+)'
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, raw_text)
                    if match:
                        parsed_results[key] = int(match.group(1))
                    else:
                        parsed_results[key] = 0 # 見つからない場合は0

                st.session_state['ai_results'] = parsed_results
                st.success("解析完了！下のフォームで数値を最終確認してください。")

            except Exception as e:
                st.error(f"解析中にエラーが発生しました: {e}")

# --- 3. 最終確認フォーム ---
st.divider()
with st.form("input_form"):
    st.subheader("📝 数値の最終確認")
    c1, c2 = st.columns(2)
    with c1:
        v1 = st.number_input("① 1Lの針", 0, 9, st.session_state['ai_results'].get('1L', 0))
        v10 = st.number_input("② 10Lの針", 0, 9, st.session_state['ai_results'].get('10L', 0))
    with c2:
        v_red = st.number_input("③ 赤い数字", 0, 9, st.session_state['ai_results'].get('Red', 0))
        v_black = st.number_input("④ 黒い数字", 0, 999999, st.session_state['ai_results'].get('Black', 0))
    
    # 検針値の計算
    # 0埋めをして桁数を揃える（例: 2 -> 02）
    result_val = f"{v_black}.{v_red}{v10}{v1}"
    
    if st.form_submit_button("✅ この値で確定"):
        st.balloons()
        st.write("### 📊 最終確定値")
        st.success(f"指針： **{result_val}** $m^3$")
        st.code(f"【検針記録】\n指針：{result_val} m3", language="text")
