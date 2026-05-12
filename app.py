import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정 및 디자인
# ==========================================
st.set_page_config(
    page_title="수면 및 심혈관 건강 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

# 메트릭 카드 및 버튼 디자인을 위한 CSS
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4f46e5;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
def categorize_bp(bp_str):
    try:
        sys, dia = map(int, str(bp_str).split('/'))
        if sys < 120 and dia < 80: return '정상혈압'
        elif 120 <= sys < 130 and dia < 80: return '주의혈압'
        elif 130 <= sys < 140 or 80 <= dia < 90: return '고혈압 전단계'
        else: return '고혈압'
    except: return '기타'

@st.cache_data
def load_data_1():
    file_path = 'Sleep_health_and_lifestyle_dataset.csv'
    if not os.path.exists(file_path): return pd.DataFrame()
    df = pd.read_csv(file_path)
    # 혈압 카테고리화 (탭 1 분석용)
    df['혈압상태'] = df['Blood Pressure'].apply(categorize_bp)
    df['BMI Category'] = df['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
    df['Sleep Disorder'] = df['Sleep Disorder'].fillna('없음').replace({'None': '없음', 'Sleep Apnea': '수면 무호흡증', 'Insomnia': '불면증'})
    occ_map = {
        'Software Engineer': '엔지니어', 'Doctor': '의사', 'Sales Representative': '영업직', 
        'Teacher': '교사', 'Nurse': '간호사', 'Engineer': '엔지니어', 'Accountant': '회계사', 
        'Scientist': '과학자', 'Lawyer': '변호사', 'Salesperson': '영업직', 'Manager': '관리자'
    }
    df['Occupation'] = df['Occupation'].map(occ_map).fillna(df['Occupation'])
    return df.rename(columns={
        'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질', 
        'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애', 
        'Age': '나이', 'Blood Pressure': '혈압원문'
    })

@st.cache_data
def load_data_2():
    file_path = 'Sleep_Efficiency.csv'
    if not os.path.exists(file_path): return pd.DataFrame()
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

# ==========================================
# 3. 사이드바 동적 필터
# ==========================================
st.sidebar.title("🎮 동적 필터 조절")
if not df1_raw.empty and not df2_raw.empty:
    min_age = int(min(df1_raw['나이'].min(), df2_raw['나이'].min()))
    max_age = int(max(df1_raw['나이'].max(), df2_raw['나이'].max()))
    age_range = st.sidebar.slider("분석 연령대 설정", min_age, max_age, (min_age, max_age))
    all_occupations = sorted(df1_raw['직업'].unique().tolist())
    selected_occ = st.sidebar.multiselect("분석 직업군 선택", all_occupations, default=all_occupations)

    df1 = df1_raw[(df1_raw['나이'].between(*age_range)) & (df1_raw['직업'].isin(selected_occ))].copy()
    df2 = df2_raw[df2_raw['나이'].between(*age_range)].copy()

# ==========================================
# 4. 메인 UI 구성
# ==========================================
st.title("📊 수면 및 건강 통합 데이터 대시보드")

tab1, tab2, tab3 = st.tabs(["📉 라이프스타일 & 혈압 분석", "💤 수면 효율 & 외부 요인", "📋 나의 수면 건강 진단"])

# ------------------------------------------
# 탭 1: 생활 습관 및 혈압 상관관계
# ------------------------------------------
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("선택된 모집단", f"{len(df1)}명")
    c2.metric("평균 수면 시간", f"{df1['수면시간'].mean():.1f}h")
    c3.metric("평균 스트레스", f"{df1['스트레스지수'].mean():.1f}점")
    c4.metric("평균 수면의 질", f"{df1['수면의질'].mean():.1f}점")

    st.markdown("---")
    st.subheader("🩸 수면의 질과 혈압의 상관관계")
    # 수면의 질 점수별 고혈압 비율 분석
    bp_analysis = df1.groupby('수면의질')['혈압상태'].value_counts(normalize=True).unstack().fillna(0) * 100
    if '고혈압' in bp_analysis.columns:
        fig_bp = px.line(bp_analysis.reset_index(), x='수면의질', y='고혈압', markers=True,
                         title="수면의 질이 낮을수록 나타나는 고혈압 비율(%)", color_discrete_sequence=['#ef4444'])
        st.plotly_chart(fig_bp, use_container_width=True)

    col_sel1, col_sel2 = st.columns([1, 3])
    with col_sel1:
        target_category = st.radio("분석 기준 선택", options=['직업', 'BMI분류', '스트레스지수'])
    with col_sel2:
        avg_dynamic = df1.groupby(target_category)[['수면시간', '수면의질']].mean().reset_index().sort_values('수면시간')
        fig_dyn = px.bar(avg_dynamic, x='수면시간', y=target_category, orientation='h', color='수면의질', text_auto='.1f', color_continuous_scale='Turbo')
        st.plotly_chart(fig_dyn, use_container_width=True)

# ------------------------------------------
# 탭 2: 수면 효율 분석 (기존 모든 기능)
# ------------------------------------------
with tab2:
    st.subheader("🛌 수면 단계 구성 및 외부 요인 분석")
    col_eff1, col_eff2 = st.columns([1, 2])
    with col_eff1:
        stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
        fig6 = px.pie(stages, values='비중', names='단계', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig6, use_container_width=True)
    with col_eff2:
        factor_choice = st.selectbox("영향 요인 선택", ['알코올 섭취량 (수면 효율)', '운동 빈도 (깊은 수면 비중)', '흡연 여부 (각성 횟수)'])
        if '알코올' in factor_choice:
            fig_f = px.line(df2.groupby('알코올')['수면효율'].mean().reset_index(), x='알코올', y='수면효율', markers=True)
        elif '운동' in factor_choice:
            fig_f = px.line(df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index(), x='운동빈도', y='깊은수면비율', markers=True)
        else:
            fig_f = px.bar(df2.groupby('흡연여부')['각성횟수'].mean().reset_index(), x='흡연여부', y='각성횟수', color='흡연여부', text_auto='.1f')
        st.plotly_chart(fig_f, use_container_width=True)

# ------------------------------------------
# 탭 3: 나의 수면 점수 및 혈압 위험 진단
# ------------------------------------------
with tab3:
    st.header("📋 나의 수면 건강 및 혈압 위험도 진단")
    st.markdown("키, 몸무게 및 생활 습관을 입력하여 데이터 기반의 종합 점수를 확인하세요.")
    
    with st.container(border=True):
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            u_height = st.number_input("키 (cm)", 100.0, 220.0, 175.0)
            u_weight = st.number_input("몸무게 (kg)", 30.0, 150.0, 70.0)
            user_smoke = st.radio("흡연 여부", ["비흡연", "흡연"], horizontal=True)
        with col_in2:
            user_alc = st.number_input("일주일 음주 횟수", 0, 7, 0)
            user_ex = st.slider("일주일 운동 횟수", 0, 7, 3)
            user_sleep = st.number_input("평균 수면 시간 (h)", 0.0, 12.0, 7.0)

        # BMI 자동 계산
        bmi_val = u_weight / ((u_height / 100) ** 2)
        bmi_status = "정상" if bmi_val < 25 else "과체중" if bmi_val < 30 else "비만"
        
        st.info(f"💡 당신의 BMI는 **{bmi_val:.1f}**로 **'{bmi_status}'** 상태입니다.")

        if st.button("내 건강 점수 확인하기 ✨"):
            score = 90
            # 감점 로직
            if bmi_status == "비만": score -= 15
            if user_smoke == "흡연": score -= 12
            if user_sleep < 6: score -= 15 # 수면 부족 시 큰 감점
            score -= (user_alc * 4)
            score += (user_ex * 5)
            
            final_score = max(0, min(100, score))
            st.markdown("---")
            st.subheader(f"📊 예상 종합 건강 점수: **{final_score}점**")
            
            # 고혈압 가능성 경고 로직 (탭 1의 상관관계 반영)
            if final_score < 70 or user_sleep < 5.5 or bmi_status == "비만":
                st.error("🚨 **고혈압 위험 주의!**")
                st.markdown("""
                데이터 분석 결과, 현재 입력하신 수면 시간과 신체 조건은 **고혈압 발생 확률이 높은 그룹**과 유사한 패턴을 보입니다. 
                숙면을 방해하는 요인을 줄이고 규칙적인 수면 시간을 확보하시길 권장합니다.
                """)
            elif final_score >= 85:
                st.success("✅ **매우 양호합니다!** 심혈관 및 수면 건강 관리가 아주 잘 이루어지고 있습니다.")
            else:
                st.warning("⚖️ **관리 권고:** 수면 시간이나 운동량을 개선하여 혈압 건강을 지키는 것을 추천드립니다.")

with st.expander("데이터 원본 상세보기"):
    st.dataframe(df1.head())
