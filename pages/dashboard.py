import streamlit as st
import pandas as pd

st.set_page_config(page_title="P2P 투자 관리", layout="wide")

# 업로드된 파일을 저장할 세션 상태 초기화
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = {}
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None

st.title('P2P 투자 내역 대시보드')

# 파일 업로드 기능 (여러 개 가능)
uploaded_files = st.file_uploader("엑셀 파일 업로드", type=["xls", "xlsx"], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_files.extend(uploaded_files)

# 데이터 처리 및 표시
if st.session_state.uploaded_files:
    all_data = []
    for file in st.session_state.uploaded_files:
        xls = pd.ExcelFile(file)
        df1 = pd.read_excel(xls, sheet_name='세부 투자내역(투자진행중)')
        df2 = pd.read_excel(xls, sheet_name='세부 투자내역(투자진행중) 회차별 상세정보')
        
        # 첫 번째 시트: 중복 제거 (업체명, 상품명 기준)
        df1_unique = df1[['업체명', '상품명']].drop_duplicates()
        all_data.append((df1_unique, df2))
    
    # 업체명 기준 그룹화
    company_dict = {company: df1 for df1, _ in all_data for company in df1['업체명'].unique()}
    df2_combined = pd.concat([df2 for _, df2 in all_data], ignore_index=True)
    
    for company in company_dict.keys():
        if st.button(company, key=f'company_{company}'):
            st.session_state.selected_company = company
    
    if st.session_state.selected_company:
        df1_selected = company_dict[st.session_state.selected_company]
        
        for product in df1_selected['상품명'].unique():
            with st.expander(product):
                # 두 번째 시트에서 상품명 기준으로 필터링하여 회차 내역 표시
                df_product_details = df2_combined[df2_combined['상품명'] == product]
                st.dataframe(df_product_details)
