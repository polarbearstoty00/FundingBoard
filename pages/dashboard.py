import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="P2P 투자 관리", layout="wide")

st.title('엑셀 파일 병합')

# 업로드된 파일을 저장할 세션 상태 초기화
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = {}
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = False

# 파일 업로드 기능 (여러 개 가능)
uploaded_files = st.file_uploader("엑셀 파일 업로드", type=["xls", "xlsx"], accept_multiple_files=True)

# 실행 버튼
run_button = st.button("실행")

# 파일이 업로드되고 실행 버튼이 눌렸을 때만 처리
if run_button and uploaded_files:
    st.session_state.uploaded_files.extend(uploaded_files)
    st.session_state.processed_data = True
    st.success("데이터 반영이 완료되었습니다!")

# 데이터 처리 및 저장 기능
if st.session_state.uploaded_files:
    df_list = []
    
    for file in st.session_state.uploaded_files:
        try:
            xls = pd.ExcelFile(file)
            sheet_detail = next((name for name in xls.sheet_names if '회차별 상세정보' in name), None)
            
            if sheet_detail:
                df = pd.read_excel(xls, sheet_name=sheet_detail)
                df['파일명'] = file.name
                df_list.append(df)
            else:
                st.warning(f"파일 '{file.name}'에서 적절한 시트를 찾을 수 없음.")
        except Exception as e:
            st.error(f"파일 '{file.name}' 처리 중 오류 발생: {e}")
    
    if df_list:
        df_combined = pd.concat(df_list, ignore_index=True)
        df_combined = df_combined.rename(columns={
            '예정 지급일': '지급일',
            '실제 지급일': '지급일',
            '예정 지급원금(단위 : 원)': '지급원금',
            '예정 지급이자(단위 : 원)': '지급이자',
            '지급원금(단위 : 원)': '지급원금',
            '지급이자(단위 : 원)': '지급이자',
            '연체이자(단위 : 원)': '연체이자',
            '실제 지급금액(단위 : 원)': '실제지급액'
        })
        df_combined['수수료'] = 0
        df_combined = df_combined[['업체명', '상품명', '회차', '지급일', '지급원금', '지급이자', '연체이자', '수수료', '실제지급액']]
        
        excel_data = BytesIO()
        writer = pd.ExcelWriter(excel_data, engine='xlsxwriter')
        
        for company in df_combined['업체명'].unique():
            df_company = df_combined[df_combined['업체명'] == company]
            df_company.to_excel(writer, sheet_name=company, index=False)
        
        df_combined.to_excel(writer, sheet_name="전체 데이터", index=False)
        writer.close()
        excel_data.seek(0)
        
        st.download_button("엑셀 저장", data=excel_data, file_name="P2P_투자내역.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.warning("처리할 데이터가 없습니다. 유효한 엑셀 파일을 업로드하세요.")
else:
    st.info("투자 내역이 있는 엑셀 파일을 업로드하세요.")
