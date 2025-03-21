import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="P2P 투자 관리", layout="wide")

st.title('엑셀 파일 병합')

# 업로드된 파일을 저장할 세션 상태 초기화
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None

# 파일 업로드 기능 (여러 개 가능)
uploaded_files = st.file_uploader("엑셀 파일 업로드", type=["xls", "xlsx"], accept_multiple_files=True)

# 실행 버튼
run_button = st.button("실행")

# 파일이 업로드되고 실행 버튼이 눌렸을 때만 처리
if run_button and uploaded_files:
    st.session_state.uploaded_files.extend(uploaded_files)
    st.success("데이터 반영이 완료되었습니다!")
    
# 데이터 처리 및 표시
if st.session_state.uploaded_files:
    df_list = []
    
    for file in st.session_state.uploaded_files:
        try:
            xls = pd.ExcelFile(file)
            sheet_main = next((name for name in xls.sheet_names if "투자내역" in name), None)
            sheet_detail = next((name for name in xls.sheet_names if "회차별 상세정보" in name), None)
            
            if sheet_main and sheet_detail:
                df_main = pd.read_excel(xls, sheet_name=sheet_main)
                df_detail = pd.read_excel(xls, sheet_name=sheet_detail)
                df_main['파일명'] = file.name
                df_detail['파일명'] = file.name
                df_list.append((df_main, df_detail))
            else:
                st.warning(f"파일 '{file.name}'에서 적절한 시트를 찾을 수 없음.")
        except Exception as e:
            st.error(f"파일 '{file.name}' 처리 중 오류 발생: {e}")
    
    if df_list:
        excel_data = BytesIO()
        writer = pd.ExcelWriter(excel_data, engine='xlsxwriter')
        
        for df_main, df_detail in df_list:
            if '업체명' in df_main.columns:
                for company in df_main['업체명'].unique():
                    df_company = df_main[df_main['업체명'] == company]
                    
                    # 업체별 시트 구성 데이터
                    sheet_data = []
                    for _, row in df_company.iterrows():
                        product = row['상품명']
                        contract_date = row.get('투자계약일', '')
                        product_type = row.get('상품유형', '')
                        
                        sheet_data.append(pd.DataFrame({
                            '상품명': [product],
                            '투자계약일': [contract_date],
                            '상품유형': [product_type]
                        }))
                        
                        df_product_detail = df_detail[(df_detail['업체명'] == company) & (df_detail['상품명'] == product)]
                        sheet_data.append(df_product_detail[['회차', '지급일', '지급원금', '지급이자', '연체이자', '수수료(0)', '실제지급액']])
                        
                    final_df = pd.concat(sheet_data, ignore_index=True)
                    final_df.to_excel(writer, sheet_name=company[:31], index=False)
        
        writer.close()
        excel_data.seek(0)
        st.download_button("엑셀 저장", data=excel_data, file_name="P2P_투자내역.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.warning("처리할 데이터가 없습니다. 유효한 엑셀 파일을 업로드하세요.")
else:
    st.info("P2P 투자 내역이 포함된 엑셀 파일을 업로드하세요.")
