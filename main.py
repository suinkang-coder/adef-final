import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# 1. 제미나이 설정 (가장 호환성 높은 gemini-pro 모델 사용)
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("🔑 .streamlit/secrets.toml 파일에 GEMINI_API_KEY가 없습니다.")
        st.stop()
    
    # 404 에러 방지를 위해 가장 안정적인 'gemini-pro' 명칭 사용
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"⚠️ API 설정 오류: {e}")
    st.stop()

# 페이지 레이아웃 설정 (와이드 모드)
st.set_page_config(page_title="NEPLES 광고 성과 분석 엔진", layout="wide")

# --- 2. 사이드바 (실명 제거 및 브랜딩 강화) ---
with st.sidebar:
    st.markdown("## 🏆 NEPLES AD AI")
    st.markdown("### 시니어 퍼포먼스 마케터 대장")
    st.write("---")
    st.info("💡 **시스템 가이드**\n1. 통합 리포트(CSV) 업로드\n2. 좌측: 자동 성과 보고서 확인\n3. 우측: 챗봇과 세부 전략 고도화")
    st.caption(f"최종 분석 세션: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown("---")
    st.write("✅ **자동 분석 카테고리**\n상시 / 카탈로그 / 바우처")
    st.write("✅ **분석 매체**\n메타(ASC), 구글, DSP, 네이버")

st.title("🔥 네플스 광고 성과 자동 진단 & 전략 에이전트")
st.markdown("---")

# 세션 상태 초기화 (대화 기록 저장)
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'auto_report' not in st.session_state:
    st.session_state['auto_report'] = ""

# 3. 파일 업로드
uploaded_file = st.file_uploader("📂 광고 통합리포트(CSV)를 업로드하세요", type=['csv'])

if uploaded_file is not None:
    # 데이터 로드 및 컬럼명 공백 제거
    try:
        df = pd.read_csv(uploaded_file)
    except:
        df = pd.read_csv(uploaded_file, encoding='cp949')
    
    # 모든 컬럼명의 앞뒤 공백/탭 제거
    df.columns = [c.strip() for c in df.columns]

    st.success(f"✔️ 데이터 연결 성공! ({len(df)}개 행 데이터 분석 준비 완료)")

    # --- 4. 화면 분할 (좌: 자동 분석 보고서 / 우: 챗봇 대화창) ---
    col1, col2 = st.columns([1.8, 1])

    # --- [왼쪽: 자동 성과 분석 영역] ---
    with col1:
        st.subheader("🤖 자동 데이터 성과 진단 리포트")
        
        # 핵심 분석 컬럼 설정
        target_biz = '사업부 구분'
        target_spend = 'Spend (net)'
        target_revenue = 'AF Revenue'
        target_order = 'pb_order_kurlynmart'

        # 필수 컬럼 존재 여부 체크 후 자동 분석
        if target_biz in df.columns:
            if not st.session_state['auto_report']:
                with st.spinner("시니어 마케터의 안목으로 실적을 분석 중입니다..."):
                    # 주요 지표 요약 계산
                    metrics = [c for c in [target_spend, target_revenue, target_order] if c in df.columns]
                    biz_summary = df.groupby(target_biz)[metrics].sum().to_string()
                    
                    # 자동 분석 프롬프트 (실명 언급 제거 및 전문성 강화)
                    auto_prompt = f"""
                    너는 20년차 시니어 퍼포먼스 마케터 대장이야. 
                    네플스(NEPLES) 통합 리포트 데이터를 기반으로 마케팅팀을 위한 전문적인 성과 보고서를 작성해줘.

                    [데이터 현황]
                    - 사업부 구분(상시/카탈로그/바우처)별 성과 요약:
                    {biz_summary}
                    
                    [분석 가이드라인]
                    1. **사업부 구분**별로 ROAS 및 광고 지출 대비 매출 효율을 날카롭게 진단할 것.
                    2. 상시, 카탈로그, 바우처 캠페인 중 현재 성과가 가장 우수한 그룹과 개선이 시급한 그룹을 명확히 구분할 것.
                    3. 단순히 수치를 나열하지 말고, 시니어 마케터로서 향후 운영 방향(**Stop / Keep / Scale-up**)을 제안할 것.
                    4. 전문적이면서 군더더기 없는 단호한 말투로 작성할 것.
                    """
                    
                    try:
                        auto_res = model.generate_content(auto_prompt)
                        st.session_state['auto_report'] = auto_res.text
                    except Exception as e:
                        st.error(f"데이터 분석 중 오류가 발생했습니다: {e}")
            
            # 결과 출력
            st.markdown(st.session_state['auto_report'])
        else:
            st.warning(f"⚠️ '{target_biz}' 컬럼을 찾을 수 없습니다. 리포트의 컬럼명을 확인해주세요.")
            with st.expander("현재 인식된 컬럼 목록 보기"):
                st.write(df.columns.tolist())

    # --- [오른쪽: 대화형 챗봇 영역] ---
    with col2:
        st.subheader("💬 전략 심화 챗봇")
        
        # 채팅창 구현
        chat_placeholder = st.container(height=550)
        
        # 이전 대화 내역 표시
        for chat in st.session_state['chat_history']:
            with chat_placeholder.chat_message(chat["role"]):
                st.write(chat["content"])

        # 채팅 입력창
        if prompt := st.chat_input("추가 지표 분석이나 전략에 대해 질문하세요"):
            st.session_state['chat_history'].append({"role": "user", "content": prompt})
            with chat_placeholder.chat_message("user"):
                st.write(prompt)

            # AI 답변 생성
            with chat_placeholder.chat_message("assistant"):
                msg_placeholder = st.empty()
                with st.spinner("전략 검토 중..."):
                    report_context = st.session_state['auto_report']
                    full_prompt = f"""
                    배경 데이터 분석 결과: {report_context}
                    
                    사용자 질문: {prompt}
                    
                    너는 20년차 시니어 마케터 대장으로서 위 분석 내용을 바탕으로 실행 가능하고 인사이트 있는 조언을 해줘.
                    """
                    
                    try:
                        chat_res = model.generate_content(full_prompt)
                        response_text = chat_res.text
                        msg_placeholder.write(response_text)
                        st.session_state['chat_history'].append({"role": "assistant", "content": response_text})
                    except Exception as e:
                        st.error(f"응답 생성 중 오류가 발생했습니다: {e}")

else:
    st.info("👆 위쪽 업로드 버튼을 통해 광고 리포트(CSV)를 업로드하면 자동 성과 진단이 시작됩니다.")