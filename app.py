import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="한눈에 보는 수면 건강 리포트",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
@st.cache_data
def load_data_1():
    file_path = 'Sleep_health_and_lifestyle_dataset.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    df['BMI Category'] = df['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
    df['Sleep Disorder'] = df['Sleep Disorder'].fillna('없음').replace({'None': '없음', 'Sleep Apnea': '수면 무호흡증', 'Insomnia': '불면증'})
    
    # [추가] 혈압 데이터 처리: "120/80" -> 수축기 혈압 기준 분류
    def categorize_bp(bp):
        try:
            systolic = int(bp.split('/')[0])
            if systolic < 120: return '정상 혈압'
            elif 120 <= systolic < 130: return '주의 혈압'
            elif 130 <= systolic < 140: return '고혈압 전단계'
            else: return '고혈압'
        except:
            return '데이터 없음'
    
    df['혈압기준'] = df['Blood Pressure'].apply(categorize_bp)
    
    occ_map = {
        'Software Engineer': '엔지니어', 'Doctor': '의사', 'Sales Representative': '영업직', 
        'Teacher': '교사', 'Nurse': '간호사', 'Engineer': '엔지니어', 'Accountant': '회계사', 
        'Scientist': '과학자', 'Lawyer': '변호사', 'Salesperson': '영업직', 'Manager': '관리자'
    }
    df['Occupation'] = df['Occupation'].map(occ_map).fillna(df['Occupation'])
    
    return df.rename(columns={
        'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질', 
        'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애', 'Age': '나이'
    })

@st.cache_data
def load_data_2():
    file_path = 'Sleep_Efficiency.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    df = df.fillna(0)
    df['Smoking status'] = df['Smoking status'].replace({'Yes': '흡연', 'No': '비흡연'})
    
    return df.rename(columns={
        'Sleep efficiency': '수면효율', 'REM sleep percentage': 'REM비율', 
        'Deep sleep percentage': '깊은수면비율', 'Light sleep percentage': '얕은수면비율', 
        'Awakenings': '각성횟수', 'Alcohol consumption': '알코올', 'Exercise frequency': '운동빈도',
        'Smoking status': '흡연여부', 'Age': '나이'
    })

df1_raw = load_data_1()
df2_raw = load_data_2()

if df1_raw.empty and df2_raw.empty:
    st.error("⚠️ 데이터를 불러오지 못했습니다.")
    st.stop()

# ==========================================
# 3. 사이드바 동적 필터
# ==========================================
st.sidebar.title("🎮 동적 필터 조절")

min_age = int(min(df1_raw['나이'].min(), df2_raw['나이'].min()))
max_age = int(max(df1_raw['나이'].max(), df2_raw['나이'].max()))
age_range = st.sidebar.slider("분석 연령대 설정", min_age, max_age, (min_age, max_age))

all_occupations = sorted(df1_raw['직업'].unique().tolist())
selected_occ = st.sidebar.multiselect("분석 직업군 선택", all_occupations, default=all_occupations)

# 필터링 적용
df1 = df1_raw[(df1_raw['나이'] >= age_range[0]) & (df1_raw['나이'] <= age_range[1]) & (df1_raw['직업'].isin(selected_occ))].copy()
df2 = df2_raw[(df2_raw['나이'] >= age_range[0]) & (df2_raw['나이'] <= age_range[1])].copy()

# ==========================================
# 4. 메인 UI 구성
# ==========================================
st.title("📊 수면 건강 핵심 데이터 대시보드")

if df1.empty and df2.empty:
    st.warning("선택한 조건에 맞는 데이터가 없습니다.")
    st.stop()

tab1, tab2 = st.tabs(["📉 라이프스타일 분석", "💤 수면 효율 분석"])

with tab1:
    if not df1.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("👥 분석 대상", f"{len(df1)}명")
        m2.metric("😴 평균 수면시간", f"{df1['수면시간'].mean():.1f}시간")
        m3.metric("🔥 평균 스트레스", f"{df1['스트레스지수'].mean():.1f}점")
        m4.metric("🌟 평균 수면의 질", f"{df1['수면의질'].mean():.1f}점")
        
        st.markdown("---")
        
        # [수정 포인트] 혈압기준 옵션 추가
        st.subheader("🎯 기준별 수면시간 분석")
        target_category = st.selectbox(
            "분석 기준 선택:", 
            options=['직업', 'BMI분류', '스트레스지수', '혈압기준'], # 여기에 혈압기준 추가
            index=0
        )
        avg_dynamic = df1.groupby(target_category)['수면시간'].mean().reset_index().sort_values('수면시간')
        st.plotly_chart(px.bar(avg_dynamic, x='수면시간', y=target_category, orientation='h', color='수면시간', text_auto='.1f', color_continuous_scale='Viridis'), use_container_width=True)
        
        st.markdown("---")
        
        # 나머지 기존 그래프 유지
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("👨‍💻 직업별 평균 수면 시간")
            st.plotly_chart(px.bar(df1.groupby('직업')['수면시간'].mean().reset_index().sort_values('수면시간'), x='수면시간', y='직업', orientation='h', color='수면시간', text_auto='.1f', color_continuous_scale='Blues'), use_container_width=True)
        with c_right:
            st.subheader("🔥 직업별 평균 스트레스")
            st.plotly_chart(px.bar(df1.groupby('직업')['스트레스지수'].mean().reset_index().sort_values('스트레스지수'), x='스트레스지수', y='직업', orientation='h', color='스트레스지수', text_auto='.1f', color_continuous_scale='Reds'), use_container_width=True)

        st.markdown("---")
        
        cl1, cl2 = st.columns(2)
        with cl1:
            st.subheader("⚖️ 체중분류별 수면 장애 현황")
            st.plotly_chart(px.bar(df1.groupby(['BMI분류', '수면장애']).size().reset_index(name='인원수'), x='BMI분류', y='인원수', color='수면장애', barmode='group', text_auto=True), use_container_width=True)
        with cl2:
            st.subheader("🌙 수면 장애별 수면의 질 점수")
            st.plotly_chart(px.bar(df1.groupby('수면장애')['수면의질'].mean().reset_index(), x='수면장애', y='수면의질', color='수면장애', text_auto='.1f'), use_container_width=True)

# 탭 2 생략 (변경 사항 없음)
