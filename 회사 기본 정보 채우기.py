from DartCompanyInfo import Company_info_finder
import pandas as pd

comp_finder1 = Company_info_finder()
df = pd.read_excel('2024 88개 대규모기업집단 계열사.xlsx', sheet_name='2024 대규모기업집단 계열사')


df = comp_finder1.create_corp_code_col(df,'다트기준 회사명','고유번호')

df.to_excel('test.xlsx')
# 고유번호 중복회사 필터링하는 파이썬 매서드 필요함