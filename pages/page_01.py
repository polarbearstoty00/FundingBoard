import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="펀딩보드", layout="wide")

# "🔙 이전 화면" 버튼 동작
if st.button("🔙 이전 화면"):
    # 편집 중이던 임시 입력 데이터 초기화
    if "new_repayments" in st.session_state:
        del st.session_state["new_repayments"]
    if "edit_repayments" in st.session_state:
        del st.session_state["edit_repayments"]
    
    # 페이지 이동
    st.switch_page("app.py")

# 대시보드 상단 통계 섹션
st.title("💰 회차별 상환 내역 입력")

# 투자 내역 표시
st.subheader("📊 투자 내역")

if "investment_data" in st.session_state and not st.session_state["investment_data"].empty:
    st.dataframe(st.session_state["investment_data"], hide_index=True)
else:
    st.warning("❌ 저장된 투자 내역이 없습니다. 먼저 투자 내역을 입력하세요.")

# 저장된 회차별 상환 내역 표시
if st.session_state.get("repayment_data"):
    columns = ["회차", "지급예정일", "원금", "이자", "세금", "수수료", "상환완료"]
    repayment_df = pd.DataFrame(st.session_state["repayment_data"], columns=columns)
    st.dataframe(repayment_df, hide_index=True)

# 편집 모드 토글 버튼
col1, col2, col3 = st.columns([1, 1, 1])
with col3:
    if st.session_state.get("repayment_data") and st.button("🪄 수정"):
        st.session_state["edit_mode"] = not st.session_state.get("edit_mode", False)
        if st.session_state["edit_mode"]:
            # 편집 모드를 활성화할 때 기존 데이터를 편집용 상태로 복사
            if "edit_repayments" not in st.session_state:
                st.session_state["edit_repayments"] = st.session_state["repayment_data"].copy()
        st.rerun()

# 편집 모드일 때 기존 데이터 편집 인터페이스 표시
if st.session_state.get("edit_mode"):
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
            repayment["이자"] = st.number_input("이자", min_value=0, step=10, key=f"edit_interest_{i}", value=repayment["이자"])
        with col5:
            repayment["세금"] = st.number_input("세금", min_value=0, step=10, key=f"edit_tax_{i}", value=repayment["세금"])
        with col6:
            repayment["수수료"] = st.number_input("수수료", min_value=0, step=10, key=f"edit_fee_{i}", value=repayment["수수료"])
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
if not st.session_state.get("edit_mode", False):
    st.subheader("➕ 상세 내역 입력")

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
            repayment["이자"] = st.number_input("이자", min_value=0, step=10, key=f"interest_{i}", value=repayment["이자"])
        with col5:
            repayment["세금"] = st.number_input("세금", min_value=0, step=10, key=f"tax_{i}", value=repayment["세금"])
        with col6:
            repayment["수수료"] = st.number_input("수수료", min_value=0, step=10, key=f"fee_{i}", value=repayment["수수료"])
        with col7:
            repayment["상환완료"] = st.checkbox("완료", key=f"repayment_status_{i}", value=repayment["상환완료"])

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        btn_col1, btn_col2 = st.columns([1, 1])  # 내부에서 다시 컬럼 생성

        with btn_col1:
            if st.button("➕ 추가"):
                new_repayment = {"회차": len(st.session_state["new_repayments"]) + 1, "지급예정일": None, "원금": 0, "이자": 0, "세금": 0, "수수료": 0, "상환완료": False}
                st.session_state["new_repayments"].append(new_repayment)
                st.rerun()
        with btn_col2:
            if st.button("➖ 삭제") and st.session_state["new_repayments"]:
                st.session_state["new_repayments"].pop()
                st.rerun()
            
    save_col1, save_col2, save_col3 = st.columns([1, 1, 1])
    with save_col1:
        if st.button("💾 저장"):
            st.session_state["repayment_data"].extend(st.session_state["new_repayments"])
            st.session_state["new_repayments"] = []
            st.success("ℹ️ 상세 내역이 저장되었습니다!")
            st.rerun()

    with save_col3:
        if st.button("📊 대시보드로 이동"):
            st.switch_page("pages/page_02.py")
