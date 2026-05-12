import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 설정 및 디자인 적용
# ==========================================
st.set_page_config(page_title="수면 건강 인사이트 대시보드", page_icon="🌙", layout="wide")

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
        'Smoking status': '흡연여부', 'Age': '나이'
    })

# 데이터 불러오기 실행
df1_raw = load_data_1()
df2_raw = load_data_2()

# ==========================================
# 3. 사이드바 구성
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3094/3094371.png", width=80)
    st.title("수면 분석 설정")
    st.markdown("---")
    if not df1_raw.empty and not df2_raw.empty:
        age_range = st.slider("📅 연령대 설정", 
                              int(min(df1_raw['나이'].min(), df2_raw['나이'].min())), 
                              int(max(df1_raw['나이'].max(), df2_raw['나이'].max())), (20, 50))
        selected_occ = st.multiselect("💼 직업군 필터", sorted(df1_raw['직업'].unique().tolist()), default=df1_raw['직업'].unique().tolist())
        df1 = df1_raw[(df1_raw['나이'].between(*age_range)) & (df1_raw['직업'].isin(selected_occ))].copy()
        df2 = df2_raw[df2_raw['나이'].between(*age_range)].copy()
    st.markdown("---")
    st.caption("Data Source: Sleep Study Research 2026")

# ==========================================
# 4. 메인 화면 UI
# ==========================================
st.title("🌙 수면 건강 핵심 데이터 대시보드")
st.markdown("데이터를 통해 현대인의 수면 패턴과 건강 지표를 심층 분석합니다.")

if df1.empty or df2.empty:
    st.error("데이터를 불러오지 못했거나 필터 결과가 없습니다.")
    st.stop()

tab1, tab2 = st.tabs(["📉 라이프스타일 분석", "💤 수면 효율 분석"])

with tab1:
    # KPI 지표
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 인원", f"{len(df1)}명")
    c2.metric("평균 수면", f"{df1['수면시간'].mean():.1f}시간")
    c3.metric("스트레스", f"{df1['스트레스지수'].mean():.1f}점")
    c4.metric("수면의 질", f"{df1['수면의질'].mean():.1f}점")

    st.markdown("### 🎯 카테고리별 상세 비교")
    with st.container(border=True):
        col_sel1, col_sel2 = st.columns([1, 3])
        with col_sel1:
            target_category = st.radio("분석 기준 선택", options=['직업', 'BMI분류', '스트레스지수', '혈압'])
        with col_sel2:
            avg_dyn = df1.groupby(target_category)[['수면시간', '수면의질']].mean().reset_index().sort_values('수면시간')
            fig_dyn = px.bar(avg_dyn, x='수면시간', y=target_category, orientation='h',
                             color='수면의질', text_auto='.1f', color_continuous_scale='Viridis', template="plotly_white")
            st.plotly_chart(fig_dyn, use_container_width=True)

    st.markdown("### ⚖️ BMI 및 수면 장애 현황")
    with st.container(border=True):
        bmi_data = df1.groupby(['BMI분류', '수면장애']).size().reset_index(name='인원수')
        fig3 = px.bar(bmi_data, x='BMI분류', y='인원수', color='수면장애', barmode='group',
                      color_discrete_map={'없음': '#4ade80', '불면증': '#facc15', '수면 무호흡증': '#fb7185'}, template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)

with tab2:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 인원", f"{len(df2)}명")
    c2.metric("수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
    c3.metric("깊은 수면", f"{df2['깊은수면비율'].mean():.1f}%")
    c4.metric("평균 각성", f"{df2['각성횟수'].mean():.1f}회")

    st.markdown("### 🛌 수면 단계 및 라이프스타일 요인")
    col_eff1, col_eff2 = st.columns([1, 2])
    with col_eff1:
        with st.container(border=True):
            stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
            fig6 = px.pie(stages, values='비중', names='단계', hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
            fig6.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2))
            st.plotly_chart(fig6, use_container_width=True)
            
    with col_eff2:
        with st.container(border=True):
            factor_choice = st.selectbox("집중 분석 요인 선택", ['알코올 섭취량 (수면 효율)', '운동 빈도 (깊은 수면 비중)', '흡연 여부 (각성 횟수)'])
            if '알코올' in factor_choice:
                avg_f = df2.groupby('알코올')['수면효율'].mean().reset_index()
                fig_f = px.line(avg_f, x='알코올', y='수면효율', markers=True, template="plotly_white")
                fig_f.update_traces(line_color='#ec4899')
            elif '운동' in factor_choice:
                avg_f = df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index()
                fig_f = px.line(avg_f, x='운동빈도', y='깊은수면비율', markers=True, template="plotly_white")
                fig_f.update_traces(line_color='#10b981')
            else:
                avg_f = df2.groupby('흡연여부')['각성횟수'].mean().reset_index()
                fig_f = px.bar(avg_f, x='흡연여부', y='각성횟수', color='흡연여부', template="plotly_white")
            st.plotly_chart(fig_f, use_container_width=True)

with st.expander("데이터 원본 상세보기"):
    st.dataframe(df1.head())
