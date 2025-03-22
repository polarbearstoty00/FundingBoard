import streamlit as st
import pandas as pd

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
        
        if st.button("💾 저장"):
            st.session_state["repayment_data"].extend(st.session_state["new_repayments"])
            st.session_state["new_repayments"] = []
            st.success("✅ 회차별 상환 내역이 저장되었습니다!")
            st.rerun()

        # 다음 버튼 추가 - 대시보드 페이지로 이동
        with save_col2:
            if st.button("📊 대시보드로 이동"):
                navigate_to("대시보드")

elif st.session_state["current_page"] == "대시보드":
    # 페이지 내비게이션 버튼 (대시보드에서 다른 페이지로 이동하기 위한 버튼)
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🔙 투자 내역 입력"):
            navigate_to("투자 내역 입력")
    with col2:
        if st.button("🔙 회차별 상환 내역"):
            navigate_to("회차별 상환 내역 입력")
    
    # 대시보드 상단 통계 섹션
    st.header("📊 P2P 투자 대시보드")
    
    # 투자 데이터가 있는 경우에만 대시보드 표시
    if not st.session_state["investment_data"].empty:
        investment_df = st.session_state["investment_data"]
        
        # 상단 통계 카드
        total_investment = investment_df["투자금액"].sum()
        avg_interest_rate = investment_df["수익률"].mean()
        active_investments = investment_df[investment_df["상품상태"] == "투자 중"].shape[0]
        completed_investments = investment_df[investment_df["상품상태"] == "상환 완료"].shape[0]
        
        st.subheader("요약")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 투자금액", f"{total_investment:,}원")
        with col2:
            st.metric("평균 수익률", f"{avg_interest_rate:.2f}%")
        with col3:
            st.metric("투자 중인 상품", f"{active_investments}개")
        with col4:
            st.metric("상환 완료 상품", f"{completed_investments}개")
        
        # 투자 현황 탭
        st.subheader("투자 현황")
        tab1, tab2 = st.tabs(["투자 내역", "플랫폼별 분석"])
        
        with tab1:
            st.dataframe(investment_df, use_container_width=True)
            
            # 상환 내역이 있는 경우 표시
            if st.session_state["repayment_data"]:
                st.subheader("회차별 상환 내역")
                repayment_df = pd.DataFrame(st.session_state["repayment_data"])
                st.dataframe(repayment_df, use_container_width=True)
                
                # 상환 완료된 항목 수
                completed_repayments = sum(item["상환완료"] for item in st.session_state["repayment_data"])
                total_repayments = len(st.session_state["repayment_data"])
                
                # 총 상환 금액 계산
                total_principal = sum(item["원금"] for item in st.session_state["repayment_data"] if item["상환완료"])
                total_interest = sum(item["이자"] for item in st.session_state["repayment_data"] if item["상환완료"])
                total_tax = sum(item["세금"] for item in st.session_state["repayment_data"] if item["상환완료"])
                total_fee = sum(item["수수료"] for item in st.session_state["repayment_data"] if item["상환완료"])
                
                # 상환 내역 요약
                st.subheader("상환 내역 요약")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("상환 진행률", f"{completed_repayments}/{total_repayments}")
                with col2:
                    st.metric("총 상환 원금", f"{total_principal:,}원")
                with col3:
                    st.metric("총 이자 수익", f"{total_interest:,}원")
                with col4:
                    net_interest = total_interest - total_tax - total_fee
                    st.metric("순 이자 수익", f"{net_interest:,}원")
        
        with tab2:
            # 플랫폼별 투자 금액 시각화
            platform_data = investment_df.groupby("서비스명")["투자금액"].sum().reset_index()
            
            # 파이 차트 
            fig1 = px.pie(platform_data, values="투자금액", names="서비스명", 
                          title="플랫폼별 투자 비중",
                          hole=0.3)
            st.plotly_chart(fig1, use_container_width=True)
            
            # 상태별 투자 금액
            status_data = investment_df.groupby("상품상태")["투자금액"].sum().reset_index()
            fig2 = px.bar(status_data, x="상품상태", y="투자금액", 
                         title="상태별 투자 금액",
                         color="상품상태", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)
            
            # 대출 유형별 분석 (대출 유형이 있는 경우)
            if not all(pd.isna(investment_df["대출유형"])):
                loan_type_data = investment_df.groupby("대출유형")["투자금액"].sum().reset_index()
                fig3 = px.pie(loan_type_data, values="투자금액", names="대출유형", 
                              title="대출 유형별 투자 비중")
                st.plotly_chart(fig3, use_container_width=True)
                
            # 시간에 따른 투자 추이
            investment_df["투자일자"] = pd.to_datetime(investment_df["투자일자"])
            investment_df = investment_df.sort_values("투자일자")
            investment_df["누적 투자금액"] = investment_df["투자금액"].cumsum()
            
            fig4 = px.line(investment_df, x="투자일자", y="누적 투자금액", 
                          title="시간에 따른 누적 투자금액 추이",
                          markers=True)
            st.plotly_chart(fig4, use_container_width=True)
            
            # 수익률 분포
            fig5 = px.histogram(investment_df, x="수익률", 
                               title="수익률 분포",
                               nbins=10)
            st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("📝 투자 내역이 없습니다. '투자 내역 입력' 페이지에서 데이터를 입력해주세요.")
