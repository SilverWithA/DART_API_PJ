from DartCompanyInfo import Company_info_finder
import pandas as pd
import DartCompanyInfo



comp_finder1 = Company_info_finder()

df = pd.read_excel('2024 88개 대규모기업집단 계열사.xlsx', sheet_name='2024 대규모기업집단 계열사 목록',dtype={"고유번호": str})
res_df = comp_finder1.create_corp_code_col(df,'다트기준 회사명','고유번호','name')

res_df.to_excel('2024 88개 대규모기업집단 계열사(고유성검증 완료).xlsx')


stock_df = comp_finder1.create_stock_code(df, '고유번호','종목코드')

krx_df = pd.read_excel('KRX_20250415_상장 데이터.xlsx', sheet_name="전종목 기본정보", dtype={"단축코드": str})

stock_df.to_excel('krx 종목코드까지 추가.xlsx')


# -------------------------------------------------------------------------------------
# 이름으로 찾기
for country in root.iter("list"):
    if country.findtext("corp_name") == "CJ올리브영":
        print("고유번호: ", country.findtext("corp_code"))
        print("종목코드: ", country.findtext("stock_code"))

# 종목코드로 찾기
for country in root.iter("list"):
    if country.findtext("stock_code") == "046140":
        print("회사명: ", country.findtext("corp_name"))
        print("고유번호: ", country.findtext("corp_code"))


# 고유번호로 찾기
for country in root.iter("list"):
    if country.findtext("stock_code") == "00884545":
        print("회사명: ", country.findtext("corp_name"))
        print("고유번호: ", country.findtext("stock_code"))

