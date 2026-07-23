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
    df = pd.read_csv("major_data.csv")
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

        st.info("👉 Part 3에서 AI 추천 알고리즘이 실행됩니다.")

# ==============================
# 학과 검색
# ==============================

elif menu == "학과 검색":

    st.header("🔍 학과 검색")

    keyword = st.text_input("학과명을 입력하세요.")

    if keyword:
        st.info("Part 8에서 검색 기능이 구현됩니다.")

# ==============================
# 학과 비교
# ==============================

elif menu == "학과 비교":

    st.header("⚖️ 학과 비교")

    st.info("Part 7에서 구현됩니다.")
