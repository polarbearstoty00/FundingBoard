import streamlit as st
import pandas as pd

def process_repayment_data(df):
    # 새로운 컬럼명 매핑
    column_mapping = {
        '실제 지급일': '지급일',
        '지급원금(원)': '지급원금',
        '지급이자(원)': '지급이자',
        '연체이자(원)': '연체이자',
        '실제 지급금액(원)': '실제지급액',
        '예정지급일': '지급일',
        '예정 지급원금(원)': '지급원금',
        '예정 지급이자(원)': '지급이자'
    }
    
    # 컬럼명 변경
    df = df.rename(columns=column_mapping)
    
    # 필요한 컬럼 생성 및 초기화
    required_columns = ['회차', '지급일', '지급원금', '지급이자', '연체이자', '수수료', '실제지급액']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
            
    # 수수료 컬럼 추가
    df['수수료'] = 0
    
    # 예정 지급건의 실제지급액 계산
    mask = (df['실제지급액'].isna()) & (df['지급원금'].notna()) & (df['지급이자'].notna())
    df.loc[mask, '실제지급액'] = df.loc[mask].apply(
        lambda x: (x['지급원금'] + x['지급이자'] - x['수수료']) 
        if pd.notna(x['지급원금']) and pd.notna(x['지급이자']) 
        else None, 
        axis=1
    )
    
    # 연체이자 0으로 초기화
    df['연체이자'] = df['연체이자'].fillna(0)
    
    # 컬럼 순서 정리
    df = df[required_columns]
    
    return df

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
    # 기존 파일 목록 유지하면서 새 파일 추가
    st.session_state.uploaded_files.extend(uploaded_files)
    
    # 처리 상태 업데이트
    st.session_state.processed_data = True
    
    st.success("데이터 반영이 완료되었습니다!")
    
# 데이터 처리 및 표시
if st.session_state.uploaded_files:
    df1_list = []
    df2_list = []
    
    for file in st.session_state.uploaded_files:
        try:
            xls = pd.ExcelFile(file)

            # 가능한 시트명 목록 정의
            df1_sheets = ['세부 투자내역(투자진행중)', '세부 투자내역(투자종료)', '투자내역']
            df2_sheets = ['세부 투자내역(투자진행중) 회차별 상세정보', '세부 투자내역(투자종료) 회차별 상세정보', '회차별 상세정보']

            # 첫 번째로 존재하는 시트 선택
            sheet_main = next((name for name in df1_sheets if name in xls.sheet_names), None)
            sheet_detail = next((name for name in df2_sheets if name in xls.sheet_names), None)

            if sheet_main and sheet_detail:
                df1 = pd.read_excel(xls, sheet_name=sheet_main)
                df2 = pd.read_excel(xls, sheet_name=sheet_detail)

                # 파일명 추가하여 중복 확인 시 사용
                df1['파일명'] = file.name
                df2['파일명'] = file.name

                df1_list.append(df1)
                df2_list.append(df2)
            else:
                st.warning(f"파일 '{file.name}'에서 적절한 시트를 찾을 수 없음.")

        except Exception as e:
            st.error(f"파일 '{file.name}' 처리 중 오류 발생: {e}")
    
    if df1_list and df2_list:
        # 모든 파일 합치기
        df1_combined = pd.concat(df1_list, ignore_index=True)
        df2_combined = pd.concat(df2_list, ignore_index=True)
        
        # 필요한 모든 컬럼 확인
        required_columns = ['업체명', '상품명']
        additional_columns = ['투자계약일', '상품유형']
        
        # 모든 필요한 컬럼이 존재하는지 확인
        for col in required_columns:
            if col not in df1_combined.columns:
                st.error(f"'{col}' 컬럼이 데이터에 존재하지 않습니다.")
        
        # 업체명과 상품명 기준으로 중복 제거하되, 추가 정보 컬럼도 유지
        display_columns = required_columns.copy()
        display_columns.extend([col for col in additional_columns if col in df1_combined.columns])
        df1_unique = df1_combined[display_columns].drop_duplicates(subset=['업체명', '상품명'])
        
        # 회차별 상세정보에서 업체명, 상품명, 회차번호 기준으로 중복 제거
        if '회차' in df2_combined.columns:
            df2_unique = df2_combined.drop_duplicates(subset=['업체명', '상품명', '회차'])
        else:
            # 회차 컬럼이 없는 경우 모든 컬럼으로 중복 제거
            df2_unique = df2_combined.drop_duplicates()
        
        # 업체명 리스트 생성
        company_list = df1_unique['업체명'].unique()
        
        # 업체 선택 옵션 (라디오 버튼 사용)
        selected_company = st.radio(
            "업체 선택", 
            options=company_list,
            index=0 if len(company_list) > 0 else None,
            key='company_selector',
            horizontal=True  # 수평으로 배치
        )
        
        st.session_state.selected_company = selected_company
        
        if st.session_state.selected_company:
            st.subheader(f"{st.session_state.selected_company} 투자 상품")
            
            # 선택된 업체의 상품 필터링
            df1_selected = df1_unique[df1_unique['업체명'] == st.session_state.selected_company]
            
            for _, row in df1_selected.iterrows():
                product = row['상품명']
                
                # 투자계약일과 상품유형 정보 추가
                display_info = f"{product}"
                
                if '투자계약일' in row and pd.notna(row['투자계약일']):
                    contract_date = row['투자계약일']
                    if isinstance(contract_date, pd.Timestamp):
                        contract_date = contract_date.strftime('%Y-%m-%d')
                    display_info += f" | 계약일: {contract_date}"
                
                if '상품유형' in row and pd.notna(row['상품유형']):
                    display_info += f" | 유형: {row['상품유형']}"
                
                with st.expander(display_info):
                    # 두 번째 시트에서 업체명과 상품명 기준으로 필터링하여 회차 내역 표시
                    df_product_details = df2_unique[
                        (df2_unique['상품명'] == product) & 
                        (df2_unique['업체명'] == st.session_state.selected_company)
                    ]
                    
                    if not df_product_details.empty:
                        # 데이터 처리
                        processed_df = process_repayment_data(df_product_details)
                        
                        # 삭제할 열 목록
                        columns_to_drop = ['투자계약 구분', '투자계약일', '업체명', '상품명', '상품유형', '파일명']
                        
                        # 실제 존재하는 열만 삭제
                        existing_columns_to_drop = [col for col in columns_to_drop if col in df_product_details.columns]
                        
                        # 화면에 표시할 데이터프레임 준비 (필터링된 열만 표시)
                        display_df = df_product_details.drop(columns=existing_columns_to_drop)
                        
                        # '회차' 열을 첫 번째 열로 이동 (있을 경우)
                        if '회차' in display_df.columns:
                            회차_column = display_df['회차']
                            display_df = display_df.drop(columns=['회차'])
                            # 회차 열을 첫 번째로 삽입
                            display_df.insert(0, '회차', 회차_column)
                        
                        # 인덱스 숨기기 (hide_index=True)
                        st.dataframe(display_df, hide_index=True)
                    else:
                        st.info(f"'{product}' 상품의 회차 정보가 없습니다.")
    else:
        st.warning("처리할 데이터가 없습니다. 유효한 엑셀 파일을 업로드하세요.")
else:
    st.info("P2P 투자 내역이 포함된 엑셀 파일을 업로드하세요.")
