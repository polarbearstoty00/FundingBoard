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

# 데이터 처리 및 표시
if st.session_state.uploaded_files:
    df1_list = []
    df2_list = []
    
    for file in st.session_state.uploaded_files:
        try:
            xls = pd.ExcelFile(file)
            df1_sheets = ['세부 투자내역(투자진행중)', '세부 투자내역(투자종료)', '투자내역']
            df2_sheets = ['세부 투자내역(투자진행중) 회차별 상세정보', '세부 투자내역(투자종료) 회차별 상세정보', '회차별 상세정보']

            sheet_main = next((name for name in df1_sheets if name in xls.sheet_names), None)
            sheet_detail = next((name for name in df2_sheets if name in xls.sheet_names), None)

            if sheet_main and sheet_detail:
                df1 = pd.read_excel(xls, sheet_name=sheet_main)
                df2 = pd.read_excel(xls, sheet_name=sheet_detail)
                df1['파일명'] = file.name
                df2['파일명'] = file.name
                df1_list.append(df1)
                df2_list.append(df2)
            else:
                st.warning(f"파일 '{file.name}'에서 적절한 시트를 찾을 수 없음.")

        except Exception as e:
            st.error(f"파일 '{file.name}' 처리 중 오류 발생: {e}")
    
    if df1_list and df2_list:
        df1_combined = pd.concat(df1_list, ignore_index=True)
        df2_combined = pd.concat(df2_list, ignore_index=True)
        required_columns = ['업체명', '상품명']
        additional_columns = ['투자계약일', '상품유형']

        for col in required_columns:
            if col not in df1_combined.columns:
                st.error(f"'{col}' 컬럼이 데이터에 존재하지 않습니다.")
        
        display_columns = required_columns.copy()
        display_columns.extend([col for col in additional_columns if col in df1_combined.columns])
        df1_unique = df1_combined[display_columns].drop_duplicates(subset=['업체명', '상품명'])

        if '회차' in df2_combined.columns:
            df2_unique = df2_combined.drop_duplicates(subset=['업체명', '상품명', '회차'])
        else:
            df2_unique = df2_combined.drop_duplicates()
        
        company_list = df1_unique['업체명'].unique()
        selected_company = st.radio("업체 선택", options=company_list, index=0 if len(company_list) > 0 else None, key='company_selector', horizontal=True)
        st.session_state.selected_company = selected_company
        
        if st.session_state.selected_company:
            st.subheader(f"{st.session_state.selected_company} 투자 상품")
            df1_selected = df1_unique[df1_unique['업체명'] == st.session_state.selected_company]
            
            excel_data = BytesIO()
            writer = pd.ExcelWriter(excel_data, engine='xlsxwriter')
            
            for _, row in df1_selected.iterrows():
                product = row['상품명']
                display_info = f"{product}"
                
                if '투자계약일' in row and pd.notna(row['투자계약일']):
                    contract_date = row['투자계약일']
                    if isinstance(contract_date, pd.Timestamp):
                        contract_date = contract_date.strftime('%Y-%m-%d')
                    display_info += f" | 계약일: {contract_date}"
                
                if '상품유형' in row and pd.notna(row['상품유형']):
                    display_info += f" | 유형: {row['상품유형']}"
                
                with st.expander(display_info):
                    df_product_details = df2_unique[(df2_unique['상품명'] == product) & (df2_unique['업체명'] == st.session_state.selected_company)]
                    if not df_product_details.empty:
                        # 필요한 컬럼만 유지
                        required_columns = ['회차', '지급일', '지급원금', '지급이자', '연체이자', '수수료', '실제지급액']
                        
                        # '수수료' 컬럼이 없으면 기본값 0으로 추가
                        if '수수료' not in df_product_details.columns:
                            df_product_details['수수료'] = 0
                        
                        existing_required_columns = [col for col in required_columns if col in df_product_details.columns]
                        display_df = df_product_details[existing_required_columns]

                        st.dataframe(display_df, hide_index=True)
                        display_df.to_excel(writer, sheet_name=product, index=False)
            writer.close()
            excel_data.seek(0)
            st.download_button("엑셀 저장", data=excel_data, file_name=f"{st.session_state.selected_company}_투자내역.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.warning("처리할 데이터가 없습니다. 유효한 엑셀 파일을 업로드하세요.")
else:
    st.info("P2P 투자 내역이 포함된 엑셀 파일을 업로드하세요.")
