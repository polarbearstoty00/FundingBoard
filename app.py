import streamlit as st
import pandas as pd

# 투자 내역을 저장할 데이터 프레임 초기화
if "investment_data" not in st.session_state:
    st.session_state["investment_data"] = pd.DataFrame(columns=["서비스명", "상품명", "상품상태", "투자일자", "투자금액", "수익률", "투자기간", "대출유형"])
if "repayment_data" not in st.session_state:
    st.session_state["repayment_data"] = []
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "투자 내역 입력"

st.set_page_config(page_title="P2P 투자 관리", layout="wide")
st.title("📌 P2P 투자 관리")

if st.session_state["current_page"] == "투자 내역 입력":
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
            st.success("✅ 투자 내역이 저장되었습니다! 회차별 내역 입력 페이지로 이동합니다.")
            st.session_state["current_page"] = "회차별 상환 내역 입력"
            st.rerun()

elif st.session_state["current_page"] == "회차별 상환 내역 입력":
    st.subheader("📊 투자 내역")
    st.dataframe(st.session_state["investment_data"], hide_index=True)
    
    st.subheader("💰 회차별 상환 내역 입력")
    columns = ["회차", "지급예정일", "원금", "이자", "세금", "수수료", "상환완료"]
    repayment_df = pd.DataFrame(st.session_state["repayment_data"], columns=columns)
    
    st.dataframe(repayment_df, hide_index=True)
    
    if "new_repayments" not in st.session_state:
        st.session_state["new_repayments"] = []
    
    for i, repayment in enumerate(st.session_state["new_repayments"]):
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 2, 2, 2, 2, 2, 1])
        with col1:
            repayment["회차"] = st.number_input(f"", min_value=1, step=1, key=f"period_num_{i}", value=repayment["회차"])
        with col2:
            repayment["지급예정일"] = st.date_input("", key=f"due_date_{i}", value=repayment["지급예정일"])
        with col3:
            repayment["원금"] = st.number_input("", min_value=0, step=10000, key=f"principal_{i}", value=repayment["원금"])
        with col4:
            repayment["이자"] = st.number_input("", min_value=0, step=1000, key=f"interest_{i}", value=repayment["이자"])
        with col5:
            repayment["세금"] = st.number_input("", min_value=0, step=100, key=f"tax_{i}", value=repayment["세금"])
        with col6:
            repayment["수수료"] = st.number_input("", min_value=0, step=100, key=f"fee_{i}", value=repayment["수수료"])
        with col7:
            repayment["상환완료"] = st.checkbox("", key=f"repayment_status_{i}", value=repayment["상환완료"])
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("➕ 추가"):
            new_repayment = {"회차": len(st.session_state["new_repayments"]) + 1, "지급예정일": None, "원금": 0, "이자": 0, "세금": 0, "수수료": 0, "상환완료": False}
            st.session_state["new_repayments"].append(new_repayment)
            st.rerun()
    with col2:
        if st.button("➖ 삭제") and st.session_state["new_repayments"]:
            st.session_state["new_repayments"].pop()
            st.rerun()
    
    if st.button("저장"):
        st.session_state["repayment_data"].extend(st.session_state["new_repayments"])
        st.session_state["new_repayments"] = []
        st.success("✅ 회차별 상환 내역이 저장되었습니다!")
        st.session_state["show_edit_button"] = True  # 수정 버튼 활성화
        st.rerun()
    
    # 저장 후에만 수정 버튼이 보이도록 설정
    if st.session_state.get("show_edit_button", False):
        if st.button("✏ 수정"):
            st.session_state["current_page"] = "수정 모드"
            st.rerun()
