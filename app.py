import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 설정 및 디자인
# ==========================================
st.set_page_config(page_title="수면 & 혈압 건강 대시보드", page_icon="📊", layout="wide")

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
    df['Blood Pressure Category'] = df['Blood Pressure'].apply(categorize_bp)
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
        'Age': '나이', 'Blood Pressure Category': '혈압상태'
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
# 3. 사이드바 필터
# ==========================================
st.sidebar.title("🎮 분석 필터")
if not df1_raw.empty:
    age_range = st.sidebar.slider("연령대 설정", int(df1_raw['나이'].min()), int(df1_raw['나이'].max()), (20, 50))
    selected_occ = st.sidebar.multiselect("직업군 선택", sorted(df1_raw['직업'].unique().tolist()), default=df1_raw['직업'].unique().tolist())
    df1 = df1_raw[(df1_raw['나이'].between(*age_range)) & (df1_raw['직업'].isin(selected_occ))].copy()
    df2 = df2_raw[df2_raw['나이'].between(*age_range)].copy()

# ==========================================
# 4. 메인 UI
# ==========================================
st.title("📊 수면-심혈관 건강 통합 분석 대시보드")

tab1, tab2, tab3 = st.tabs(["📉 생활 습관 & 혈압 분석", "💤 수면 단계 & 외부 요인", "📋 자가진단 서비스"])

# --- 탭 1: 혈압 상관관계 집중 분석 ---
with tab1:
    st.subheader("🩸 수면의 질과 혈압의 위험한 상관관계")
    
    # 분석용 데이터 가공: 수면의 질 점수별 고혈압 비율 계산
    bp_analysis = df1.groupby('수면의질')['혈압상태'].value_counts(normalize=True).unstack().fillna(0) * 100
    if '고혈압' in bp_analysis.columns:
        hp_rate = bp_analysis[['고혈압']].reset_index()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            fig_hp = px.line(hp_rate, x='수면의질', y='고혈압', markers=True, 
                             title="수면의 질 점수가 낮을수록 급증하는 고혈압 비율(%)",
                             color_discrete_sequence=['#ef4444'])
            fig_hp.update_layout(xaxis_title="수면의 질 점수 (1-10)", yaxis_title="고혈압군 비율 (%)")
            st.plotly_chart(fig_hp, use_container_width=True)
        
        with c2:
            st.markdown("#### 💡 데이터 인사이트")
            st.error(f"수면의 질이 **{hp_rate['수면의질'].min()}점**인 그룹은 고혈압 비율이 매우 높게 나타납니다.")
            st.info("수면 부족은 교감신경을 활성화시켜 혈압을 상승시키는 주요 원인임이 데이터로 증명됩니다.")
    
    st.divider()
    
    # 기존 직업/BMI 분석
    st.subheader("🎯 카테고리별 수면 지표")
    col_sel1, col_sel2 = st.columns([1, 3])
    with col_sel1:
        target = st.radio("분석 기준", options=['직업', 'BMI분류', '스트레스지수'])
    with col_sel2:
        avg_d = df1.groupby(target)[['수면시간', '수면의질']].mean().reset_index().sort_values('수면시간')
        fig_d = px.bar(avg_d, x='수면시간', y=target, orientation='h', color='수면의질', text_auto='.1f', color_continuous_scale='Viridis')
        st.plotly_chart(fig_d, use_container_width=True)

# --- 탭 2: 기존 수면 효율 분석 ---
with tab2:
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        st.subheader("🛌 수면 단계 비중")
        stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
        fig6 = px.pie(stages, values='비중', names='단계', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig6, use_container_width=True)
    with col_e2:
        st.subheader("⚡ 외부 요인 영향")
        factor = st.selectbox("분석 요인", ['알코올 섭취량 (수면 효율)', '운동 빈도 (깊은 수면 비중)', '흡연 여부 (각성 횟수)'])
        if '알코올' in factor:
            fig_f = px.line(df2.groupby('알코올')['수면효율'].mean().reset_index(), x='알코올', y='수면효율', markers=True)
        elif '운동' in factor:
            fig_f = px.line(df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index(), x='운동빈도', y='깊은수면비율', markers=True)
        else:
            fig_f = px.bar(df2.groupby('흡연여부')['각성횟수'].mean().reset_index(), x='흡연여부', y='각성횟수', color='흡연여부')
        st.plotly_chart(fig_f, use_container_width=True)

# --- 탭 3: 자가진단 (키/몸무게 포함) ---
with tab3:
    st.header("📋 수면 & 혈압 건강 자가진단")
    with st.container(border=True):
        i1, i2 = st.columns(2)
        with i1:
            u_h = st.number_input("키 (cm)", 100, 220, 175)
            u_w = st.number_input("몸무게 (kg)", 30, 150, 70)
            u_smoke = st.radio("흡연 여부", ["비흡연", "흡연"], horizontal=True)
        with i2:
            u_alc = st.number_input("주간 음주 횟수", 0, 7, 0)
            u_ex = st.slider("주간 운동 횟수", 0, 7, 3)
            u_hr = st.number_input("평균 수면 시간", 4.0, 12.0, 7.0)

        bmi = u_w / ((u_h/100)**2)
        status = "정상" if bmi < 25 else "과체중" if bmi < 30 else "비만"
        st.info(f"계산된 BMI: **{bmi:.1f} ({status})**")

        if st.button("내 건강 점수 확인 ✨"):
            score = 90
            if status == "비만": score -= 20
            if u_smoke == "흡연": score -= 15
            score -= (u_alc * 5)
            score += (u_ex * 5)
            if u_hr < 6: score -= 10
            
            final = max(0, min(100, score))
            st.subheader(f"종합 건강 점수: {final}점")
            if final < 60: st.error("🚨 수면 부족과 고혈압 위험이 높습니다. 관리가 필요합니다!")
            else: st.success("✅ 양호한 생활 습관을 유지하고 계십니다.")
