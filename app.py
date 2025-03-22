import streamlit as st
import pandas as pd
from datetime import datetime

# 투자 내역을 저장할 데이터 프레임 초기화
if "investment_data" not in st.session_state:
    st.session_state["investment_data"] = pd.DataFrame(columns=["서비스명", "상품명", "상품상태", "투자일자", "투자금액", "수익률", "투자기간", "대출유형"])
if "repayment_data" not in st.session_state:
    st.session_state["repayment_data"] = []
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "투자 내역 입력"
if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = False

st.set_page_config(page_title="P2P 투자 관리", layout="wide")
st.title("📌 P2P 투자 관리")

# JavaScript로 Enter 키 입력 방지
st.markdown(
    """
    <script>
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
            }
        });
    </script>
    """,
    unsafe_allow_html=True,
)

if st.session_state["current_page"] == "투자 내역 입력":
    # 투자 내역 입력 폼
    with st.form("investment_form"):
        platform = st.text_input("서비스명 (플랫폼명)")
        product = st.text_input("상품명")
        status = st.selectbox("상품상태", ["투자중", "상환완료", "연체"])
        date = st.date_input("투자일자")
        amount = st.number_input("투자금액", min_value=0, step=10000)
        rate = st.number_input("수익률 (%)", min_value=0.0, step=0.1)
        period = st.number_input("투자기간 (개월)", min_value=1, step=1)
        loan_type = st.selectbox("대출유형", ["부동산 담보", "어음·매출채권 담보", "기타 담보", "개인 신용", "법인 신용"])
        
        submitted = st.form_submit_button("저장")

        if submitted:
            new_entry = pd.DataFrame([[platform, product, status, pd.to_datetime(date).date(), amount, rate, period, loan_type]], 
                                     columns=["서비스명", "상품명", "상품상태", "투자일자", "투자금액", "수익률", "투자기간", "대출유형"])
            st.session_state["investment_data"] = pd.concat([st.session_state["investment_data"], new_entry], ignore_index=True)

            st.success("✅ 투자 내역이 저장되었습니다! 회차별 내역 입력 페이지로 이동합니다.")
        
            # 페이지 이동
            st.switch_page("pages/page_01.py")
