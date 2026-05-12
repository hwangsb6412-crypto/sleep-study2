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
    
    # 나이대(Age Group) 컬럼 생성 (10년 단위)
    df['나이대'] = (df['Age'] // 10 * 10).astype(str) + "대"
    
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
    
    # 두 번째 데이터셋에도 나이대 생성
    df['나이대'] = (df['Age'] // 10 * 10).astype(str) + "대"
    
    return df.rename(columns={
        'Sleep efficiency': '수면효율', 'REM sleep percentage': 'REM비율', 
        'Deep sleep percentage': '깊은수면비율', 'Light sleep percentage': '얕은수면비율', 
        'Awakenings': '각성횟수', 'Alcohol consumption': '알코올', 'Exercise frequency': '운동빈도',
        'Smoking status': '흡연여부', 'Age': '나이'
    })

try:
    df1_raw = load_data_1()
    df2_raw = load_data_2()
except Exception as e:
    st.error(f"데이터 로드 오류: {e}")
    df1_raw, df2_raw = pd.DataFrame(), pd.DataFrame()

# ==========================================
# 3. 사이드바 전체 필터 (나이별 동적 필터)
# ==========================================
st.sidebar.header("🔍 전체 데이터 필터")
st.sidebar.markdown("나이대를 선택하면 모든 그래프가 업데이트됩니다.")

# 나이대 리스트 추출 (두 데이터셋 합쳐서 유니크한 값 추출)
all_age_groups = sorted(list(set(df1_raw['나이대'].unique()) | set(df2_raw['나이대'].unique())))
selected_ages = st.sidebar.multiselect("확인할 나이대 선택:", options=all_age_groups, default=all_age_groups)

# 필터링된 데이터 생성
df1 = df1_raw[df1_raw['나이대'].isin(selected_ages)]
df2 = df2_raw[df2_raw['나이대'].isin(selected_ages)]

# ==========================================
# 4. 메인 UI 구성
# ==========================================
st.title("📊 수면 건강 통합 대시보드")
st.write(f"현재 데이터 범위: **{', '.join(selected_ages)}**")

if df1.empty and df2.empty:
    st.warning("선택한 조건에 맞는 데이터가 없습니다. 필터를 조정해 주세요.")
    st.stop()

tab1, tab2 = st.tabs(["📉 라이프스타일 분석", "💤 수면 효율 분석"])

with tab1:
    if not df1.empty:
        # 상단 Metric
        c1, c2, c3 = st.columns(3)
        c1.metric("선택 범위 평균 수면시간", f"{df1['수면시간'].mean():.1f}시간")
        c2.metric("선택 범위 평균 스트레스", f"{df1['스트레스지수'].mean():.1f}점")
        c3.metric("선택 범위 평균 수면의질", f"{df1['수면의질'].mean():.1f}점")
        
        st.markdown("---")
        
        # 동적 기준 분석
        st.subheader("🎯 조건별 수면시간 분석")
        target_cat = st.selectbox("분석 기준 선택:", options=['직업', 'BMI분류', '스트레스지수'], key='s1')
        avg_dyn = df1.groupby(target_cat)['수면시간'].mean().reset_index().sort_values('수면시간')
        st.plotly_chart(px.bar(avg_dyn, x='수면시간', y=target_cat, orientation='h', color='수면시간', text_auto='.1f', color_continuous_scale='Viridis'), use_container_width=True)

        # 기존 그래프들
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("👨‍💻 직업별 수면시간")
            st.plotly_chart(px.bar(df1.groupby('직업')['수면시간'].mean().reset_index().sort_values('수면시간'), x='수면시간', y='직업', orientation='h', color_continuous_scale='Blues'), use_container_width=True)
        with col_r:
            st.subheader("🔥 직업별 스트레스")
            st.plotly_chart(px.bar(df1.groupby('직업')['스트레스지수'].mean().reset_index().sort_values('스트레스지수'), x='스트레스지수', y='직업', orientation='h', color_continuous_scale='Reds'), use_container_width=True)

with tab2:
    if not df2.empty:
        e1, e2, e3 = st.columns(3)
        e1.metric("평균 수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
        e2.metric("깊은 수면 비중", f"{df2['깊은수면비율'].mean():.1f}%")
        e3.metric("평균 각성 횟수", f"{df2['각성횟수'].mean():.1f}회")

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.subheader("🍺 알코올 섭취량별 수면 효율")
            avg_eff = df2.groupby('알코올')['수면효율'].mean().reset_index()
            avg_eff['수면효율'] = (avg_eff['수면효율'] * 100).round(1)
            st.plotly_chart(px.line(avg_eff, x='알코올', y='수면효율', markers=True, text='수면효율'), use_container_width=True)
        with col_e2:
            st.subheader("🛌 평균 수면 단계 구성")
            stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
            st.plotly_chart(px.pie(stages, values='비중', names='단계', hole=0.4), use_container_width=True)
