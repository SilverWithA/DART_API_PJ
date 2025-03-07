import library

############ (주의) 보안상의 이유로 api키는 매서드 내 직접 정의하지 않음 유의(글로벌에 미리 정의해두고 매서드를 사용할 것)####################
# 회사명으로 고유번호를 찾는 매서드
def find_corp_num(find_name):
    """회사명으로 고유번호 찾기
        find_name = 고유번호를 찾고자하는 회사명"""

    for country in root.iter("list"):
        if country.findtext("corp_name") == find_name:
            return country.findtext("corp_code")

# 고유코드로 종목 코드 찾는 매서드
def find_stock_code(corp_code):
        """회사 고유번호로 종목코드 찾기
        corp_code = df내 고유번호가 정의된 컬럼명"""

        # 종목코드를 불러와 저장해줄 컬럼 사전 정의
        # df['종목코드'] = None

        # API 호출 url 정의
        url = f'https://opendart.fss.or.kr/api/company.json'

        if not corp_code:
            return None

        params = {
            "crtfc_key": str(api_key),  # 호출을 위한 API키
            "corp_code": str(corp_code) # 고유번호
        }

        # API호출
        res = requests.get(url, params= params)
        data = res.json()   #json 형식으로 파싱

        # 호출이 정상적으로 불러와졌을 때만 종목코드 추가 및 수정
        if data['message'] != '정상':
            return "API 호출 오류"

        # Dart 데이터베이스 내 종목코드가 정의된 것이 없다면 패스
        if len(data['stock_code']) == 0:
            return None
        else:
            return data['stock_code']

# KRX 데이터로 빠진 종목 코드 보충하는 매서드
def supplement_stock_code(df,stock_code_col,krx_corp_name_col):
    """KRX 전종목 기본정보를 기준으로 종목코드를 추가 및 보충하는 매서드
    실행 전 krx_df내 컬럼 명을 확인할 것, 매서드 수정이 필요할 수 있음"""

    for i, company_name in enumerate(df[krx_corp_name_col]):
        for idx, krx_name in enumerate(krx_df['한글 종목약명']):
            if krx_name == company_name:
                df[str(stock_code_col)][i] = krx_df['단축코드'][idx]
                continue


# 매핑이 되지 않은 빈 row를 확인하는 매서드
def count_none_mapping_rows(df, check_col_name, corp_name):
    """위 매서드 사용 후 매핑되지 않은 빈 컬럼 확인시 사용할 수 있는 매서드
        check_col_name: 매핑여부를 확인할 컬럼 이름
        corp_name: 회사명이 정의된 컬럼 이름"""

    missing_corpcode_list = []
    for index, data in enumerate(df[str(check_col_name)]):

        # 매핑이 되지 않은 경우
        if data is None or len(data) == 0:
            missing_corpcode_list.append(df[str(corp_name)][index])

    print("전체 계열사 개수: ", len(df[str(corp_name)]))
    print("매핑 안된 계열사 수: ",len(missing_corpcode_list))
    print("매핑 안된 계열사: ", missing_corpcode_list)




##### 매서드 사용 예시: 88개 대규모 기업집단의 지주 및 지주격 회사 ########
# 작업 설명: 대기업집단의 지주 및 지주격 회사의 고유번호와 종목코드를 추가한 xlsx파일을 디렉토리에 저장합니다"""

# 0. 라이브러리 및 매서드, api키 미리 불러오기
# 1. 데이터 불러오기
df = pd.read_csv('대기업집단 지주 및 지주격 회사 리스트.csv')

# 2. 사명으로 고유번호 찾기
df['고유번호'] = df['기업명'].apply(find_corp_num)

# 고유번호로
find_stock_code(df)
# df['종목코드'] = df['기업명'].apply(find_stock_code)
# 종목코드 보충하기
supplement_stock_code(df,'종목코드','기업명')
# xlsx 파일로 저장(csv로 저장시 숫자형 데이터로 자동변환 문제 有)
df.to_excel('대기업집단 지주 및 지주격 회사 리스트 (고유번호 및 종목코드 포함).xlsx', index=False)

# 실행 코드
make_holdings_list()