import pandas as pd
import copy

# 데이터 불러오기
df = pd.read_excel('2024 대규모기업집단 현황.xlsx',sheet_name='2024 대규모기업집단 계열사')
# KRX 전종목 기본정보 로드(디렉토리에 미리 저장 필요)
krx_df = pd.read_excel('KRX  전종목 기본정보_20250306.xlsx',sheet_name='Sheet1')

# 다트기준 회사명으로 고유번호 서치
df['고유번호'] = df['다트기준 회사명'].apply(find_corp_num)
df = df.explode('고유번호').reset_index(drop=True) # 리스트 값을 행으로 확장


# 고유번호로 종목코드 서치(다트기준 종목코드)
df['종목코드'] = df['고유번호'].apply(find_stock_code)

temp_df = copy.deepcopy(df) # 임시저장
count_none_mapping_rows(df,'종목코드','회사명') # 2935개

# KRX 기준으로 종목코드 보충(KRX기준 종목코드로 통일)
supplement_stock_code(df,'종목코드','KRX기준 회사명')
count_none_mapping_rows(df,'종목코드','회사명') # 3222개


# 데이터 내보내기
df.to_excel('2024 대규모기업집단 현황(고유번호 및 종목코드 포함).xlsx', index=False)

