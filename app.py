import streamlit as st
import pandas as pd

# 투자 내역을 저장할 데이터 프레임 초기화
if "investment_data" not in st.session_state:
    st.session_state["investment_data"] = pd.DataFrame(columns=["서비스명", "상품명", "상품상태", "투자일자", "투자금액", "수익률", "투자기간", "대출유형"])

st.title("📌 P2P 투자 관리")

# 투자 내역 입력 폼
with st.form("investment_form"):
    platform = st.text_input("서비스명 (플랫폼명)")
    product = st.text_input("상품명")
    status = st.selectbox("상품상태", ["투자 중", "상환 완료", "연체"])
    date = st.date_input("투자일자")
    amount = st.number_input("투자금액", min_value=0, step=10000)
    rate = st.number_input("수익률 (%)", min_value=0.0, step=0.1)
    period = st.number_input("투자기간 (개월)", min_value=1, step=1)
    loan_type = st.text_input("대출유형")
    
    submitted = st.form_submit_button("저장")
    
    if submitted:
        new_entry = pd.DataFrame([[platform, product, status, date, amount, rate, period, loan_type]], 
                                 columns=["서비스명", "상품명", "상품상태", "투자일자", "투자금액", "수익률", "투자기간", "대출유형"])
        st.session_state["investment_data"] = pd.concat([st.session_state["investment_data"], new_entry], ignore_index=True)
        st.success("✅ 투자 내역이 저장되었습니다! 다음 회차별 내역을 입력하세요.")
        st.session_state["show_repayment"] = True

# 저장된 투자 내역 출력
st.subheader("📊 투자 내역")
st.dataframe(st.session_state["investment_data"])

# 회차별 내역 입력 폼 (투자 내역 입력 후에만 표시)
if st.session_state.get("show_repayment", False):
    st.subheader("💰 회차별 상환 내역 입력")
    with st.form("repayment_form"):
        period_num = st.number_input("회차", min_value=1, step=1)
        due_date = st.date_input("지급예정일")
        principal = st.number_input("원금", min_value=0, step=10000)
        interest = st.number_input("이자", min_value=0, step=1000)
        tax = st.number_input("세금", min_value=0, step=100)
        fee = st.number_input("수수료", min_value=0, step=100)
        net_income = principal + interest - tax - fee
        repayment_status = st.checkbox("상환 완료")
        
        repayment_submitted = st.form_submit_button("저장")
        
        if repayment_submitted:
            st.success("✅ 회차별 내역이 저장되었습니다!")
