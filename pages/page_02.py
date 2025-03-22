import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="P2P 투자 대시보드", layout="wide")

# 메인 화면으로 돌아가기 버튼
if st.button("🔙 메인 화면으로 돌아가기"):
    st.switch_page("app.py")

# 대시보드 상단 통계 섹션
st.title("📊 P2P 투자 대시보드")

# 필요한 데이터 확인
if "dashboard_repayments" not in st.session_state or not st.session_state["dashboard_repayments"]:
    st.info("📝 상환 내역이 없습니다. 먼저 상환 내역을 입력해주세요.")
elif "investment_data" not in st.session_state or st.session_state["investment_data"].empty:
    st.info("📝 투자 내역이 없습니다. 먼저 투자 내역을 입력해주세요.")
else:
    # 투자 데이터 로드
    investment_df = st.session_state["investment_data"]
    
    # 상환 데이터 처리
    repayment_data = st.session_state["dashboard_repayments"]
    repayment_df = pd.DataFrame(repayment_data)
    
    # 상단 통계 카드 (investment_df에서 가져옴)
    if "투자금액" in investment_df.columns:
        total_investment = investment_df["투자금액"].sum()
    else:
        total_investment = 0
        
    if "수익률" in investment_df.columns:
        avg_interest_rate = investment_df["수익률"].mean()
    else:
        avg_interest_rate = 0
        
    if "상품상태" in investment_df.columns:
        active_investments = investment_df[investment_df["상품상태"] == "투자 중"].shape[0]
        completed_investments = investment_df[investment_df["상품상태"] == "상환 완료"].shape[0]
    else:
        active_investments = 0
        completed_investments = 0
    
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
    tab1, tab2 = st.tabs(["투자 내역", "상환 내역"])
    
    with tab1:
        st.dataframe(investment_df, use_container_width=True)
    
    with tab2:
        st.subheader("회차별 상환 내역")
        st.dataframe(repayment_df, use_container_width=True)
        
        # 상환 완료된 항목 수
        if "상환완료" in repayment_df.columns:
            completed_repayments = repayment_df["상환완료"].sum()
            total_repayments = len(repayment_df)
            
            # 총 상환 금액 계산
            completed_df = repayment_df[repayment_df["상환완료"]]
            total_principal = completed_df["원금"].sum() if "원금" in completed_df.columns else 0
            total_interest = completed_df["이자"].sum() if "이자" in completed_df.columns else 0
            total_tax = completed_df["세금"].sum() if "세금" in completed_df.columns else 0
            total_fee = completed_df["수수료"].sum() if "수수료" in completed_df.columns else 0
            
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
        
        # 상환 차트: 회차별 원금 및 이자 차트
        if not repayment_df.empty and "회차" in repayment_df.columns and "원금" in repayment_df.columns and "이자" in repayment_df.columns:
            fig_payment = px.bar(
                repayment_df.sort_values("회차"), 
                x="회차", 
                y=["원금", "이자"],
                title="회차별 원금 및 이자",
                barmode="group"
            )
            st.plotly_chart(fig_payment, use_container_width=True)
            
    # 조건부 탭3: 투자 데이터에 필요한 컬럼이 있는 경우에만 표시
    if (("서비스명" in investment_df.columns) and 
        ("투자금액" in investment_df.columns) and
        len(investment_df) > 0):
        
        st.subheader("통계 분석")
        
        # 플랫폼별 투자 금액 시각화
        platform_data = investment_df.groupby("서비스명")["투자금액"].sum().reset_index()
        
        # 파이 차트 
        fig1 = px.pie(platform_data, values="투자금액", names="서비스명", 
                    title="플랫폼별 투자 비중",
                    hole=0.3)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 기타 차트는 필요한 컬럼이 있는 경우에만 표시
        if "상품상태" in investment_df.columns:
            status_data = investment_df.groupby("상품상태")["투자금액"].sum().reset_index()
            fig2 = px.bar(status_data, x="상품상태", y="투자금액", 
                        title="상태별 투자 금액",
                        color="상품상태", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)
        
        # 이하 다른 차트들도 비슷하게 조건부로 표시
