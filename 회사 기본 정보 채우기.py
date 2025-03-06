from DartCompanyInfo import Company_info_finder
import pandas as pd


comp_finder1 = Company_info_finder()

df = pd.read_excel('2024 88개 대규모기업집단 계열사_20250421 (2).xlsx', sheet_name='30대그룹 계열사 최종',dtype={'고유번호':str,'종목코드':str,'법인등록번호':str})

df = comp_finder1.create_stock_code(df, '고유번호', '다트기준회사명', '종목코드')

df.to_excel('종목코드까지 채움.xlsx', index=False)

# -------------------------------------------------------------------------------------



# 대량으로 찾기
def 이름으로_고유번호_찾기(corp_name):
    for country in root.iter("list"):
        if country.findtext("corp_name") == corp_name:
            return country.findtext("corp_code")


def 이름으로_종목코드_찾기(corp_name):
    for country in root.iter("list"):
        if country.findtext("corp_name") == corp_name:
            return country.findtext("stock_code")


def 종목코드로_고유번호_찾기(stock_code):
    for country in root.iter("list"):
        if country.findtext("stock_code") == stock_code:
            return country.findtext("corp_code")

df['종목코드_by이름'] = df['회사명'].apply(이름으로_종목코드_찾기)
df['고유번호'] = df['회사명'].apply(이름으로_고유번호_찾기)

df.to_excel('2023 500대.xlsx', index=False)


# 이름으로 찾기
for country in root.iter("list"):
    if country.findtext("corp_name") == "미래에셋파트너스제11호사모투자":
        print("고유번호: ", country.findtext("corp_code"))
        print("종목코드: ", country.findtext("stock_code"))

# 종목코드로 찾기
for country in root.iter("list"):
    if country.findtext("stock_code") == "010060":
        print("회사명: ", country.findtext("corp_name"))
        print("고유번호: ", country.findtext("corp_code"))


# 고유번호로 찾기
for country in root.iter("list"):
    if country.findtext("corp_code") == "01783207":
        print("회사명: ", country.findtext("corp_name"))
        print("종목코드: ", country.findtext("stock_code"))

