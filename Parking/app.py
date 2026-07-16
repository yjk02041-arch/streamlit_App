import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="서울시 공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

# ===============================
# 제목
# ===============================
st.title("🅿️ 서울시 공영주차장 안내 시스템")
st.markdown("""
서울시 공영주차장 정보를 지도에서 확인하고,
가장 저렴한 주차장을 추천받을 수 있습니다.
""")

# ===============================
# 사이드바
# ===============================
st.sidebar.title("메뉴")

uploaded_file = st.sidebar.file_uploader(
    "CSV 업로드",
    type=["csv"]
)

DEFAULT_FILE = "서울시 공영주차장 안내 정보 (1).csv"

# ===============================
# 데이터 불러오기
# ===============================

@st.cache_data
def load_data(file):

    try:
        df = pd.read_csv(file, encoding="cp949")
    except:
        try:
            df = pd.read_csv(file, encoding="utf-8")
        except:
            df = pd.read_csv(file)

    return df


if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    try:
        df = load_data(DEFAULT_FILE)
    except:
        st.warning("CSV를 업로드해주세요.")
        st.stop()

# ===============================
# 데이터 전처리
# ===============================

df = df.copy()

numeric_cols = [
    "기본 주차 요금",
    "추가 단위 요금",
    "일 최대 요금",
    "월 정기권 금액",
    "총 주차면",
    "위도",
    "경도"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "")
            .replace("nan", np.nan)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["위도", "경도"])

# ===============================
# 자치구 추출
# ===============================

def get_gu(address):

    try:
        return address.split()[1]
    except:
        return "기타"

df["자치구"] = df["주소"].apply(get_gu)

# ===============================
# 사이드바 필터
# ===============================

st.sidebar.header("검색")

district = st.sidebar.selectbox(
    "자치구 선택",
    ["전체"] + sorted(df["자치구"].unique())
)

keyword = st.sidebar.text_input(
    "주차장 이름 검색"
)

free_only = st.sidebar.checkbox("무료 주차장")

night_free = st.sidebar.checkbox("야간 무료")

weekend_free = st.sidebar.checkbox("토요일 무료")

holiday_free = st.sidebar.checkbox("공휴일 무료")

# ===============================
# 필터 적용
# ===============================

filtered = df.copy()

if district != "전체":
    filtered = filtered[
        filtered["자치구"] == district
    ]

if keyword != "":
    filtered = filtered[
        filtered["주차장명"]
        .str.contains(keyword,
                      case=False,
                      na=False)
    ]

if free_only:

    filtered = filtered[
        filtered["유무료구분명"]
        == "무료"
    ]

if night_free:

    filtered = filtered[
        filtered["야간무료개방여부명"]
        == "무료개방"
    ]

if weekend_free:

    filtered = filtered[
        filtered["토요일 유,무료 구분명"]
        == "무료"
    ]

if holiday_free:

    filtered = filtered[
        filtered["공휴일 유,무료 구분명"]
        == "무료"
    ]

st.sidebar.success(
    f"검색 결과 : {len(filtered)}개"
)

# ===============================
# 지도 생성
# ===============================

center_lat = filtered["위도"].mean()
center_lon = filtered["경도"].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# ===============================
# 추천 주차장
# ===============================

st.subheader("💰 가장 저렴한 주차장")

recommend = filtered.copy()

recommend = recommend.dropna(
    subset=["기본 주차 요금"]
)

recommend = recommend.sort_values(
    "기본 주차 요금"
)

if len(recommend):

    best = recommend.iloc[0]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "주차장",
        best["주차장명"]
    )

    c2.metric(
        "기본요금",
        f'{int(best["기본 주차 요금"]):,}원'
    )

    c3.metric(
        "자치구",
        best["자치구"]
    )

else:

    st.info("추천할 주차장이 없습니다.")

st.divider()

st.subheader("🗺 지도")
# ==========================================
# Part 2
# 지도 마커 및 상세 정보
# ==========================================

for _, row in filtered.iterrows():

    popup_html = f"""
    <div style="width:300px">

    <h4>{row['주차장명']}</h4>

    <b>주소</b><br>
    {row['주소']}<br><br>

    <b>기본요금</b><br>
    {row['기본 주차 요금']:,}원<br><br>

    <b>기본시간</b><br>
    {row['기본 주차 시간(분 단위)']}분<br><br>

    <b>추가요금</b><br>
    {row['추가 단위 요금']:,}원
    ({row['추가 단위 시간(분 단위)']}분)<br><br>

    <b>일 최대요금</b><br>
    {row['일 최대 요금']:,}원<br><br>

    <b>월 정기권</b><br>
    {row['월 정기권 금액']:,}원<br><br>

    <b>총 주차면</b><br>
    {row['총 주차면']}면<br><br>

    <b>무료 여부</b><br>
    {row['유무료구분명']}<br><br>

    <b>야간 무료</b><br>
    {row['야간무료개방여부명']}<br><br>

    <b>토요일</b><br>
    {row['토요일 유,무료 구분명']}<br><br>

    <b>공휴일</b><br>
    {row['공휴일 유,무료 구분명']}<br><br>

    <b>전화번호</b><br>
    {row['전화번호']}<br>

    </div>
    """

    if row["유무료구분명"] == "무료":
        color = "green"
    else:
        color = "blue"

    folium.Marker(
        location=[row["위도"], row["경도"]],
        popup=folium.Popup(
            popup_html,
            max_width=350
        ),
        tooltip=row["주차장명"],
        icon=folium.Icon(
            color=color,
            icon="info-sign"
        )
    ).add_to(m)

# ==========================
# 지도 출력
# ==========================

map_data = st_folium(
    m,
    width=1200,
    height=700
)

# ==========================
# 선택한 마커 정보
# ==========================

st.divider()

st.subheader("📍 선택한 주차장 정보")

clicked = map_data.get("last_object_clicked")

if clicked is not None:

    lat = clicked["lat"]
    lon = clicked["lng"]

    selected = filtered[
        (filtered["위도"] == lat)
        &
        (filtered["경도"] == lon)
    ]

    if len(selected):

        row = selected.iloc[0]

        c1, c2 = st.columns(2)

        with c1:

            st.markdown("### 기본 정보")

            st.write("주차장명 :", row["주차장명"])
            st.write("주소 :", row["주소"])
            st.write("전화 :", row["전화번호"])
            st.write("총 주차면 :", row["총 주차면"])

            st.write("무료 :", row["유무료구분명"])
            st.write("야간 무료 :", row["야간무료개방여부명"])

        with c2:

            st.markdown("### 요금 정보")

            st.write("기본요금 :", row["기본 주차 요금"], "원")

            st.write("기본시간 :",
                     row["기본 주차 시간(분 단위)"],
                     "분")

            st.write("추가요금 :",
                     row["추가 단위 요금"],
                     "원")

            st.write("추가시간 :",
                     row["추가 단위 시간(분 단위)"],
                     "분")

            st.write("일 최대요금 :",
                     row["일 최대 요금"],
                     "원")

            st.write("월 정기권 :",
                     row["월 정기권 금액"],
                     "원")

else:

    st.info("지도에서 마커를 클릭하면 상세정보가 나타납니다.")

# ==========================
# Top5 저렴한 주차장
# ==========================

st.divider()

st.subheader("🏆 가장 저렴한 주차장 TOP5")

top5 = filtered.copy()

top5 = top5.dropna(
    subset=["기본 주차 요금"]
)

top5 = top5.sort_values(
    "기본 주차 요금"
).head(5)

top5 = top5[
    [
        "주차장명",
        "자치구",
        "기본 주차 요금",
        "일 최대 요금",
        "유무료구분명"
    ]
]

st.dataframe(
    top5,
    use_container_width=True,
    hide_index=True
)

# ==========================
# 검색 결과 표
# ==========================

st.divider()

st.subheader("📋 검색 결과")

show_cols = [
    "주차장명",
    "자치구",
    "주소",
    "기본 주차 요금",
    "일 최대 요금",
    "유무료구분명",
    "야간무료개방여부명",
    "총 주차면"
]

st.dataframe(
    filtered[show_cols],
    use_container_width=True,
    hide_index=True
)
# ==========================================
# Part 3
# 통계 및 추가 기능
# ==========================================

from datetime import datetime

st.divider()
st.header("📊 통계")

# -----------------------------
# 자치구별 주차장 개수
# -----------------------------

district_count = (
    filtered["자치구"]
    .value_counts()
    .reset_index()
)

district_count.columns = ["자치구", "주차장 수"]

fig = px.bar(
    district_count,
    x="자치구",
    y="주차장 수",
    title="자치구별 공영주차장 수"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------
# 평균 요금
# -----------------------------

fee = (
    filtered
    .groupby("자치구")["기본 주차 요금"]
    .mean()
    .reset_index()
)

fee["기본 주차 요금"] = fee["기본 주차 요금"].round(0)

fig2 = px.bar(
    fee,
    x="자치구",
    y="기본 주차 요금",
    title="자치구별 평균 기본요금"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# -----------------------------
# 무료 비율
# -----------------------------

free_count = (
    filtered["유무료구분명"]
    .value_counts()
    .reset_index()
)

free_count.columns = ["구분", "개수"]

fig3 = px.pie(
    free_count,
    names="구분",
    values="개수",
    title="무료/유료 비율"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ==========================================
# 운영 중인지 확인
# ==========================================

st.divider()

st.header("🕒 운영 여부")

now = datetime.now()

current = int(
    now.strftime("%H%M")
)

today = now.weekday()

def is_open(row):

    try:

        if today < 5:

            start = int(row["평일 운영 시작시각(HHMM)"])
            end = int(row["평일 운영 종료시각(HHMM)"])

        elif today == 5:

            start = int(row["주말 운영 시작시각(HHMM)"])
            end = int(row["주말 운영 종료시각(HHMM)"])

        else:

            start = int(row["공휴일 운영 시작시각(HHMM)"])
            end = int(row["공휴일 운영 종료시각(HHMM)"])

        return start <= current <= end

    except:

        return False

filtered["현재 운영중"] = filtered.apply(
    is_open,
    axis=1
)

open_only = st.checkbox(
    "현재 운영중인 주차장만 보기"
)

if open_only:

    open_df = filtered[
        filtered["현재 운영중"]
    ]

else:

    open_df = filtered

st.write(
    f"현재 운영중인 주차장 : {len(open_df)}개"
)

st.dataframe(

    open_df[
        [
            "주차장명",
            "자치구",
            "현재 운영중",
            "기본 주차 요금",
            "주소"
        ]
    ],

    use_container_width=True,
    hide_index=True
)

# ==========================================
# 자치구 추천
# ==========================================

st.divider()

st.header("⭐ 자치구 추천")

if district != "전체":

    recommend = (
        open_df
        .sort_values("기본 주차 요금")
        .head(3)
    )

    st.success(
        f"{district} 추천 주차장 TOP3"
    )

    st.dataframe(

        recommend[
            [
                "주차장명",
                "기본 주차 요금",
                "일 최대 요금",
                "총 주차면"
            ]
        ],

        use_container_width=True,
        hide_index=True
    )

# ==========================================
# CSV 다운로드
# ==========================================

st.divider()

st.header("📥 결과 다운로드")

csv = open_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(

    label="검색 결과 CSV 다운로드",

    data=csv,

    file_name="parking_result.csv",

    mime="text/csv"
)

# ==========================================
# 데이터 요약
# ==========================================

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "총 주차장",
    len(open_df)
)

c2.metric(
    "무료",
    len(
        open_df[
            open_df["유무료구분명"]=="무료"
        ]
    )
)

c3.metric(
    "유료",
    len(
        open_df[
            open_df["유무료구분명"]=="유료"
        ]
    )
)

c4.metric(
    "평균 기본요금",
    f"{int(open_df['기본 주차 요금'].mean()):,}원"
)

st.success("분석이 완료되었습니다.")
# ==========================================
# Part 4
# 완성 및 부가 기능
# ==========================================

from math import radians, sin, cos, sqrt, atan2

st.divider()

st.header("📍 현재 위치에서 가장 가까운 주차장")

st.info(
"""
브라우저에서는 현재 위치를 직접 가져올 수 없으므로
아래에 현재 위치의 위도·경도를 입력하면 가장 가까운
주차장을 계산합니다.
"""
)

user_lat = st.number_input(
    "현재 위도",
    value=37.5665,
    format="%.6f"
)

user_lon = st.number_input(
    "현재 경도",
    value=126.9780,
    format="%.6f"
)

def distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)

    a = (
        sin(dlat/2)**2
        +
        cos(radians(lat1))
        *
        cos(radians(lat2))
        *
        sin(dlon/2)**2
    )

    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R*c


nearest = filtered.copy()

nearest["거리(km)"] = nearest.apply(

    lambda x:

    distance(

        user_lat,

        user_lon,

        x["위도"],

        x["경도"]

    ),

    axis=1

)

nearest = nearest.sort_values(
    "거리(km)"
)

st.success("가장 가까운 주차장")

st.dataframe(

    nearest[
        [
            "주차장명",
            "자치구",
            "거리(km)",
            "기본 주차 요금",
            "주소"
        ]
    ].head(5),

    use_container_width=True,

    hide_index=True

)

# ==========================================
# 데이터 요약
# ==========================================

st.divider()

st.header("📈 데이터 요약")

c1,c2,c3,c4=st.columns(4)

c1.metric(
    "전체 주차장",
    len(df)
)

c2.metric(
    "검색 결과",
    len(filtered)
)

c3.metric(
    "평균 기본요금",
    f"{filtered['기본 주차 요금'].mean():.0f}원"
)

c4.metric(
    "평균 주차면",
    f"{filtered['총 주차면'].mean():.0f}면"
)

# ==========================================
# 가장 싼 주차장 TOP10
# ==========================================

st.divider()

st.header("🏆 가장 저렴한 주차장 TOP10")

cheap = filtered.sort_values(
    "기본 주차 요금"
)

st.dataframe(

    cheap[
        [
            "주차장명",
            "자치구",
            "기본 주차 요금",
            "일 최대 요금",
            "총 주차면",
            "주소"
        ]
    ].head(10),

    use_container_width=True,

    hide_index=True

)

# ==========================================
# 가장 비싼 주차장
# ==========================================

st.divider()

st.header("💸 가장 비싼 주차장")

expensive = filtered.sort_values(
    "기본 주차 요금",
    ascending=False
)

st.dataframe(

    expensive[
        [
            "주차장명",
            "자치구",
            "기본 주차 요금",
            "일 최대 요금",
            "주소"
        ]
    ].head(10),

    use_container_width=True,

    hide_index=True

)

# ==========================================
# 자치구별 통계
# ==========================================

st.divider()

st.header("🏙 자치구별 통계")

summary = (

    filtered

    .groupby("자치구")

    .agg(

        주차장수=("주차장명","count"),

        평균요금=("기본 주차 요금","mean"),

        평균주차면=("총 주차면","mean")

    )

    .round(1)

)

st.dataframe(

    summary,

    use_container_width=True

)

# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
"""
서울시 공영주차장 안내 시스템

Streamlit + Pandas + Plotly + Folium

Made for School Project
"""
)
