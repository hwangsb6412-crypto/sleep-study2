import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정
st.set_page_config(page_title="수면 및 라이프스타일 분석 대시보드", page_icon="🌙", layout="wide")

# 2. 데이터 로드 함수
@st.cache_data
def load_health_data(file_path):
    df = pd.read_csv(file_path)
    column_mapping = {
        'Occupation': '직업',
        'Sleep Duration': '수면시간',
        'Quality of Sleep': '수면의질',
        'Physical Activity Level': '운동량',
        'Stress Level': '스트레스지수',
        'BMI Category': 'BMI분류',
        'Daily Steps': '일일걸음수',
        'Sleep Disorder': '수면장애'
    }
    df = df.rename(columns=column_mapping)
    df['수면장애'] = df['수면장애'].fillna('None')
    return df

@st.cache_data
def load_efficiency_data(file_path):
    df = pd.read_csv(file_path)
    # 카페인, 알코올 데이터 한글화
    column_mapping = {
        'Caffeine consumption': '카페인섭취량',
        'Alcohol consumption': '알코올섭취량',
        'Smoking status': '흡연여부',
        'Sleep efficiency': '수면효율',
        'Awakenings': '잠에서깬횟수'
    }
    df = df.rename(columns=column_mapping)
    return df

# 3. 메인 로직
st.title("🌙 현대인 수면 질 및 라이프스타일 요인 분석")
st.markdown("직업적 요인과 외부 요인(카페인, 음주)이 수면에 미치는 영향을 통합 분석합니다.")

# 파일 경로 설정
FILE1 = 'Sleep_health_and_lifestyle_dataset.csv'
FILE2 = 'Sleep_Efficiency.csv'

# 두 파일이 모두 있는지 확인
if os.path.exists(FILE1) and os.path.exists(FILE2):
    df_health = load_health_data(FILE1)
    df_eff = load_efficiency_data(FILE2)

    # 탭 구성
    tab1, tab2 = st.tabs(["🏥 직업군 및 건강 지표 분석", "☕ 카페인/알코올 영향 분석"])

    # --- 첫 번째 탭: 기존 분석 ---
    with tab1:
        st.sidebar.header("직업군 필터")
        selected_occ = st.sidebar.multiselect("분석할 직업군 선택", df_health['직업'].unique(), default=df_health['직업'].unique())
        filtered_health = df_health[df_health['직업'].isin(selected_occ)]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("대상 인원", f"{len(filtered_health)} 명")
        col2.metric("평균 수면 시간", f"{filtered_health['수면시간'].mean():.1f}h")
        col3.metric("평균 스트레스", f"{filtered_health['스트레스지수'].mean():.1f}/10")
        col4.metric("평균 걸음 수", f"{int(filtered_health['일일걸음수'].mean()):,}보")

        st.divider()
        
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.subheader("📊 직업군별 평균 수면 시간")
            occ_sleep = filtered_health.groupby('직업')['수면시간'].mean().sort_values().reset_index()
            fig1 = px.bar(occ_sleep, x='수면시간', y='직업', orientation='h', color='수면시간', color_continuous_scale='Purples')
            st.plotly_chart(fig1, use_container_width=True)
        
        with r1_c2:
            st.subheader("🏃 활동량과 스트레스 상관관계")
            fig2 = px.scatter(filtered_health, x='일일걸음수', y='스트레스지수', color='직업', trendline="ols")
            st.plotly_chart(fig2, use_container_width=True)

    # --- 두 번째 탭: 카페인/알코올 분석 ---
    with tab2:
        st.header("☕ 외부 요인이 수면 효율에 미치는 영향")
        st.info("수면 효율(Sleep Efficiency)은 실제 취침 시간 대비 실제 수면 시간의 비율을 의미합니다.")

        r2_c1, r2_c2 = st.columns(2)
        
        with r2_c1:
            st.subheader("☕ 카페인 섭취량별 수면 효율")
            # 카페인 섭취량은 0, 25, 50, 75, 100 등으로 나뉘어 있음
            fig3 = px.box(df_eff, x='카페인섭취량', y='수면효율', color='카페인섭취량',
                          title="카페인 섭취(mg)에 따른 수면 효율 분포")
            st.plotly_chart(fig3, use_container_width=True)

        with r2_c2:
            st.subheader("🍺 알코올 섭취량별 수면 효율")
            fig4 = px.box(df_eff, x='알코올섭취량', y='수면효율', color='알코올섭취량',
                          title="음주량에 따른 수면 효율 분포", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig4, use_container_width=True)

        st.divider()
        st.subheader("🚬 흡연 여부와 잠에서 깬 횟수")
        fig5 = px.violin(df_eff, x="흡연여부", y="잠에서깬횟수", color="흡연여부", box=True, points="all")
        st.plotly_chart(fig5, use_container_width=True)

    with st.expander("데이터 원본 보기"):
        st.write("건강 및 직업 데이터", df_health.head())
        st.write("수면 효율 및 라이프스타일 데이터", df_eff.head())

else:
    st.error("파일을 찾을 수 없습니다. 깃허브에 아래 두 파일이 있는지 확인해주세요.")
    st.write(f"- {FILE1}")
    st.write(f"- {FILE2}")
