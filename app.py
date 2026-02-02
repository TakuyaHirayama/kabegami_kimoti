import streamlit as st
import requests
from supabase import create_client
from datetime import datetime
from openai import OpenAI

# ===== 設定 =====
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(layout="wide")

# ===== CSS =====
st.markdown("""
<style>
body {
    background-color: #111;
}
.overlay {
    background: rgba(0,0,0,0.55);
    padding: 40px;
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌤 今日の気分で壁紙が変わるAIダイアリー")

mood = st.selectbox(
    "今日の気分は？",
    ["元気", "疲れた", "集中したい", "落ち込み気味"]
)

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Tokyo&appid={WEATHER_API_KEY}&lang=ja"
    data = requests.get(url).json()
    return data["weather"][0]["description"]

weather = get_weather()

# ===== AIコメント =====
def generate_comment(mood, weather):
    prompt = f"""
今日の気分は「{mood}」、天気は「{weather}」です。
ユーザーを優しく励ます短い日本語コメントを1文で生成してください。
"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

if st.button("AIに今日を任せる"):
    comment = generate_comment(mood, weather)

    image_url = "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"

    st.image(image_url, use_container_width=True)

    st.markdown(f"""
    <div class="overlay">
        <h2>{comment}</h2>
        <p>気分：{mood} ／ 天気：{weather}</p>
    </div>
    """, unsafe_allow_html=True)

    supabase.table("mood_logs").insert({
        "mood": mood,
        "weather": weather,
        "comment": comment,
        "created_at": datetime.now().isoformat()
    }).execute()
