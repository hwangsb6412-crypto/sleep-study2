import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="수면 건강 데이터 분석",
    page_icon="🌙",
    layout="wide"
)

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
@st.cache_data
def load_data():
    file_path = 'Sleep_health_and_lifestyle_dataset.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    
    # 한글 변환
    df['BMI Category'] = df['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
    
    occ_map = {
        'Software Engineer': '엔지니어', 'Doctor': '의사', 'Sales Representative': '영업직', 
        'Teacher': '교사', 'Nurse': '간호사', 'Engineer': '엔지니어', 'Accountant': '회계사', 
        'Scientist': '과학자', 'Lawyer': '변호사', 'Salesperson': '영업직', 'Manager': '관리자'
    }
    df['Occupation'] = df['Occupation'].map(occ_map).fillna(df['Occupation'])
    
    return df.rename(columns={
        'Occupation': '직업', 
        'Sleep Duration': '수면시간', 
        'Stress Level': '스트레스지수', 
        'BMI Category': 'BMI분류'
    })

df = load_data()

# ==========================================
# 3. 메인 UI 구성
# ==========================================
st.title("📊 내 맘대로 바꾸는 수면 분석 대시보드")

if df.empty:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.stop()

# 상단 안내
st.info("💡 왼쪽 박스에서 '기준'을 바꾸면 그래프의 세로축이 바뀝니다.")

# 레이아웃 나누기
col1, col2 = st.columns([1, 3])

with col1:
    st.write("### ⚙️ 그래프 설정")
    # [핵심] 무엇별로 볼 것인가? (세로축 결정)
    target_category = st.selectbox(
        "분석 기준(세로축) 선택:",
        options=['직업', 'BMI분류', '스트레스지수'],
        index=0
    )
    
    st.write(f"현재 **{target_category}**별 평균 수면시간을 보고 계십니다.")

with col2:
    # 데이터 계산: 선택한 기준별로 수면시간 평균 내기
    chart_data = df.groupby(target_category)['수면시간'].mean().reset_index()
    chart_data = chart_data.sort_values('수면시간', ascending=True)

    # 그래프 그리기
    fig = px.bar(
        chart_data,
        x='수면시간',
        y=target_category,
        orientation='h',
        text_auto='.1f',
        color='수면시간',
        color_continuous_scale='Viridis',
        labels={'수면시간': '평균 수면 시간 (시간)'},
        height=500
    )
    
    # 그래프 스타일 조정
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# 추가 분석: 선택한 기준의 상세 데이터 표
# ------------------------------------------
st.markdown("---")
st.subheader(f"🔍 {target_category}별 상세 수치")
st.dataframe(chart_data, use_container_width=True)
