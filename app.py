import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 설정 및 디자인 적용
# ==========================================
st.set_page_config(page_title="수면 건강 종합 진단 대시보드", page_icon="🌙", layout="wide")

def apply_custom_design():
    st.markdown("""
        <style>
        /* 메인 배경색 */
        .main { background-color: #f8f9fa; }
        
        /* Metric 카드 스타일링 */
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        }
        
        /* 탭 디자인 */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            font-size: 18px;
            font-weight: 600;
        }
        
        /* 버튼 스타일 */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            background-color: #4f46e5;
            color: white;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_design()

# ==========================================
# 2. 데이터 로드 및 전처리 함수
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
    df['Blood Pressure'] = df['Blood Pressure'].apply(categorize_bp)
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
        'Age': '나이', 'Blood Pressure': '혈압'
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
        'Smoking status': '흡연여부', 'Age': '나이', 'Caffeine consumption': '카페인'
    })

df1_raw = load_data_1()
df2_raw = load_data_2()

# ==========================================
# 3. 사이드바 필터
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3094/3094371.png", width=80)
    st.title("분석 설정")
    st.markdown("---")
    if not df1_raw.empty and not df2_raw.empty:
        age_range = st.slider("📅 연령대", 10, 80, (20, 50))
        selected_occ = st.multiselect("💼 직업군", sorted(df1_raw['직업'].unique().tolist()), default=df1_raw['직업'].unique().tolist())
        df1 = df1_raw[(df1_raw['나이'].between(*age_range)) & (df1_raw['직업'].isin(selected_occ))].copy()
        df2 = df2_raw[df2_raw['나이'].between(*age_range)].copy()
    st.markdown("---")
    st.caption("Data Source: Sleep Study Research 2026")

# ==========================================
# 4. 메인 화면
# ==========================================
st.title("🌙 수면 건강 데이터 진단 대시보드")

if df1.empty or df2.empty:
    st.error("데이터를 찾을 수 없습니다. 파일명을 확인해 주세요.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📉 라이프스타일 분석", "💤 수면 효율 분석", "📋 나의 수면 점수 진단"])

# --- 탭 1: 직업 및 건강 ---
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 인원", f"{len(df1)}명")
    c2.metric("평균 수면", f"{df1['수면시간'].mean():.1f}h")
    c3.metric("스트레스", f"{df1['스트레스지수'].mean():.1f}점")
    c4.metric("수면 질", f"{df1['수면의질'].mean():.1f}점")

    with st.container(border=True):
        col_sel1, col_sel2 = st.columns([1, 3])
        with col_sel1:
            target = st.radio("분석 기준", options=['직업', 'BMI분류', '혈압'])
        with col_sel2:
            avg_d = df1.groupby(target)[['수면시간', '수면의질']].mean().reset_index().sort_values('수면시간')
            fig_d = px.bar(avg_d, x='수면시간', y=target, orientation='h', color='수면의질', text_auto='.1f', color_continuous_scale='Viridis', template="plotly_white")
            st.plotly_chart(fig_d, use_container_width=True)

# --- 탭 2: 수면 효율 ---
with tab2:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 인원", f"{len(df2)}명")
    c2.metric("수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
    c3.metric("깊은 수면", f"{df2['깊은수면비율'].mean():.1f}%")
    c4.metric("평균 각성", f"{df2['각성횟수'].mean():.1f}회")

    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        with st.container(border=True):
            stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
            fig6 = px.pie(stages, values='비중', names='단계', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig6, use_container_width=True)
    with col_e2:
        with st.container(border=True):
            factor = st.selectbox("집중 분석 요인", ['알코올 섭취량 (수면 효율)', '운동 빈도 (깊은 수면 비중)', '카페인 섭취량 (각성 횟수)'])
            if '알코올' in factor:
                fig_f = px.line(df2.groupby('알코올')['수면효율'].mean().reset_index(), x='알코올', y='수면효율', markers=True, template="plotly_white")
            elif '운동' in factor:
                fig_f = px.line(df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index(), x='운동빈도', y='깊은수면비율', markers=True, template="plotly_white")
            else:
                fig_f = px.scatter(df2, x='카페인', y='각성횟수', trendline="ols", template="plotly_white")
            st.plotly_chart(fig_f, use_container_width=True)

# --- 탭 3: 자가진단 (새로 추가된 기능) ---
with tab3:
    st.header("🔍 나의 예상 수면 점수 확인")
    st.markdown("본인의 데이터를 입력하면 기존 분석 결과를 바탕으로 수면 건강 점수를 계산합니다.")
    
    with st.container(border=True):
        i1, i2 = st.columns(2)
        with i1:
            u_bmi = st.selectbox("나의 BMI 상태", ["정상", "과체중", "비만"])
            u_smoke = st.radio("흡연 여부", ["비흡연", "흡연"], horizontal=True)
            u_stress = st.slider("스트레스 지수 (1~10)", 1, 10, 5)
        with i2:
            u_alc = st.number_input("주간 음주 횟수", 0, 7, 0)
            u_ex = st.slider("주간 운동 횟수", 0, 7, 3)
            u_hr = st.number_input("평균 수면 시간", 4, 12, 7)

        if st.button("점수 산출하기 ✨"):
            score = 80 # 기본 점수
            if u_bmi == "과체중": score -= 5
            elif u_bmi == "비만": score -= 15
            if u_smoke == "흡연": score -= 10
            score -= (u_alc * 3)
            score -= (u_stress * 2)
            score += (u_ex * 4)
            if 7 <= u_hr <= 8: score += 10
            elif u_hr < 6: score -= 10
            
            score = max(0, min(100, score))
            st.markdown("---")
            st.subheader(f"당신의 예상 수면 점수: **{score}점**")
            if score >= 80: st.success("✅ 우수한 수면 습관입니다!")
            elif score >= 60: st.warning("⚠️ 보통입니다. 개선의 여지가 있습니다.")
            else: st.error("🚨 수면 건강 위험군입니다. 생활 습관 교정이 필요합니다.")
            st.info(f"💡 분석 결과, 주 {u_ex}회 운동을 {u_ex+1}회로 늘리면 숙면 확률이 더 높아질 수 있습니다.")

with st.expander("원본 데이터 확인"):
    st.dataframe(df1.head())
