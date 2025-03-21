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
    # 새로 업로드된 파일만 추가
    st.session_state.uploaded_files.extend([file for file in uploaded_files 
                                           if file.name not in [existing.name for existing in st.session_state.uploaded_files]])

# 데이터 처리 및 표시
if st.session_state.uploaded_files:
    df1_list = []
    df2_list = []
    
    for file in st.session_state.uploaded_files:
        try:
            xls = pd.ExcelFile(file)
            df1 = pd.read_excel(xls, sheet_name='세부 투자내역(투자진행중)')
            df2 = pd.read_excel(xls, sheet_name='세부 투자내역(투자진행중) 회차별 상세정보')
            
            # 각 데이터프레임에 고유 식별자를 추가하여 나중에 중복 확인 시 사용
            df1['파일명'] = file.name
            df2['파일명'] = file.name
            
            df1_list.append(df1)
            df2_list.append(df2)
        except Exception as e:
            st.error(f"파일 '{file.name}' 처리 중 오류 발생: {e}")
    
    if df1_list and df2_list:
        # 모든 파일 합치기
        df1_combined = pd.concat(df1_list, ignore_index=True)
        df2_combined = pd.concat(df2_list, ignore_index=True)
        
        # 업체명, 상품명, 회차번호를 기준으로 중복 제거
        # 기존 세부 투자내역 시트에서 업체명과 상품명 기준으로 중복 제거
        df1_unique = df1_combined[['업체명', '상품명']].drop_duplicates()
        
        # 회차별 상세정보에서 업체명, 상품명, 회차번호 기준으로 중복 제거
        if '회차' in df2_combined.columns:
            df2_unique = df2_combined.drop_duplicates(subset=['업체명', '상품명', '회차'])
        else:
            # 회차 컬럼이 없는 경우 모든 컬럼으로 중복 제거
            df2_unique = df2_combined.drop_duplicates()
        
        # 업체명 리스트 생성
        company_list = df1_unique['업체명'].unique()
        
        # 업체 선택 옵션
        selected_company = st.radio(
            "업체 선택", 
            options=company_list,
            index=0 if company_list.size > 0 else None,
            key='company_selector'
        )
        
        st.session_state.selected_company = selected_company
        
        if st.session_state.selected_company:
            st.subheader(f"{st.session_state.selected_company} 투자 상품")
            
            # 선택된 업체의 상품 필터링
            df1_selected = df1_unique[df1_unique['업체명'] == st.session_state.selected_company]
            
            for product in df1_selected['상품명'].unique():
                with st.expander(product):
                    # 두 번째 시트에서 업체명과 상품명 기준으로 필터링하여 회차 내역 표시
                    df_product_details = df2_unique[
                        (df2_unique['상품명'] == product) & 
                        (df2_unique['업체명'] == st.session_state.selected_company)
                    ]
                    
                    if not df_product_details.empty:
                        st.dataframe(df_product_details)
                    else:
                        st.info(f"'{product}' 상품의 회차 정보가 없습니다.")
    else:
        st.warning("처리할 데이터가 없습니다. 유효한 엑셀 파일을 업로드하세요.")
else:
    st.info("P2P 투자 내역이 포함된 엑셀 파일을 업로드하세요.")
