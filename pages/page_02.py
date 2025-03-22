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

# 투자 데이터가 있는 경우에만 대시보드 표시
if "dashboard_repayments" in st.session_state and not st.session_state["dashboard_repayments"].empty:
    investment_df = st.session_state["dashboard_repayments"]
    
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
        if "dashboard_repayments" in st.session_state and st.session_state["dashboard_repayments"]:
            st.subheader("회차별 상환 내역")
            repayment_df = pd.DataFrame(st.session_state["repayment_data"])
            st.dataframe(repayment_df, use_container_width=True)
            
            # 상환 완료된 항목 수
            completed_repayments = sum(item["상환완료"] for item in st.session_state["dashboard_repayments"])
            total_repayments = len(st.session_state["repayment_data"])
            
            # 총 상환 금액 계산
            total_principal = sum(item["원금"] for item in st.session_state["dashboard_repayments"] if item["상환완료"])
            total_interest = sum(item["이자"] for item in st.session_state["dashboard_repayments"] if item["상환완료"])
            total_tax = sum(item["세금"] for item in st.session_state["dashboard_repayments"] if item["상환완료"])
            total_fee = sum(item["수수료"] for item in st.session_state["dashboard_repayments"] if item["상환완료"])
            
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
        if "대출유형" in investment_df.columns and not all(pd.isna(investment_df["대출유형"])):
            loan_type_data = investment_df.groupby("대출유형")["투자금액"].sum().reset_index()
            fig3 = px.pie(loan_type_data, values="투자금액", names="대출유형", 
                          title="대출 유형별 투자 비중")
            st.plotly_chart(fig3, use_container_width=True)
            
        # 시간에 따른 투자 추이
        if "투자일자" in investment_df.columns:
            investment_df["투자일자"] = pd.to_datetime(investment_df["투자일자"])
            investment_df_sorted = investment_df.sort_values("투자일자")
            investment_df_sorted["누적 투자금액"] = investment_df_sorted["투자금액"].cumsum()
            
            fig4 = px.line(investment_df_sorted, x="투자일자", y="누적 투자금액", 
                          title="시간에 따른 누적 투자금액 추이",
                          markers=True)
            st.plotly_chart(fig4, use_container_width=True)
        
        # 수익률 분포
        fig5 = px.histogram(investment_df, x="수익률", 
                           title="수익률 분포",
                           nbins=10)
        st.plotly_chart(fig5, use_container_width=True)
        
        # 추가적인 차트: 투자기간 vs 수익률
        fig6 = px.scatter(investment_df, x="투자기간", y="수익률",
                         title="투자기간 vs 수익률",
                         # size 파라미터가 문제의 원인
                         size=investment_df["투자금액"].astype(float),  # narwhals Series를 float로 변환
                         hover_data=["서비스명", "상품명"])
        st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("📝 투자 내역이 없습니다. 메인 화면에서 데이터를 입력해주세요.")
