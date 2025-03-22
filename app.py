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
    
    # 저장된 회차별 상환 내역 표시
    if st.session_state["repayment_data"]:
        columns = ["회차", "지급예정일", "원금", "이자", "세금", "수수료", "상환완료"]
        repayment_df = pd.DataFrame(st.session_state["repayment_data"], columns=columns)
        st.dataframe(repayment_df, hide_index=True)
    
    # 편집 모드 토글 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.session_state["repayment_data"] and st.button("🪄 수정"):
            st.session_state["edit_mode"] = not st.session_state["edit_mode"]
            if st.session_state["edit_mode"]:
                # 편집 모드를 활성화할 때 기존 데이터를 편집용 상태로 복사
                if "edit_repayments" not in st.session_state:
                    st.session_state["edit_repayments"] = st.session_state["repayment_data"].copy()
            st.rerun()
    
    # 편집 모드일 때 기존 데이터 편집 인터페이스 표시
    if st.session_state["edit_mode"]:
        st.subheader("✏️ 회차별 상환 내역 수정")

        indices_to_delete = []
        
        for i, repayment in enumerate(st.session_state["edit_repayments"]):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 2, 2, 2, 2, 2, 1, 1])
            with col1:
                repayment["회차"] = st.number_input(f"회차", min_value=1, step=1, key=f"edit_period_num_{i}", value=repayment["회차"])
            with col2:
                repayment["지급예정일"] = st.date_input("지급예정일", key=f"edit_due_date_{i}", value=repayment["지급예정일"])
            with col3:
                repayment["원금"] = st.number_input("원금", min_value=0, step=10000, key=f"edit_principal_{i}", value=repayment["원금"])
            with col4:
                repayment["이자"] = st.number_input("이자", min_value=0, step=1000, key=f"edit_interest_{i}", value=repayment["이자"])
            with col5:
                repayment["세금"] = st.number_input("세금", min_value=0, step=100, key=f"edit_tax_{i}", value=repayment["세금"])
            with col6:
                repayment["수수료"] = st.number_input("수수료", min_value=0, step=100, key=f"edit_fee_{i}", value=repayment["수수료"])
            with col7:
                repayment["상환완료"] = st.checkbox("완료", key=f"edit_repayment_status_{i}", value=repayment["상환완료"])
            with col8:
                if st.button("🗑 삭제", key=f"delete_repayment_{i}"):
                    indices_to_delete.append(i)
        
        if indices_to_delete:
            for idx in sorted(indices_to_delete, reverse=True):
                del st.session_state["edit_repayments"][idx]
            st.rerun()
            
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("➕ 추가"):
                st.session_state["edit_repayments"].append({"회차": 1, "지급예정일": None, "원금": 0, "이자": 0, "세금": 0, "수수료": 0, "상환완료": False})
                st.rerun()
        with col2:
            if st.button("✔️ 수정 완료"):
                st.session_state["repayment_data"] = st.session_state["edit_repayments"].copy()
                st.session_state["edit_mode"] = False
                st.success("✅ 회차별 상환 내역이 수정되었습니다!")
                st.rerun()
        with col3:
            if st.button("❌ 취소"):
                st.session_state["edit_mode"] = False
                st.rerun()
    
    # 편집 모드가 아닐 때만 새로운 회차 추가 인터페이스 표시
    if not st.session_state["edit_mode"]:
        st.subheader("➕ 새로운 회차 추가")
        
        if "new_repayments" not in st.session_state:
            st.session_state["new_repayments"] = []
        
        for i, repayment in enumerate(st.session_state["new_repayments"]):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 2, 2, 2, 2, 2, 1])
            with col1:
                repayment["회차"] = st.number_input(f"회차", min_value=1, step=1, key=f"period_num_{i}", value=repayment["회차"])
            with col2:
                repayment["지급예정일"] = st.date_input("지급예정일", key=f"due_date_{i}", value=repayment["지급예정일"])
            with col3:
                repayment["원금"] = st.number_input("원금", min_value=0, step=10000, key=f"principal_{i}", value=repayment["원금"])
            with col4:
                repayment["이자"] = st.number_input("이자", min_value=0, step=1000, key=f"interest_{i}", value=repayment["이자"])
            with col5:
                repayment["세금"] = st.number_input("세금", min_value=0, step=100, key=f"tax_{i}", value=repayment["세금"])
            with col6:
                repayment["수수료"] = st.number_input("수수료", min_value=0, step=100, key=f"fee_{i}", value=repayment["수수료"])
            with col7:
                repayment["상환완료"] = st.checkbox("완료", key=f"repayment_status_{i}", value=repayment["상환완료"])
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("➕ 추가"):
                new_repayment = {"회차": len(st.session_state["new_repayments"]) + 1, "지급예정일": None, "원금": 0, "이자": 0, "세금": 0, "수수료": 0, "상환완료": False}
                st.session_state["new_repayments"].append(new_repayment)
                st.rerun()
        with col2:
            if st.button("➖ 삭제") and st.session_state["new_repayments"]:
                st.session_state["new_repayments"].pop()
                st.rerun()
        
        save_col1, save_col2 = st.columns([1, 1])
        with save_col1:
            if st.button("💾 저장"):
                st.session_state["repayment_data"].extend(st.session_state["new_repayments"])
                st.session_state["new_repayments"] = []
                st.success("✅ 회차별 상환 내역이 저장되었습니다!")
                st.rerun()
        
        # 대시보드로 이동 버튼
        with save_col2:
            if st.button("📊 대시보드로 이동"):
                st.switch_page("dashboard_03.py")
