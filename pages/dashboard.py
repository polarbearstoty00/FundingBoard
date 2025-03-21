import streamlit as st
import pandas as pd

# 파일 업로드
def load_excel():
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xls", "xlsx"])
    if uploaded_file:
        xls = pd.ExcelFile(uploaded_file)
        df1 = pd.read_excel(xls, sheet_name='세부 투자내역(투자진행중)')
        df2 = pd.read_excel(xls, sheet_name='세부 투자내역(투자진행중) 회차별 상세정보')
        return df1, df2
    return None, None

# 데이터 병합 함수
def merge_data(df1, df2):
    key_cols = ['투자계약 구분', '투자계약일', '업체명', '상품명', '상품유형']
    merged_df = df1.merge(df2, on=key_cols, how='left')
    return merged_df

# 메인 실행 코드
st.title("P2P 투자 내역 분석 대시보드")

# 엑셀 데이터 로드
df1, df2 = load_excel()

if df1 is not None and df2 is not None:
    merged_df = merge_data(df1, df2)
    st.write("### 병합된 투자 데이터")
    st.dataframe(merged_df)
