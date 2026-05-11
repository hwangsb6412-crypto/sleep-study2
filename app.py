import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="수면 & 라이프스타일 대시보드",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 데이터 로드 및 전처리 (더미 데이터 생성 포함)
# ==========================================
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        # 사용자가 CSV 파일을 업로드한 경우
        df = pd.read_csv(uploaded_file)
        return df
    else:
        # 업로드된 파일이 없을 경우 시연용 가상 데이터 생성
        np.random.seed(42)
        n = 400
        occupations = ['엔지니어', '변호사', '의사/간호사', '교사', '영업직']
        
        df = pd.DataFrame({
            '직업': np.random.choice(occupations, n),
            '일일걸음수': np.random.randint(3000, 12000, n),
            'BMI분류': np.random.choice(['정상', '과체중', '비만'], n, p=[0.55, 0.3, 0.15]),
            '수면무호흡증_여부': np.random.choice(['없음', '있음'], n, p=[0.7, 0.3]),
            '심야_스마트폰_사용': np.random.choice(['예', '아니오'], n, p=[0.6, 0.4])
        })
        
        # 이전 슬라이드 인사이트에 맞게 데이터 조작
        # 1. 걸음수가 많을수록 스트레스 감소
        df['스트레스지수'] = 10 - (df['일일걸음수'] / 1500) + np.random.normal(0, 1, n)
        df.loc[df['직업'] == '영업직', '스트레스지수'] += 2.0 # 영업직 스트레스 가중
        df['스트레스지수'] = df['스트레스지수'].clip(1, 10).round(1)
        
        # 2. 직업별 기본 수면 시간 및 스마트폰 사용에 따른 수면의 질 하락
        base_sleep = {'엔지니어': 8.0, '변호사': 7.4, '의사/간호사': 6.8, '교사': 6.5, '영업직': 5.9}
        df['수면시간'] = df['직업'].map(base_sleep) + np.random.normal(0, 0.5, n)
        df['수면의질'] = (df['수면시간'] * 1.2) + np.random.normal(0, 0.5, n)
        
        df.loc[df['심야_스마트폰_사용'] == '예', '수면의질'] -= 1.5
        df['수면의질'] = df['수면의질'].clip(1, 10).round(1)
        
        return df

# ==========================================
# 3. 사이드바 (데이터 업로드 및 필터)
# ==========================================
st.sidebar.title("설정 및 필터")
st.sidebar.markdown("Kaggle의 `Sleep Health and Lifestyle Dataset` CSV를 업로드해보세요. (없으면 샘플 데이터로 동작합니다.)")
uploaded_file = st.sidebar.file_uploader("CSV 파일 업로드", type=['csv'])

df = load_data(uploaded_file)

st.sidebar.markdown("---")
st.sidebar.subheader("데이터 필터링")
selected_occ = st.sidebar.multiselect("직업군 선택", df['직업'].unique(), default=df['직업'].unique())

# 필터 적용
filtered_df = df[df['직업'].isin(selected_occ)]

# ==========================================
# 4. 메인 화면 구성
# ==========================================
st.title("🌙 현대인 생활 습관 및 수면 질 분석")
st.markdown("수면 시간, 신체 활동량(걸음 수), 스트레스가 건강에 미치는 영향을 탐색합니다.")

# 주요 지표 (KPI)
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 데이터 수", f"{len(filtered_df)} 명")
col2.metric("평균 수면 시간", f"{filtered_df['수면시간'].mean():.1f} 시간")
col3.metric("평균 스트레스 지수", f"{filtered_df['스트레스지수'].mean():.1f} / 10")
col4.metric("평균 일일 걸음 수", f"{int(filtered_df['일일걸음수'].mean()):,} 보")

st.markdown("---")

# 레이아웃 나누기
row1_col1, row1_col2 = st.columns(2)

# [차트 1] 직업군별 평균 수면 시간 및 수면의 질 (Bar Chart)
with row1_col1:
    st.subheader("📊 직업군별 평균 수면 시간")
    occ_sleep = filtered_df.groupby('직업')[['수면시간', '수면의질']].mean().reset_index()
    occ_sleep = occ_sleep.sort_values('수면시간', ascending=False)
    
    fig1 = px.bar(occ_sleep, x='수면시간', y='직업', orientation='h', 
                  color='수면시간', color_continuous_scale='Blues',
                  text_auto='.1f', title="직업에 따른 평균 수면 시간 비교")
    st.plotly_chart(fig1, use_container_width=True)

# [차트 2] 걸음 수와 스트레스 지수의 상관관계 (Scatter Plot)
with row1_col2:
    st.subheader("🏃 일일 걸음 수 vs 스트레스 지수")
    fig2 = px.scatter(filtered_df, x='일일걸음수', y='스트레스지수', color='직업',
                      trendline="ols", opacity=0.7,
                      title="걸음 수가 많을수록 스트레스가 감소하는가?")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

row2_col1, row2_col2 = st.columns(2)

# [차트 3] 밤 10시 이후 스마트폰 사용과 수면의 질
with row2_col1:
    st.subheader("📱 심야 스마트폰 사용과 수면 효율")
    smart_sleep = filtered_df.groupby('심야_스마트폰_사용')['수면의질'].mean().reset_index()
    
    fig3 = px.box(filtered_df, x='심야_스마트폰_사용', y='수면의질', color='심야_스마트폰_사용',
                  color_discrete_sequence=['#ef4444', '#38bdf8'],
                  title="심야 스마트폰 사용 여부에 따른 수면의 질 분포")
    st.plotly_chart(fig3, use_container_width=True)
    
    avg_yes = smart_sleep.loc[smart_sleep['심야_스마트폰_사용']=='예', '수면의질'].values[0]
    avg_no = smart_sleep.loc[smart_sleep['심야_스마트폰_사용']=='아니오', '수면의질'].values[0]
    st.info(f"💡 인사이트: 스마트폰을 사용하지 않는 그룹의 수면 질이 약 **{avg_no - avg_yes:.1f}** 포인트 더 높습니다.")

# [차트 4] BMI와 수면 무호흡증 비율
with row2_col2:
    st.subheader("⚖️ 비만도(BMI)에 따른 수면 무호흡증 비율")
    bmi_apnea = filtered_df.groupby(['BMI분류', '수면무호흡증_여부']).size().reset_index(name='count')
    
    fig4 = px.bar(bmi_apnea, x='BMI분류', y='count', color='수면무호흡증_여부', barmode='group',
                  color_discrete_sequence=['#334155', '#38bdf8'],
                  title="체중 카테고리별 수면 무호흡증 발생 빈도")
    st.plotly_chart(fig4, use_container_width=True)

# ==========================================
# 5. 원본 데이터 확인 탭
# ==========================================
with st.expander("원본 데이터 테이블 보기"):
    st.dataframe(filtered_df, use_container_width=True)