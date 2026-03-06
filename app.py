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

           # --- 🧠 AIへの指示（針の読み取り強化版） ---
            prompt = """
            あなたは超精密な水道検針員です。
            画像から以下の4つの値を『渦巻きロジック』で特定してください。

            1. 【1Lの針】: メーター右下の「x1L」または「0.001」と書かれた円の中の針。
            2. 【10Lの針】: その隣の「x10L」または「0.01」と書かれた円の中の針。
            3. 【赤い数字】: 中央右側の「赤い枠」で囲まれた回転数字 (0.1の位)。
            4. 【黒い数字】: 左側の大きな5桁（または4桁）の黒い数字 (m3の位)。

            🚨 重要なルール:
            - 針が2つの数字の間にある場合は、必ず『小さい方の数字』を答えてください。
            - 針の根元ではなく、一番細い『先端』が指している数字を読んでください。
            - 金属部分の製造番号は無視してください。

            回答形式：
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
