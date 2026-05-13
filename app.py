import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정 및 디자인
# ==========================================
st.set_page_config(
    page_title="수면 건강 집중 분석 대시보드",
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
    df['혈압상태'] = df['Blood Pressure'].apply(categorize_bp)
    df['BMI Category'] = df['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
    df['Sleep Disorder'] = df['Sleep Disorder'].fillna('없음').replace({'None': '없음', 'Sleep Apnea': '수면 무호흡증', 'Insomnia': '불면증'})
    occ_map = {
        'Software Engineer': '엔지니어', 'Doctor': '의사', 'Sales Representative': '영업직', 
        'Teacher': '교사', 'Nurse': '간호사', 'Engineer': '엔지니어', 'Accountant': '회계사', 
        'Scientist': '과학자', 'Lawyer': '변호사', 'Salesperson': '영업직', 'Manager': '관리자'
    }
    df['Occupation'] = df['Occupation'].map(occ_map).fillna(df['Occupation'])
    
    # 이 부분에 'Daily Steps': '일일걸음수'가 반드시 들어가야 합니다!
    return df.rename(columns={
        'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질', 
        'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애', 
        'Age': '나이', 'Blood Pressure': '혈압원문', 'Daily Steps': '일일걸음수'
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

try:
    df1_raw = load_data_1()
    df2_raw = load_data_2()
except:
    df1_raw = pd.DataFrame()
    df2_raw = pd.DataFrame()

# ==========================================
# 3. 사이드바 동적 필터
# ==========================================
st.sidebar.title(" 동적 필터 조절")

if not df1_raw.empty and not df2_raw.empty:
    min_age = int(min(df1_raw['나이'].min(), df2_raw['나이'].min()))
    max_age = int(max(df1_raw['나이'].max(), df2_raw['나이'].max()))
    age_range = st.sidebar.slider("분석 연령대 설정", min_age, max_age, (min_age, max_age))
    all_occupations = sorted(df1_raw['직업'].unique().tolist())
    selected_occ = st.sidebar.multiselect("분석 직업군 선택", all_occupations, default=all_occupations)

    df1 = df1_raw[(df1_raw['나이'] >= age_range[0]) & (df1_raw['나이'] <= age_range[1]) & (df1_raw['직업'].isin(selected_occ))].copy()
    df2 = df2_raw[(df2_raw['나이'] >= age_range[0]) & (df2_raw['나이'] <= age_range[1])].copy()
else:
    df1, df2 = df1_raw, df2_raw

# ==========================================
# 4. 메인 UI 구성 (탭 순서 변경)
# ==========================================
st.title(" 수면 건강 핵심 데이터 대시보드")

if df1.empty and df2.empty:
    st.error(" 데이터를 불러오지 못했습니다. CSV 파일 위치를 확인해 주세요.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    " 라이프스타일 분석 (생활 습관)", 
    " 수면 효율 분석 (외부 요인)", 
    " 심혈관 건강 분석",
    " 나의 수면 점수 진단",
    " 최적 수면 골든타임"
])
# ------------------------------------------
# 탭 1: 생활 습관
# ------------------------------------------
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("선택된 모집단", f"{len(df1)}명", f"전체 {len(df1_raw)}명 대비")
    c2.metric("평균 수면 시간", f"{df1['수면시간'].mean():.1f}시간")
    c3.metric("평균 스트레스 지수", f"{df1['스트레스지수'].mean():.1f}점")
    c4.metric("평균 수면의 질", f"{df1['수면의질'].mean():.1f}점")
    
    st.markdown("---")
    st.subheader(" 맞춤형 수면시간 & 수면의 질 분석")
    col_sel1, col_sel2 = st.columns([1, 3])
    with col_sel1:
        target_category = st.radio("분석 기준", options=['직업', 'BMI분류', '스트레스지수', '혈압원문'], key='tab1_radio')
    with col_sel2:
        avg_dynamic = df1.groupby(target_category)[['수면시간', '수면의질']].mean().reset_index().sort_values('수면시간')
        fig_dyn = px.bar(avg_dynamic, x='수면시간', y=target_category, orientation='h', color='수면의질', text_auto='.1f', color_continuous_scale='Turbo', title=f"[{target_category}]별 현황")
        st.plotly_chart(fig_dyn, use_container_width=True)

    st.subheader(" 체중(BMI) 분류별 수면 장애 현황")
    bmi_data = df1.groupby(['BMI분류', '수면장애']).size().reset_index(name='인원수')
    fig3 = px.bar(bmi_data, x='BMI분류', y='인원수', color='수면장애', barmode='group', text_auto=True, color_discrete_map={'없음': '#22c55e', '불면증': '#eab308', '수면 무호흡증': '#ef4444'})
    st.plotly_chart(fig3, use_container_width=True)

# ------------------------------------------
# 탭 2: 수면 효율
# ------------------------------------------
with tab2:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("선택된 모집단", f"{len(df2)}명", f"전체 {len(df2_raw)}명 대비")
    c2.metric("평균 수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
    c3.metric("깊은 수면 비중", f"{df2['깊은수면비율'].mean():.1f}%")
    c4.metric("평균 각성 횟수", f"{df2['각성횟수'].mean():.1f}회")

    st.markdown("---")
    col_eff1, col_eff2 = st.columns([1, 2])
    with col_eff1:
        st.subheader(" 수면 단계 구성")
        stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
        fig6 = px.pie(stages, values='비중', names='단계', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig6, use_container_width=True)
    with col_eff2:
        st.subheader(" 외부 요인별 분석")
        factor_choice = st.selectbox("분석 요인 선택", ['알코올 섭취량 (수면 효율)', '운동 빈도 (깊은 수면 비중)', '흡연 여부 (각성 횟수)'])
        if '알코올' in factor_choice:
            avg_f = df2.groupby('알코올')['수면효율'].mean().reset_index()
            fig_f = px.line(avg_f, x='알코올', y='수면효율', markers=True, title="음주와 수면효율")
        elif '운동' in factor_choice:
            avg_f = df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index()
            fig_f = px.line(avg_f, x='운동빈도', y='깊은수면비율', markers=True, title="운동과 깊은 수면")
        else:
            avg_f = df2.groupby('흡연여부')['각성횟수'].mean().reset_index()
            fig_f = px.bar(avg_f, x='흡연여부', y='각성횟수', color='흡연여부', text_auto='.1f', title="흡연과 각성 횟수")
        st.plotly_chart(fig_f, use_container_width=True)

# ------------------------------------------
# 탭 3: 심혈관 건강 분석 (위치 변경)
# ------------------------------------------
with tab3:
    st.header(" 수면 질과 심혈관 건강(고혈압) 상관관계")
    st.markdown("수면 점수(수면의 질)가 낮을수록 고혈압 위험이 어떻게 변하는지 실제 데이터를 통해 확인합니다.")
    
    # 1. 수면의 질 점수별 고혈압 비율 계산
    bp_data = df1.groupby('수면의질')['혈압상태'].value_counts(normalize=True).unstack().fillna(0) * 100
    
    if '고혈압' in bp_data.columns:
        hp_rate = bp_data[['고혈압']].reset_index()
        
        c_hp1, c_hp2 = st.columns([2, 1])
        
        with c_hp1:
            fig_hp = px.line(hp_rate, x='수면의질', y='고혈압', markers=True,
                             title="수면의 질 점수에 따른 고혈압군 비율(%)",
                             color_discrete_sequence=['#ef4444'])
            fig_hp.update_layout(xaxis_title="수면의 질 점수 (1-10점)", yaxis_title="고혈압군 비율 (%)")
            st.plotly_chart(fig_hp, use_container_width=True)
            
        with c_hp2:
            st.markdown("####  분석 인사이트")
            st.write("그래프를 보면 **수면의 질 점수가 낮아질수록 고혈압군에 속하는 인원의 비중이 급격히 증가**하는 경향을 보입니다.")
            st.warning("특히 수면의 질이 4~5점대 이하인 경우, 8점대 이상의 숙면 집단에 비해 고혈압 위험이 유의미하게 높게 관찰됩니다.")
            st.info("수면 부족은 자율신경계 불균형을 초래하여 혈압 상승의 직접적인 원인이 될 수 있음을 시사합니다.")
            
        st.markdown("---")
        st.subheader(" 스트레스 및 BMI와 혈압의 복합 관계")
        col_hp_sub1, col_hp_sub2 = st.columns(2)
        
        with col_hp_sub1:
            # 스트레스와 혈압 상태
            fig_stress_bp = px.histogram(df1, x="스트레스지수", color="혈압상태", barmode="group",
                                         title="스트레스 지수별 혈압 상태 분포",
                                         color_discrete_map={'정상혈압':'#22c55e', '주의혈압':'#34d399', '고혈압 전단계':'#fbbf24', '고혈압':'#ef4444'})
            st.plotly_chart(fig_stress_bp, use_container_width=True)
            
        with col_hp_sub2:
            # BMI와 혈압 상태
            fig_bmi_bp = px.histogram(df1, x="BMI분류", color="혈압상태", barmode="group",
                                      title="BMI 분류별 혈압 상태 분포",
                                      color_discrete_map={'정상혈압':'#22c55e', '주의혈압':'#34d399', '고혈압 전단계':'#fbbf24', '고혈압':'#ef4444'})
            st.plotly_chart(fig_bmi_bp, use_container_width=True)
    else:
        st.warning("현재 선택된 데이터 범위 내에 '고혈압' 데이터가 부족하여 분석 그래프를 표시할 수 없습니다. 사이드바 필터를 조절해 보세요.")

# ------------------------------------------
# 탭 4: 나의 수면 점수 진단 (3컬럼 레이아웃 수정본)
# ------------------------------------------
with tab4:
    st.header(" 나의 수면 건강 자가진단 서비스")
    st.markdown("본인의 데이터를 입력하면 BMI를 자동으로 계산하고 데이터 분석 기반 수면 점수를 산출합니다.")
    
    with st.container(border=True):
        # 입력 부분을 3개의 컬럼으로 분할
        col_in1, col_in2, col_in3 = st.columns(3) 
        
        with col_in1: 
            # 첫 번째 컬럼: 키와 몸무게
            u_height = st.number_input("키 (cm)", 100.0, 250.0, 170.0)
            u_weight = st.number_input("몸무게 (kg)", 30.0, 200.0, 65.0)
            
        with col_in2: 
            # 두 번째 컬럼: 운동횟수와 수면시간
            user_ex = st.slider("일주일 운동 횟수 (회)", 0, 7, 3)
            user_sleep = st.number_input("일일 평균 수면 시간 (시간)", 0.0, 12.0, 7.0, step=0.5)
            
        with col_in3: 
            # 세 번째 컬럼: 음주횟수와 흡연여부
            user_alc = st.number_input("일주일 음주 횟수 (회)", 0, 7, 0)
            user_smoke = st.radio("흡연 여부", ["비흡연", "흡연"], horizontal=True)

        # --- 아래는 기존 점수 계산 로직 (수정 금지) ---
        bmi_val = u_weight / ((u_height / 100) ** 2)
        bmi_status = "정상" if bmi_val < 18.5 else "정상" if bmi_val < 25 else "과체중" if bmi_val < 30 else "비만"
        st.info(f" 당신의 BMI는 **{bmi_val:.1f}**로, **'{bmi_status}'** 상태입니다.")

       # 버튼을 오른쪽으로 밀기 위해 컬럼을 나눕니다. 
        # 비율을 [4, 1]로 주면 버튼이 오른쪽 끝 20% 영역에 위치하게 됩니다.
        btn_space, btn_col = st.columns([2, 2])
        
        with btn_col:
            submit_btn = st.button("내 수면 점수 확인하기 ✨")

        if submit_btn:
            base_score = 90
            if bmi_status == "과체중": base_score -= 7
            elif bmi_status == "비만": base_score -= 18
            if user_smoke == "흡연": base_score -= 12
            base_score -= (user_alc * 4)
            base_score += (user_ex * 5)
            if 7 <= user_sleep <= 8.5: base_score += 10
            elif user_sleep < 6 or user_sleep > 10: base_score -= 10
            
            final_score = max(0, min(100, base_score))
            st.markdown("---")
            st.subheader(f"📊 예상 수면 점수: **{final_score}점**")
            
            if final_score >= 85:
                st.success("🎉 아주 좋은 습관입니다! 숙면 가능성이 매우 높습니다.")
            elif final_score >= 65:
                st.warning("⚖️ 보통입니다. 운동량을 늘리거나 음주를 줄여보세요.")
            else:
                st.error("🚨 개선이 시급합니다. 생활 습관 교정을 추천드립니다.")

# ------------------------------------------
# 탭 5: 최적 수면 골든타임 계산기 (기능 100% 복구 + 3컬럼 레이아웃)
# ------------------------------------------
with tab5:
    st.header(" 데이터 기반 수면 골든타임 계산기")
    st.markdown("내일 기상 시간과 현재 상태를 입력하면, 개인별 최적 취침 시간을 계산해 드립니다.")

    with st.container(border=True):
        # 입력창과 결과창 사이에 여백을 주어 시각적 쾌적함 제공
        col_calc1, col_empty, col_calc2 = st.columns([8, 2, 10]) 
        
        with col_calc1:
            st.subheader(" 나의 상태 및 일정")
            target_wakeup = st.time_input("내일 몇 시에 일어나야 하나요?", value=pd.to_datetime("07:00").time())
            user_quality = st.slider("평소 본인의 수면 만족도(점수)", 1, 10, 7)
            today_steps = st.number_input("오늘 총 몇 걸음 걸으셨나요?", 0, 30000, 6000)
            
            # 카페인 및 흡연 여부 체크 (기존 가로 배치 유지)
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                has_coffee = st.checkbox("오늘 카페인 섭취")
            with c_col2:
                is_smoking = st.checkbox("흡연 여부(니코틴)")

        # --- 로직 계산 (모든 보정 수치 원복) ---
        base_sleep_hr = df1[df1['수면의질'] >= 8]['수면시간'].mean() if not df1.empty else 7.5
        adjustment = 0.0
        
        # 1. 수면 만족도 보정 로직
        if user_quality <= 4:
            adjustment += 1.0
        elif user_quality <= 6:
            adjustment += 0.5
            
        # 2. 활동량 보정 로직
        if today_steps >= 10000:
            adjustment += 0.5
            
        # 3. 카페인 패널티 로직
        if has_coffee:
            adjustment += 0.3
            
        # 4. 흡연(니코틴) 패널티 로직
        if is_smoking:
            adjustment += 0.4

        recommended_duration = base_sleep_hr + adjustment
        
        # 날짜 및 취침 시간 계산
        from datetime import datetime, timedelta
        now = datetime.now()
        wakeup_dt = datetime.combine(now.date() + timedelta(days=1), target_wakeup)
        bedtime_dt = wakeup_dt - timedelta(hours=recommended_duration)

        with col_calc2:
            st.subheader(" 최적 분석 결과")
            st.write("") # 간격 조절
            st.subheader(f"최적 취침 시각: :blue[{bedtime_dt.strftime('%H시 %M분')}]")
            st.metric("권장 수면 시간", f"{recommended_duration:.1f}시간")
            
            # 복합 조언 및 시간 경고 (기존 상세 문구 복구)
            if is_smoking or has_coffee:
                st.markdown("> ** 전문가 조언:** 니코틴과 카페인은 심박수를 높여 깊은 수면(Deep Sleep) 비중을 줄입니다. 평소보다 어둡고 시원한 환경을 조성하세요.")
            
            if bedtime_dt.hour >= 1 and bedtime_dt.hour <= 4:
                st.error(" 데이터상 새벽 1시 이후 취침은 수면 장애 위험을 2배 이상 높입니다.")
            elif recommended_duration >= 8.5:
                st.info(" 현재 상태를 고려할 때 충분한 보충 수면이 필요한 날입니다.")

    st.divider()

   # --- 하단 분석 가이드 (레이아웃 수정: 컬럼1에 집중, 너비 70%) ---
    st.subheader(" 개인 맞춤형 분석 가이드")
    
    # 첫 번째 컬럼의 너비를 7(70%), 두 번째 빈 컬럼을 3(30%)으로 설정
    g_col1, g_col2 = st.columns([7, 3])
    
    with g_col1:
        # 1. 수면 만족도 관련 가이드
        if user_quality <= 4:
            st.error(" 수면 만족도 보정: 만족도가 매우 낮아 1시간의 보충 수면을 권장합니다.")
        elif user_quality <= 6:
            st.warning(" 수면 만족도 보정: 수면 개선을 위해 30분 더 긴 수면이 필요합니다.")
        
        # 2. 활동량 관련 가이드
        if today_steps >= 10000:
            st.info(" 활동량 보정: 높은 활동량으로 인해 회복 수면 30분이 추가되었습니다.")
        elif today_steps < 3000 and today_steps > 0:
            st.write(" 오늘은 활동량이 적어 평소보다 잠들기까지 시간이 걸릴 수 있습니다.")

        # 3. 카페인 관련 가이드
        if has_coffee:
            st.warning(" 카페인 패널티: 카페인은 뇌를 각성시켜 수면 도입을 방해합니다. (+20분)")
        
        # 4. 니코틴 관련 가이드
        if is_smoking:
            st.error(" 니코틴 패널티: 니코틴은 혈압을 높이고 각성 횟수를 늘립니다. 숙면을 위해 25분 더 일찍 준비하세요.")
            
        # 5. 기본 상태 안내
        if not (has_coffee or is_smoking or user_quality <= 6 or today_steps >= 10000):
            st.write("• 현재 입력하신 데이터는 모두 표준 범위 내에 있습니다. 데이터 기반 권장 시간을 유지하세요.")

    with g_col2:
    
        pass
