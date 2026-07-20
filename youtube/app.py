import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from wordcloud import WordCloud
from konlpy.tag import Okt
import requests
import os
from PIL import Image
from io import BytesIO

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="유튜브 댓글 분석기",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 유튜브 댓글 분석기")
st.write("영상의 댓글을 분석하여 시간대별 추이, 감성분석, 워드클라우드를 제공합니다.")

# -----------------------------
# Secrets에서 API 키 가져오기
# -----------------------------
API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

# -----------------------------
# GitHub 나눔고딕 폰트 다운로드
# -----------------------------
FONT_URL = "https://raw.githubusercontent.com/사용자이름/저장소/main/fonts/NanumGothic.ttf"

FONT_PATH = "NanumGothic.ttf"

if not os.path.exists(FONT_PATH):
    response = requests.get(FONT_URL)
    with open(FONT_PATH, "wb") as f:
        f.write(response.content)

# -----------------------------
# 유튜브 주소 입력
# -----------------------------
url = st.text_input(
    "유튜브 영상 주소",
    placeholder="https://www.youtube.com/watch?v=..."
)

comment_limit = st.slider(
    "분석할 댓글 개수",
    100,
    1000,
    300,
    100
)

# -----------------------------
# Video ID 추출
# -----------------------------
def get_video_id(url):

    if "youtu.be" in url:
        return url.split("/")[-1]

    parsed = urlparse(url)

    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed.query).get("v",[None])[0]

    return None

# -----------------------------
# 영상 정보 가져오기
# -----------------------------
def get_video_info(video_id):

    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )

    response = request.execute()

    if len(response["items"]) == 0:
        return None

    return response["items"][0]

# -----------------------------
# 댓글 가져오기
# -----------------------------
def get_comments(video_id, limit=300):

    comments = []

    nextPageToken = None

    while len(comments) < limit:

        request = youtube.commentThreads().list(

            part="snippet",

            videoId=video_id,

            maxResults=100,

            pageToken=nextPageToken,

            textFormat="plainText"

        )

        response = request.execute()

        for item in response["items"]:

            c = item["snippet"]["topLevelComment"]["snippet"]

            comments.append({

                "작성자": c["authorDisplayName"],

                "댓글": c["textDisplay"],

                "좋아요": c["likeCount"],

                "작성시간": c["publishedAt"]

            })

            if len(comments) >= limit:
                break

        nextPageToken = response.get("nextPageToken")

        if nextPageToken is None:
            break

    return pd.DataFrame(comments)

# -----------------------------
# 영상 출력
# -----------------------------
if url:

    video_id = get_video_id(url)

    if video_id is None:

        st.error("올바른 유튜브 주소가 아닙니다.")

    else:

        info = get_video_info(video_id)

        if info:

            st.header(info["snippet"]["title"])

            st.image(
                info["snippet"]["thumbnails"]["high"]["url"],
                use_container_width=True
            )

            st.video(url)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "조회수",
                    format(int(info["statistics"]["viewCount"]), ",")
                )

            with col2:
                st.metric(
                    "좋아요",
                    format(int(info["statistics"].get("likeCount",0)), ",")
                )

            with col3:
                st.metric(
                    "댓글 수",
                    format(int(info["statistics"]["commentCount"]), ",")
                )

            if st.button("댓글 분석 시작"):

                with st.spinner("댓글을 불러오는 중입니다..."):

                    df = get_comments(video_id, comment_limit)

                st.success(f"{len(df)}개의 댓글을 가져왔습니다.")

                st.dataframe(df.head())

                st.session_state["comments"] = df
              # ======================================================
# Part 2 : 댓글 데이터 분석
# (Part 1 아래에 그대로 붙여넣기)
# ======================================================

if "comments" in st.session_state:

    st.divider()
    st.header("📊 댓글 데이터 분석")

    df = st.session_state["comments"].copy()

    # -----------------------------
    # 날짜 형식 변환
    # -----------------------------
    df["작성시간"] = pd.to_datetime(df["작성시간"])

    # 날짜
    df["날짜"] = df["작성시간"].dt.date

    # 시간
    df["시간"] = df["작성시간"].dt.hour

    # -----------------------------
    # 댓글 통계
    # -----------------------------
    st.subheader("댓글 요약")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "수집 댓글",
            len(df)
        )

    with col2:
        st.metric(
            "평균 좋아요",
            round(df["좋아요"].mean(), 2)
        )

    with col3:
        st.metric(
            "최대 좋아요",
            int(df["좋아요"].max())
        )

    # -----------------------------
    # 날짜별 댓글 작성 추이
    # -----------------------------
    st.subheader("📅 날짜별 댓글 작성 추이")

    daily = (
        df.groupby("날짜")
        .size()
        .reset_index(name="댓글 수")
    )

    fig = px.line(
        daily,
        x="날짜",
        y="댓글 수",
        markers=True,
        title="날짜별 댓글 작성 수"
    )

    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="댓글 수"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------
    # 시간대별 댓글 작성 추이
    # -----------------------------
    st.subheader("🕒 시간대별 댓글 작성 추이")

    hourly = (
        df.groupby("시간")
        .size()
        .reset_index(name="댓글 수")
    )

    fig2 = px.bar(
        hourly,
        x="시간",
        y="댓글 수",
        title="시간대별 댓글 수"
    )

    fig2.update_layout(
        xaxis=dict(
            tickmode="linear",
            dtick=1
        ),
        xaxis_title="시간",
        yaxis_title="댓글 수"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -----------------------------
    # 좋아요 많은 댓글 TOP10
    # -----------------------------
    st.subheader("👍 좋아요 TOP10 댓글")

    top_comments = (
        df.sort_values(
            "좋아요",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_comments[
            [
                "작성자",
                "좋아요",
                "댓글"
            ]
        ],
        use_container_width=True
    )

    # -----------------------------
    # CSV 다운로드
    # -----------------------------
    csv = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 댓글 CSV 다운로드",
        data=csv,
        file_name="youtube_comments.csv",
        mime="text/csv"
    )
  # =====================================================
# Part 3 : 댓글 감성 분석 (KcELECTRA)
# =====================================================

from transformers import pipeline

# 모델은 한 번만 로드
@st.cache_resource
def load_sentiment_model():
    return pipeline(
        "sentiment-analysis",
        model="beomi/KcELECTRA-base-v2022"
    )

classifier = load_sentiment_model()

# -----------------------------
# 감성 분석 함수
# -----------------------------
def analyze_sentiment(text):

    try:

        result = classifier(text[:512])[0]

        label = result["label"]

        score = result["score"]

        if label.upper() == "POSITIVE":
            return "긍정"

        elif label.upper() == "NEGATIVE":
            return "부정"

        else:
            return "중립"

    except:
        return "중립"


# -----------------------------
# 감성 분석
# -----------------------------
if "comments" in st.session_state:

    st.divider()

    st.header("😊 댓글 감성 분석")

    df = st.session_state["comments"].copy()

    with st.spinner("감성 분석 중입니다..."):

        df["감성"] = df["댓글"].apply(analyze_sentiment)

    st.session_state["comments"] = df

    sentiment = (
        df["감성"]
        .value_counts()
        .reset_index()
    )

    sentiment.columns = ["감성", "개수"]

    # -----------------------------
    # 통계
    # -----------------------------
    col1, col2, col3 = st.columns(3)

    positive = len(df[df["감성"] == "긍정"])
    negative = len(df[df["감성"] == "부정"])
    neutral = len(df[df["감성"] == "중립"])

    with col1:
        st.metric("😊 긍정", positive)

    with col2:
        st.metric("😐 중립", neutral)

    with col3:
        st.metric("😡 부정", negative)

    # -----------------------------
    # 막대 그래프
    # -----------------------------
    fig = px.bar(
        sentiment,
        x="감성",
        y="개수",
        color="감성",
        title="댓글 감성 분석"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------
    # 파이 차트
    # -----------------------------
    fig2 = px.pie(
        sentiment,
        names="감성",
        values="개수",
        hole=0.45,
        title="감성 비율"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -----------------------------
    # 감성별 댓글 보기
    # -----------------------------
    option = st.selectbox(
        "감성별 댓글 보기",
        ["전체", "긍정", "중립", "부정"]
    )

    if option == "전체":
        show = df

    else:
        show = df[df["감성"] == option]

    st.dataframe(
        show[
            [
                "작성자",
                "감성",
                "좋아요",
                "댓글"
            ]
        ],
        use_container_width=True
    )
  # =====================================================
# Part 4 : 한글 워드클라우드
# =====================================================

from collections import Counter

st.divider()
st.header("☁️ 댓글 워드클라우드")

# -----------------------------
# 불용어
# -----------------------------
stopwords = {
    "것","수","등","더","좀","진짜","정말","너무","오늘","이번",
    "그","저","이","저는","제가","입니다","있어요","있다","하는",
    "에서","으로","그리고","하지만","이다","있는","하는데",
    "영상","유튜브","댓글","그냥","ㅋㅋ","ㅎㅎ","ㅠㅠ","ㅜㅜ",
    "진심","완전","하나","사람","생각","때문","모두","우리",
    "니다","입니다","하세요","합니다","하세요","같아요","같다"
}

# -----------------------------
# 명사 추출
# -----------------------------
@st.cache_resource
def load_okt():
    return Okt()

okt = load_okt()

text = " ".join(df["댓글"].astype(str))

nouns = okt.nouns(text)

words = []

for word in nouns:

    if len(word) < 2:
        continue

    if word in stopwords:
        continue

    words.append(word)

counter = Counter(words)

# -----------------------------
# TOP20 단어
# -----------------------------
top20 = pd.DataFrame(
    counter.most_common(20),
    columns=["단어","빈도"]
)

st.subheader("가장 많이 사용된 단어 TOP20")

fig = px.bar(
    top20,
    x="단어",
    y="빈도",
    text="빈도",
    title="TOP20 단어"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------
# 워드클라우드
# -----------------------------
st.subheader("☁️ 워드클라우드")

wc = WordCloud(

    font_path=FONT_PATH,

    width=1200,

    height=700,

    background_color="white",

    max_words=150,

    collocations=False

).generate_from_frequencies(counter)

fig, ax = plt.subplots(figsize=(16,8))

ax.imshow(wc)

ax.axis("off")

st.pyplot(fig)

# -----------------------------
# 빈도표
# -----------------------------
with st.expander("단어 빈도 보기"):

    st.dataframe(
        top20,
        use_container_width=True
    )

# -----------------------------
# CSV 다운로드
# -----------------------------
csv = top20.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(

    "📥 단어 빈도 다운로드",

    csv,

    "word_frequency.csv",

    "text/csv"

)
# =====================================================
# Part 5-1 : 추가 분석 기능
# =====================================================

st.divider()
st.header("📈 추가 분석")

df = st.session_state["comments"].copy()

# -----------------------------
# 탭 생성
# -----------------------------
tab1, tab2, tab3 = st.tabs(
    [
        "⭐ 인기 댓글",
        "🔍 댓글 검색",
        "📏 댓글 길이 분석"
    ]
)

# =====================================================
# 인기 댓글
# =====================================================
with tab1:

    st.subheader("좋아요 TOP10 댓글")

    top10 = (
        df.sort_values(
            "좋아요",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(

        top10,

        x="좋아요",

        y="작성자",

        orientation="h",

        text="좋아요",

        hover_data=["댓글"],

        title="좋아요 TOP10"

    )

    fig.update_layout(

        yaxis=dict(

            autorange="reversed"

        )

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        top10[
            [
                "작성자",
                "좋아요",
                "댓글"
            ]
        ],
        use_container_width=True
    )

# =====================================================
# 댓글 검색
# =====================================================
with tab2:

    st.subheader("댓글 검색")

    keyword = st.text_input(
        "검색할 키워드 입력"
    )

    if keyword:

        result = df[
            df["댓글"].str.contains(
                keyword,
                case=False,
                na=False
            )
        ]

        st.write(f"검색 결과 : {len(result)}개")

        st.dataframe(
            result[
                [
                    "작성자",
                    "좋아요",
                    "댓글"
                ]
            ],
            use_container_width=True
        )

# =====================================================
# 댓글 길이 분석
# =====================================================
with tab3:

    st.subheader("댓글 길이 분석")

    df["댓글길이"] = df["댓글"].astype(str).apply(len)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "평균 길이",
            round(df["댓글길이"].mean(),1)
        )

    with col2:
        st.metric(
            "최대 길이",
            df["댓글길이"].max()
        )

    with col3:
        st.metric(
            "최소 길이",
            df["댓글길이"].min()
        )

    fig = px.histogram(

        df,

        x="댓글길이",

        nbins=30,

        title="댓글 길이 분포"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig2 = px.box(
        df,
        y="댓글길이",
        title="댓글 길이 Box Plot"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )
    
     st.error(f"댓글을 불러올 수 없습니다.\n{e}")

    return pd.DataFrame(comments)
# =====================================================
# Part 5-2 : 요일별 분석 및 최종 대시보드
# =====================================================

st.divider()
st.header("📅 댓글 활동 분석")

df = st.session_state["comments"].copy()

# ----------------------------------
# 날짜 변환
# ----------------------------------
df["작성시간"] = pd.to_datetime(df["작성시간"])

df["요일"] = df["작성시간"].dt.day_name()

weekday_map = {
    "Monday":"월",
    "Tuesday":"화",
    "Wednesday":"수",
    "Thursday":"목",
    "Friday":"금",
    "Saturday":"토",
    "Sunday":"일"
}

df["요일"] = df["요일"].map(weekday_map)

order = ["월","화","수","목","금","토","일"]

weekday = (
    df.groupby("요일")
      .size()
      .reindex(order, fill_value=0)
      .reset_index(name="댓글 수")
)

st.subheader("요일별 댓글 작성 수")

fig = px.bar(
    weekday,
    x="요일",
    y="댓글 수",
    text="댓글 수",
    color="댓글 수"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------
# 시간 × 요일 Heatmap
# ----------------------------------

st.subheader("요일/시간 활동 Heatmap")

df["시간"] = df["작성시간"].dt.hour

heat = (
    df.pivot_table(
        index="요일",
        columns="시간",
        values="댓글",
        aggfunc="count",
        fill_value=0
    )
)

heat = heat.reindex(order)

fig = px.imshow(

    heat,

    labels=dict(
        x="시간",
        y="요일",
        color="댓글 수"
    ),

    aspect="auto"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------
# 분석 결과 자동 요약
# ----------------------------------

st.divider()
st.header("📋 분석 결과 요약")

most_day = weekday.loc[
    weekday["댓글 수"].idxmax(),
    "요일"
]

most_hour = (
    df["시간"]
    .value_counts()
    .idxmax()
)

avg_like = round(df["좋아요"].mean(),2)

long_comment = df["댓글"].str.len().max()

top_word = ""

try:
    top_word = counter.most_common(1)[0][0]
except:
    top_word = "-"

st.success(
f"""
### 📊 분석 요약

- 수집한 댓글 수 : **{len(df)}개**

- 댓글이 가장 많이 작성된 요일 : **{most_day}요일**

- 댓글이 가장 활발한 시간 : **{most_hour}시**

- 평균 좋아요 수 : **{avg_like}개**

- 가장 긴 댓글 길이 : **{long_comment}자**

- 가장 많이 등장한 단어 : **{top_word}**
"""
)

# ----------------------------------
# 데이터 미리보기
# ----------------------------------

with st.expander("전체 댓글 데이터 보기"):

    st.dataframe(
        df,
        use_container_width=True
    )

# ----------------------------------
# Footer
# ----------------------------------

st.divider()

st.caption("🎬 YouTube Comment Analyzer")

st.caption("Made with Streamlit")
