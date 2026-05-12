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
# 2. 데이터 로드 및 전처리 함수
# ==========================================
@st.cache_data
def load_data_1():
    file_path = 'Sleep_health_and_lifestyle_dataset.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    
    # 카테고리 한글 변환
    df['BMI Category'] = df['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
    
    # 결측치 처리 및 변환
    df['Sleep Disorder'] = df['Sleep Disorder'].fillna('없음')
    df['Sleep Disorder'] = df['Sleep Disorder'].replace({'None': '없음', 'Sleep Apnea': '수면 무호흡증', 'Insomnia': '불면증'})
    
    occ_map = {
        'Software Engineer': '엔지니어', 'Doctor': '의사', 'Sales Representative': '영업직', 
        'Teacher': '교사', 'Nurse': '간호사', 'Engineer': '엔지니어', 'Accountant': '회계사', 
        'Scientist': '과학자', 'Lawyer': '변호사', 'Salesperson': '영업직', 'Manager': '관리자'
    }
    df['Occupation'] = df['Occupation'].map(occ_map).fillna(df['Occupation'])
    
    return df.rename(columns={
        'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질', 
        'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애'
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
        'Smoking status': '흡연여부' 
    })

# 데이터 로드 실행 (안전하게 try-except 감싸기)
try:
    df1 = load_data_1()
    df2 = load_data_2()
except Exception as e:
    st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

# ==========================================
# 3. 메인 UI 구성
# ==========================================
st.title("📊 수면 건강 핵심 데이터 대시보드")
st.markdown("항목을 직접 선택하여 **직업별 수면 지표**를 실시간으로 비교해 보세요.")

# 데이터가 아예 없는 경우 방어 코드
if df1.empty and df2.empty:
    st.error("⚠️ 데이터를 불러오지 못했습니다. CSV 파일이 `app.py`와 같은 폴더에 있는지 확인해 주세요.")
    st.stop()

tab1, tab2 = st.tabs(["📉 라이프스타일 분석 (생활 습관)", "💤 수면 효율 분석 (외부 요인)"])

# ------------------------------------------
# 탭 1: 생활 습관 (직업별 선택 기능 포함)
# ------------------------------------------
with tab1:
    if df1.empty:
        st.warning("`Sleep_health_and_lifestyle_dataset.csv` 파일이 없습니다.")
    else:
        # 상단 지표
        c1, c2, c3 = st.columns(3)
        c1.metric("평균 수면 시간", f"{df1['수면시간'].mean():.1f}시간")
        c2.metric("평균 스트레스 지수", f"{df1['스트레스지수'].mean():.1f}점")
        c3.metric("평균 수면의 질", f"{df1['수면의질'].mean():.1f}점")
        
        st.markdown("---")
        
        # 사용자가 비교 항목 선택
        st.subheader("📋 직업별 상세 지표 비교")
        selected_col = st.selectbox(
            "비교하고 싶은 항목을 선택하세요:",
            options
