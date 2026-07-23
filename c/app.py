import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# 페이지 설정
# ==============================
st.set_page_config(
    page_title="AI 대학교 학과 추천",
    page_icon="🎓",
    layout="wide"
)

# ==============================
# 제목
# ==============================
st.title("🎓 AI 대학교 학과 추천 시스템")

st.markdown("""
MBTI와 관심 분야, 좋아하는 과목을 선택하면
가장 적합한 학과를 추천해드립니다.

---
""")

# ==============================
# 사이드바
# ==============================
st.sidebar.title("📌 메뉴")

menu = st.sidebar.radio(
    "선택",
    [
        "학과 추천",
        "학과 검색",
        "학과 비교"
    ]
)

# ==============================
# 기본 데이터
# ==============================

mbti_list = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]

interest_list = [
    "생명과학",
    "화학",
    "물리",
    "수학",
    "컴퓨터",
    "AI",
    "의학",
    "환경",
    "전자",
    "기계",
    "건축",
    "디자인",
    "예술",
    "음악",
    "심리",
    "교육",
    "경제",
    "경영",
    "법",
    "사회"
]

subject_list = [
    "국어",
    "영어",
    "수학",
    "생명과학",
    "화학",
    "물리학",
    "지구과학",
    "정보",
    "사회",
    "한국사",
    "미술",
    "음악"
]

# ==============================
# 학과 데이터
# (Part2에서 계속 추가)
# ==============================

major_data = []

# ==============================
# 메인 화면
# ==============================
# ==============================
# 데이터 불러오기
# ==============================

try:
    df = pd.read_excel("major_data.xlsx")
except FileNotFoundError:
    st.error("major_data.csv 파일을 찾을 수 없습니다.")
    st.stop()
# ==============================
# 학과 추천 화면
# ==============================

if menu == "학과 추천":

    st.header("📝 나에게 맞는 학과 찾기")

    st.write("아래 정보를 입력한 후 **'학과 추천받기'** 버튼을 눌러주세요.")

    col1, col2 = st.columns(2)

    with col1:
        selected_mbti = st.selectbox(
            "🧑 MBTI",
            mbti_list
        )

        selected_interests = st.multiselect(
            "🔬 관심 분야 (최대 3개)",
            interest_list,
            max_selections=3
        )

    with col2:
        selected_subjects = st.multiselect(
            "📚 좋아하는 과목 (최대 3개)",
            subject_list,
            max_selections=3
        )

    st.divider()

    recommend_btn = st.button(
        "🎓 학과 추천받기",
        type="primary",
        use_container_width=True
    )

    # ----------------------------
    # 입력값 확인
    # ----------------------------
    if recommend_btn:

        if len(selected_interests) == 0:
            st.warning("관심 분야를 최소 1개 선택해주세요.")
            st.stop()

        if len(selected_subjects) == 0:
            st.warning("좋아하는 과목을 최소 1개 선택해주세요.")
            st.stop()

        st.success("입력이 완료되었습니다!")

        st.subheader("입력한 정보")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("MBTI", selected_mbti)

        with col2:
            st.write("**관심 분야**")
            for item in selected_interests:
                st.write(f"• {item}")

        with col3:
            st.write("**좋아하는 과목**")
            for item in selected_subjects:
                st.write(f"• {item}")

# ====================================
# 추천 결과 출력
# ====================================

recommendations = recommend_majors(
    df,
    selected_mbti,
    selected_interests,
    selected_subjects
)

st.divider()

st.subheader("🎯 추천 학과 TOP 5")

chart_data = []

for i, major in enumerate(recommendations):

    st.markdown(f"## {i+1}. {major['major']}")

    st.progress(int(major["score"]))

    st.write(f"**적합도 : {major['score']}점**")

    st.write("### 추천 이유")

    if len(major["reason"]) == 0:

        st.write("- 추천 근거가 부족합니다.")

    else:

        for reason in major["reason"]:
            st.write(f"- {reason}")

with st.expander(f"📖 {major['major']} 상세 정보 보기"):

    st.write("### 📚 학과 소개")
    st.write(major["description"])

    st.write("### 📖 배우는 과목")

    if major["subjects"] != "":
        for subject in str(major["subjects"]).split(";"):
            st.write(f"- {subject}")

    st.write("### 💡 필요한 역량")

    if major["ability"] != "":
        for ability in str(major["ability"]).split(";"):
            st.write(f"- {ability}")

    st.write("### 🏫 개설 대학")

    if major["universities"] != "":
        for university in str(major["universities"]).split(";"):
            st.write(f"- {university}")

chart_data.append(
    {
        "학과": major["major"],
        "적합도": major["score"]
    }
)

st.divider()

chart_df = pd.DataFrame(chart_data)

fig = px.bar(
    chart_df,
    x="학과",
    y="적합도",
    text="적합도",
    title="추천 학과 적합도 비교"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==============================
# 학과 검색
# ==============================

elif menu == "학과 검색":

    st.header("🔍 학과 검색")

    keyword = st.text_input(
        "검색할 학과명을 입력하세요."
    )

    if keyword:

        result = df[
            df["major"].str.contains(
                keyword,
                case=False,
                na=False
            )
        ]

        if len(result) == 0:

            st.warning("검색 결과가 없습니다.")

        else:

            st.success(f"{len(result)}개의 학과를 찾았습니다.")

            for _, row in result.iterrows():

                with st.expander(row["major"]):

                    st.write("### 📚 학과 소개")
                    st.write(row["description"])

                    st.write("### 📖 배우는 과목")

                    if row["subjects"] != "":
                        for subject in str(row["subjects"]).split(";"):
                            st.write(f"- {subject}")

                    st.write("### 💡 필요한 역량")

                    if row["ability"] != "":
                        for ability in str(row["ability"]).split(";"):
                            st.write(f"- {ability}")

                    st.write("### 🏫 개설 대학")

                    if row["universities"] != "":
                        for university in str(row["universities"]).split(";"):
                            st.write(f"- {university}")

# ==============================
# 학과 비교
# ==============================

elif menu == "학과 비교":

    st.header("⚖️ 학과 비교")

    major_list = sorted(df["major"].unique())

    col1, col2 = st.columns(2)

    with col1:
        major1 = st.selectbox(
            "첫 번째 학과",
            major_list,
            key="major1"
        )

    with col2:
        major2 = st.selectbox(
            "두 번째 학과",
            major_list,
            index=1 if len(major_list) > 1 else 0,
            key="major2"
        )

    if major1 == major2:
        st.warning("서로 다른 학과를 선택해주세요.")
    else:

        row1 = df[df["major"] == major1].iloc[0]
        row2 = df[df["major"] == major2].iloc[0]

        st.divider()

        compare_df = pd.DataFrame({

            "항목": [
                "학과 소개",
                "추천 MBTI",
                "관심 분야",
                "좋아하는 과목",
                "배우는 과목",
                "필요한 역량",
                "개설 대학"
            ],

            major1: [
                row1["description"],
                row1["mbti"],
                row1["interest"],
                row1["subject"],
                row1["subjects"],
                row1["ability"],
                row1["universities"]
            ],

            major2: [
                row2["description"],
                row2["mbti"],
                row2["interest"],
                row2["subject"],
                row2["subjects"],
                row2["ability"],
                row2["universities"]
            ]

        })

        st.dataframe(
            compare_df,
            use_container_width=True,
            hide_index=True
        )
###
# ==========================================================
# 데이터 불러오기
# ==========================================================

@st.cache_data
def load_data():

    try:
        df = pd.read_excel("major_data.xlsx")

    except FileNotFoundError:
        st.error("major_data.xlsx 파일이 없습니다.")
        st.stop()

    required_columns = [
        "major",
        "description",
        "mbti",
        "interest",
        "subject",
        "subjects",
        "ability",
        "universities"
    ]

    for column in required_columns:

        if column not in df.columns:

            st.error(f"'{column}' 컬럼이 없습니다.")

            st.stop()

    return df.fillna("")


df = load_data()
# ==========================================================
# 추천 점수 계산
# ==========================================================

def calculate_score(row, user_mbti, user_interest, user_subject):

    score = 0
    reasons = []

    # -------------------------
    # MBTI
    # -------------------------
    major_mbti = str(row["mbti"]).split(";")

    if user_mbti in major_mbti:
        score += 30
        reasons.append(f"{user_mbti} 성향과 잘 맞습니다.")

    # -------------------------
    # 관심분야
    # -------------------------
    major_interest = str(row["interest"]).split(";")

    matched_interest = []

    for interest in user_interest:

        if interest in major_interest:
            score += 20
            matched_interest.append(interest)

    if matched_interest:
        reasons.append(
            "관심 분야가 일치합니다. (" +
            ", ".join(matched_interest) +
            ")"
        )

    # -------------------------
    # 좋아하는 과목
    # -------------------------
    major_subject = str(row["subject"]).split(";")

    matched_subject = []

    for subject in user_subject:

        if subject in major_subject:
            score += 15
            matched_subject.append(subject)

    if matched_subject:
        reasons.append(
            "좋아하는 과목이 일치합니다. (" +
            ", ".join(matched_subject) +
            ")"
        )

    if score > 100:
        score = 100

    return score, reasons
    # ==========================================================
# 추천 학과 계산
# ==========================================================

def recommend_majors(df, mbti, interests, subjects):

    result = []

    for _, row in df.iterrows():

        score, reasons = calculate_score(
            row,
            mbti,
            interests,
            subjects
        )

        result.append({

            "major": row["major"],

            "score": score,

            "reason": reasons,

            "description": row["description"],

            "subjects": row["subjects"],

            "ability": row["ability"],

            "universities": row["universities"]

        })

    result = sorted(
        result,
        key=lambda x: x["score"],
        reverse=True
    )

    return result[:5]
    
