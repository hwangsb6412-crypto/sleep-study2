import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정
st.set_page_config(page_title="수면 & 라이프스타일 분석", page_icon="🌙", layout="wide")

# 2. 데이터 로드 함수 (한글 컬럼 변환 포함)
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    # 실제 데이터셋의 영문 컬럼을 한글로 매핑
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
    # 수면장애 결측치는 '정상'으로 채우기
    df['수면장애'] = df['수면장애'].fillna('None')
    return df

# 3. 메인 로직
st.title("🌙 현대인 생활 습관 및 수면 질 분석 대시보드")

# 깃허브에 함께 올린 파일 이름 (대소문자 주의!)
DATA_FILE = 'Sleep_health_and_lifestyle_dataset.csv'

# 파일이 존재하는지 확인 후 로드
if os.path.exists(DATA_FILE):
    df = load_data(DATA_FILE)
    
    # 사이드바 필터링
    st.sidebar.header("데이터 필터")
    selected_occ = st.sidebar.multiselect("분석할 직업군 선택", df['직업'].unique(), default=df['직업'].unique())
    filtered_df = df[df['직업'].isin(selected_occ)]

    # 상단 지표 (KPI)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 데이터 수", f"{len(filtered_df)} 명")
    col2.metric("평균 수면 시간", f"{filtered_df['수면시간'].mean():.1f}h")
    col3.metric("평균 수면의 질", f"{filtered_df['수면의질'].mean():.1f} / 10")
    col4.metric("평균 스트레스 지수", f"{filtered_df['스트레스지수'].mean():.1f} / 10")

    st.divider()

    # 그래프 레이아웃 (이후 코드는 동일)
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("📊 직업군별 평균 수면 시간")
        occ_sleep = filtered_df.groupby('직업')['수면시간'].mean().sort_values().reset_index()
        fig1 = px.bar(occ_sleep, x='수면시간', y='직업', orientation='h', color='수면시간',
                      color_continuous_scale='Purples', text_auto='.1f')
        st.plotly_chart(fig1, use_container_width=True)

    with row1_col2:
        st.subheader("🏃 일일 걸음 수 vs 스트레스 지수")
        fig2 = px.scatter(filtered_df, x='일일걸음수', y='스트레스지수', color='직업', 
                          trendline="ols", title="활동량과 스트레스의 관계")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("⚖️ BMI 분류에 따른 수면 장애")
        fig3 = px.histogram(filtered_df, x="BMI분류", color="수면장애", barmode="group",
                            title="비만도와 수면 장애 현황")
        st.plotly_chart(fig3, use_container_width=True)

    with row2_col2:
        st.subheader("🔍 수면 시간과 수면의 질 상관관계")
        fig4 = px.density_heatmap(filtered_df, x="수면시간", y="수면의질", text_auto=True,
                                  color_continuous_scale="Viridis")
        st.plotly_chart(fig4, use_container_width=True)

    with st.expander("원본 데이터 확인"):
        st.dataframe(filtered_df)
else:
    st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_FILE}")
    st.info("CSV 파일이 깃허브 저장소에 app.py와 같은 위치에 있는지 확인해주세요.")
