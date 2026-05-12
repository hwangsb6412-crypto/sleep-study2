# 2. 데이터 로드 함수 수정
@st.cache_data
def load_data():
    # 파일이 깃허브에 있다고 가정
    df_health = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
    df_eff = pd.read_csv('Sleep_Efficiency.csv')
    
    # 1번 데이터 한글화 (기존 코드 유지)
    df_health = df_health.rename(columns={
        'Occupation': '직업', 'Sleep Duration': '수면시간', 
        'Quality of Sleep': '수면의질', 'Daily Steps': '걸음수'
    })
    
    # 2번 데이터 한글화 (새로운 인사이트용)
    df_eff = df_eff.rename(columns={
        'Caffeine consumption': '카페인섭취량',
        'Alcohol consumption': '알코올섭취량',
        'Smoking status': '흡연여부',
        'Sleep efficiency': '수면효율'
    })
    return df_health, df_eff

df1, df2 = load_data()

# 탭 메뉴 구성 (이게 시각적으로 깔끔합니다)
tab1, tab2 = st.tabs(["🏥 직업 및 활동 분석", "☕ 라이프스타일 분석 (카페인/알코올)"])

with tab1:
    # 기존에 만드신 직업별 그래프 코드들을 여기 넣으세요.
    st.header("직업군별 수면 상태")
    # ... 기존 코드 ...

with tab2:
    st.header("☕ 카페인과 알코올이 수면에 미치는 영향")
    st.markdown("이 섹션에서는 수면 효율 데이터를 통해 외부 요인을 분석합니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        # 카페인과 수면 효율의 관계
        fig_caf = px.box(df2, x='카페인섭취량', y='수면효율', points="all",
                         title="카페인 섭취량에 따른 수면 효율", color_discrete_sequence=['#FFCC00'])
        st.plotly_chart(fig_caf, use_container_width=True)
        
    with col2:
        # 알코올과 수면 효율의 관계
        fig_alc = px.box(df2, x='알코올섭취량', y='수면효율', points="all",
                         title="음주량에 따른 수면 효율", color_discrete_sequence=['#FF6666'])
        st.plotly_chart(fig_alc, use_container_width=True)
