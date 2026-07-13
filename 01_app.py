import streamlit as st
import requests
import random

st.set_page_config(
    page_title="서울 날씨 음악 추천",
    page_icon="🎵",
    layout="wide"
)

# -----------------------
# CSS
# -----------------------
st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#141E30,#243B55);
color:white;
}

.title{
font-size:55px;
font-weight:bold;
text-align:center;
}

.subtitle{
text-align:center;
font-size:20px;
color:#dddddd;
margin-bottom:40px;
}

.card{
padding:30px;
border-radius:25px;
color:white;
box-shadow:0px 10px 30px rgba(0,0,0,.3);
margin-top:30px;
}

.song{
font-size:34px;
font-weight:bold;
}

.artist{
font-size:22px;
opacity:.9;
}

.weather{
font-size:18px;
margin-top:15px;
}

.temp{
font-size:22px;
font-weight:bold;
margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# 노래 데이터
# -----------------------

music = {

"Clear":[
("Golden","Harry Styles","#F4B400","☀️"),
("Sunflower","Post Malone","#FBC02D","🌻"),
("Walking on Sunshine","Katrina & The Waves","#FFA000","🌞")
],

"Clouds":[
("Blue & Grey","BTS","#607D8B","☁️"),
("Daydream","j-hope","#78909C","🌥️"),
("Paris in the Rain","Lauv","#90A4AE","🌫️")
],

"Rain":[
("Rain","태연","#42A5F5","🌧️"),
("Umbrella","Rihanna","#1976D2","☔"),
("Through the Rain","Mariah Carey","#29B6F6","💧")
],

"Snow":[
("Snowman","Sia","#B3E5FC","❄️"),
("Winter Bear","V","#BBDEFB","🩵"),
("White Winter Hymnal","Fleet Foxes","#E1F5FE","☃️")
],

"Thunderstorm":[
("Thunder","Imagine Dragons","#673AB7","⚡"),
("Electric Love","BØRNS","#512DA8","🌩️")
]

}

# -----------------------
# 서울 날씨 가져오기
# -----------------------

def get_weather():

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=37.5665&longitude=126.9780"
        "&current=temperature_2m,weather_code"
    )

    data = requests.get(url).json()

    temp = data["current"]["temperature_2m"]
    code = data["current"]["weather_code"]

    if code == 0:
        weather = "Clear"

    elif code in [1,2,3]:
        weather = "Clouds"

    elif code in [61,63,65,80,81,82]:
        weather = "Rain"

    elif code in [71,73,75,77,85,86]:
        weather = "Snow"

    elif code in [95,96,99]:
        weather = "Thunderstorm"

    else:
        weather = "Clouds"

    return weather,temp

# -----------------------
# 화면
# -----------------------

st.markdown("<div class='title'>🎵 서울 날씨 음악 추천</div>",unsafe_allow_html=True)
st.markdown("<div class='subtitle'>오늘 서울의 날씨에 어울리는 음악을 추천합니다.</div>",unsafe_allow_html=True)

if st.button("🎧 오늘의 추천 받기"):

    weather,temp = get_weather()

    title,artist,color,emoji = random.choice(music[weather])

    st.markdown(f"""
    <div class="card" style="background:{color};">

    <div style="font-size:60px;">
    {emoji}
    </div>

    <div class="song">
    {title}
    </div>

    <div class="artist">
    {artist}
    </div>

    <div class="temp">
    🌡️ {temp}°C
    </div>

    <div class="weather">
    오늘 서울의 날씨 : {weather}
    </div>

    </div>
    """,unsafe_allow_html=True)

    st.balloons()
