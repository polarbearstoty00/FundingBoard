import streamlit as st
import pandas as pd

# 업로드된 파일을 저장할 세션 상태 초기화
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

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
        
        # 데이터 전처리 및 병합
        merged_df = df1.merge(df2, on=['투자계약 구분', '투자계약일', '업체명', '상품명', '상품유형'], how='left')
        all_data.append(merged_df)
    
    final_df = pd.concat(all_data, ignore_index=True)
    
    # 업체명 기준 그룹화
    grouped = final_df.groupby('업체명')
    
    for name, group in grouped:
        with st.expander(name):
            st.write(group)

# 닫기 버튼 (파일 유지)
if st.button("닫기"):
    st.success("파일 목록은 유지됩니다.")
