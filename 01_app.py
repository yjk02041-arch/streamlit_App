import streamlit as st
import requests
import random

st.set_page_config(
    page_title="Weather Music",
    page_icon="🎵",
    layout="wide"
)

#############################
# CSS
#############################

st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#0f172a,#1e3a8a,#312e81);
color:white;
}

.big{
font-size:55px;
font-weight:700;
text-align:center;
margin-top:20px;
margin-bottom:5px;
}

.sub{
text-align:center;
font-size:20px;
color:#dddddd;
margin-bottom:40px;
}

.song-card{
padding:25px;
border-radius:25px;
color:white;
box-shadow:0 10px 30px rgba(0,0,0,.3);
margin-bottom:20px;
transition:.4s;
}

.song-card:hover{
transform:scale(1.03);
}

.song-title{
font-size:30px;
font-weight:bold;
}

.artist{
font-size:20px;
opacity:0.85;
}

.weather{
font-size:18px;
margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

#############################
# 노래 데이터
#############################

music = {

"Clear":[

{
"title":"Golden",
"artist":"Harry Styles",
"color":"#FFD54F",
"emoji":"☀️"
},

{
"title":"Sunflower",
"artist":"Post Malone",
"color":"#FBC02D",
"emoji":"🌻"
},

{
"title":"Walking on Sunshine",
"artist":"Katrina & The Waves",
"color":"#FFB300",
"emoji":"🌞"
}

],

"Clouds":[

{
"title":"Blue & Grey",
"artist":"BTS",
"color":"#607D8B",
"emoji":"☁️"
},

{
"title":"Daydream",
"artist":"J-Hope",
"color":"#90A4AE",
"emoji":"🌥️"
},

{
"title":"Paris in the Rain",
"artist":"Lauv",
"color":"#78909C",
"emoji":"🌫️"
}

],

"Rain":[

{
"title":"Rain",
"artist":"Taeyeon",
"color":"#4FC3F7",
"emoji":"🌧️"
},

{
"title":"Umbrella",
"artist":"Rihanna",
"color":"#0288D1",
"emoji":"☔"
},

{
"title":"Through the Rain",
"artist":"Mariah Carey",
"color":"#29B6F6",
"emoji":"💧"
}

],

"Snow":[

{
"title":"Snowman",
"artist":"Sia",
"color":"#B3E5FC",
"emoji":"❄️"
},

{
"title":"White Winter Hymnal",
"artist":"Fleet Foxes",
"color":"#E1F5FE",
"emoji":"☃️"
},

{
"title":"Winter Bear",
"artist":"V",
"color":"#BBDEFB",
"emoji":"🩵"
}

],

"Thunderstorm":[

{
"title":"Thunder",
"artist":"Imagine Dragons",
"color":"#673AB7",
"emoji":"⚡"
},

{
"title":"Electric Love",
"artist":"BØRNS",
"color":"#512DA8",
"emoji":"🌩️"
}

]

}

#############################
# 타이틀
#############################

st.markdown('<div class="big">🎵 Weather Melody</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">오늘의 날씨에 어울리는 음악을 추천합니다.</div>', unsafe_allow_html=True)

city = st.text_input("도시 이름 입력", "Seoul")

#############################
# API
#############################

API_KEY = st.secrets["OPENWEATHER_API_KEY"]

if st.button("🎧 추천받기"):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    res = requests.get(url)

    if res.status_code == 200:

        data = res.json()

        weather = data["weather"][0]["main"]

        temp = data["main"]["temp"]

        icon = data["weather"][0]["icon"]

        st.image(f"https://openweathermap.org/img/wn/{icon}@2x.png", width=100)

        st.success(f"현재 날씨 : {weather} | {temp:.1f}℃")

        if weather not in music:
            weather="Clouds"

        song = random.choice(music[weather])

        st.markdown(f"""
        <div class="song-card" style="background:{song['color']};">

        <div style="font-size:60px;">
        {song['emoji']}
        </div>

        <div class="song-title">
        {song['title']}
        </div>

        <div class="artist">
        {song['artist']}
        </div>

        <div class="weather">
        오늘 날씨 : {weather}
        </div>

        </div>

        """, unsafe_allow_html=True)

        st.balloons()

    else:

        st.error("도시를 찾을 수 없습니다.")
