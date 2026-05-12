import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정
st.set_page_config(page_title="수면 질 및 라이프스타일 분석", page_icon="🌙", layout="wide")

# 2. 데이터 로드 함수
@st.cache_data
def load_health_data(file_path):
    df = pd.read_csv(file_path)
    df = df.rename(columns={'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질'})
    return df

@st.cache_data
def load_student_data(file_path):
    df = pd.read_csv(file_path)
    # 실제 파일의 컬럼명에 맞춰 한글화 (파일 확인 후 필요시 수정)
    column_mapping = {
        'caffeine_intake': '카페인섭취',
        'alcohol_intake': '알코올섭취',
        'psqi_score': '수면불량지수',
        'exam_stress': '시험스트레스'
    }
    df = df.rename(columns=column_mapping)
    return df

# 3. 메인 로직
st.title("🌙 수면 결정 요인 분석: 직장인 vs 대학생")

FILE1 = 'Sleep_health_and_lifestyle_dataset.csv'
FILE2 = 'Student_Sleep_Exam.csv'

if os.path.exists(FILE1) and os.path.exists(FILE2):
    df_work = load_health_data(FILE1)
    df_stud = load_student_data(FILE2)

    # 탭 구성
    tab1, tab2 = st.tabs(["🏢 [Case 1] 일반인/직장인 분석", "🎓 [Case 2] 대학생 시험 기간 분석"])

    # --- 탭 1: 직장인 ---
    with tab1:
        # 상단에 모집단 수 배치
        col_info1, col_info2 = st.columns([1, 3])
        with col_info1:
            st.metric("총 모집단 수", f"{len(df_work)} 명")
        with col_info2:
            st.info("💡 일반적인 생활 패턴을 가진 직장인 및 전문직 데이터셋입니다.")

        st.divider()
        # (이후 그래프 코드들...)
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.box(df_work, x='직업', y='수면시간', color='직업', title="직업별 수면 시간 분포")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.histogram(df_work, x='수면의질', nbins=10, title="수면의 질 분포 (10점 만점)")
            st.plotly_chart(fig2, use_container_width=True)

    # --- 탭 2: 대학생 ---
    with tab2:
        # 상단에 모집단 수 배치
        col_info3, col_info4 = st.columns([1, 3])
        with col_info3:
            st.metric("총 모집단 수", f"{len(df_stud)} 명", delta="논문 기반 표본")
        with col_info4:
            st.info("💡 시험 기간 스트레스 하에 있는 대학생들을 대상으로 한 연구 데이터입니다.")

        st.divider()
        # (이후 그래프 코드들...)
        row2_c1, row2_c2 = st.columns(2)
        with row2_c1:
            fig3 = px.scatter(df_stud, x='카페인섭취', y='수면불량지수', trendline="ols",
                              title="카페인 섭취와 수면 질(PSQI) 상관관계")
            st.plotly_chart(fig3, use_container_width=True)
        with row2_c2:
            fig4 = px.density_heatmap(df_stud, x="시험스트레스", y="수면불량지수", text_auto=True,
                                      title="스트레스와 수면 불량의 관계")
            st.plotly_chart(fig4, use_container_width=True)

    with st.expander("데이터 상세 보기"):
        st.write("표본 크기 확인:", f"직장인 {len(df_work)}개 / 대학생 {len(df_stud)}개")
        st.dataframe(df_stud.head())

else:
    st.error("데이터 파일을 로드할 수 없습니다.")
