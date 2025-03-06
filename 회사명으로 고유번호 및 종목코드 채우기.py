import requests

from library import root
import library

############ api_key 및 root 글로벌 변수 정의 전제 ############


# 회사으로 고유번호 찾기
def find_corp_num(find_name):
    """회사명으로 고유번호 찾기
        find_name = 고유번호를 찾고자하는 회사명
        기업개황 정보가 담긴 root가 글로벌로 정의되어 있어야함"""
    for country in root.iter("list"):
        if country.findtext("corp_name") == find_name:
            return country.findtext("corp_code")

# 고유코드로 종목 코드 찾기
def find_stock_code(df):
        """회사 고유번호로 종목코드 찾기"""

        url = f'https://opendart.fss.or.kr/api/company.json'

        for index, corp_code in enumerate(df['고유번호']):
            if not corp_code:
                continue

            params = {
                "crtfc_key": str(api_key),
                "corp_code": str(corp_code)
            }
            res = requests.get(url, params= params)
            data = res.json()

            if data['message'] != '정상':
                continue
            else:
                df['종목코드'][index] = data['stock_code']


# 회사명으로 종목 코드 찾기
# def find_stock_code(find_name):
#         """회사명으로 종목코드 찾기"""
#
#         for country in root.iter("list"):
#             if country.findtext("corp_name") == find_name:
#                 return country.findtext("stock_code")


# KRX 데이터로 빠진 종목 코드 보충하기
def supplement_stock_code(df,stock_code_col,corp_name_col):

    krx_df = pd.read_excel('20250228_주가.xlsx')

    for idx, stock_code in enumerate(df[stock_code_col]):
        if stock_code == ' ':
            company_name = df[corp_name_col][idx]

            for idx, krx_name in enumerate(krx_df['종목명']):
                if krx_name == company_name:
                    df[stock_code_col][idx] = krx_df['종목코드'][idx]
                    continue

    # api 호출
    # 호출한 api에서 종목 이름만 추출


# 매서드 사용 예시
def make_holdings_list():
    """대기업집단의 지주 및 지주격 회사의 고유번호와 종목코드를 추가한 xlsx파일을 디렉토리에 저장합니다"""

    # 사명이 담긴 데이터 불러오기
    df = pd.read_csv('대기업집단 지주 및 지주격 회사 리스트.csv')

    # 매서드 적용
    df['고유번호'] = df['기업명'].apply(find_corp_num)
    df['종목코드'] = None  # 빈 컬럼 생성

    find_stock_code(df)
    # df['종목코드'] = df['기업명'].apply(find_stock_code)

    # 종목코드 보충하기
    supplement_stock_code(df,'종목코드','기업명')

    # xlsx 파일로 저장(csv로 저장시 숫자형 데이터로 자동변환 문제 有)
    df.to_excel('대기업집단 지주 및 지주격 회사 리스트 (고유번호 및 종목코드 포함).xlsx', index=False)

# 실행 코드
make_holdings_list()