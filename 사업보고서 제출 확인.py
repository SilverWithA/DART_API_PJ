

### 1. 데이터 불러오기
# 30대그룹 데이터 불러오기(불러오기 전 컬럼 별 타입 지정 필요)
group30_df = pd.read_excel('2024 대규모기업집단 현황(고유번호 및 종목코드 포함).xlsx',
                           dtype={
                               "연번": int,
                               "법인등록번호": str,
                               "고유번호": str
                               ,"종목코드": str})


# 500대기업 데이터 불러오기(고유번호 등 컬럼 문자형으로 지정해주기)
com500_df = pd.read_excel('2024년 기준 500대 기업(고유번호 및 종목코드 포함).xlsx',
                        dtype={"순위":int,
                               "종목코드":str,
                               "고유번호":str})


# 2024년기준 사업보고서 제출 여부 확인 ---------------------------

# 제출한 공시 보고서 조회하는 매서드
def collect_anuual_report_list(df):
    """기업 고유번호를 기반으로 사업보고서 제출 여부를 확인하는 매서드
    사용한 API 설명 페이지: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001"""

    url = 'https://opendart.fss.or.kr/api/list.json'

    # 빈 df 생성(API로 불러와지는 데이터에 맞게 미리 정의 필요)
    res_df = pd.DataFrame(columns = ['corp_code', 'corp_name', 'stock_code'
                                , 'corp_cls', 'report_nm','rcept_no'
                                , 'flr_nm', 'rcept_dt', 'rm'])

    for index, corp_code in enumerate(df['고유번호']):
        if corp_code is None:
            continue

        params = {"crtfc_key": api_key,
            "corp_code": str(corp_code),
            "bgn_de":   '20240101',
            "end_de":'20250304',
            "last_reprt_at": 'Y',
            "pblntf_ty": 'A',   #정기보고서만 조회하기
            "corp_cls": 'Y',
            "page_no": '1',
            "page_count": '100'
        }

        res = requests.get(url, params=params) # API 호출
        data = res.json()   # 불러온 json to dictionary 변환

        if data['message'] == '조회된 데이타가 없습니다.': #데이타 ㅎ
            continue

        new_data = pd.DataFrame(data["list"]) # dictionary to df 변환

        # 계속 df에 새로 불러온 정보를 불러와서 concat해주며 데이터 추가
        res_df = pd.concat([res_df,new_data], ignore_index=True)
    print("정기 보고서 불러오기 작업 완료----------------------------------")

    return res_df

# 500대 기업 사업보고서 제출 기업 찾기
res.df = collect_anuual_report_list(com500_df)
res_df.to_excel('2024년 500대그룹 및 계열사 정기보고서.xlsx')    # 중간 저장

# 사업보고서 필터링
    # 불필요한 문자 제거 (정규식 사용)
        # 1. 대괄호로 묶인 문자열 제거 ex) [기재정정], [첨부정정] => \[.*?\]
        # 2. 괄호로 묶인 문자열 제거 ex) (2024.09) => \(.*?\)

res_df["report_nm"] = res_df["report_nm"].str.replace(r"\[.*?\]|\(.*?\)", "", regex=True).str.strip()


# 사업보고서 항목만 남기기
res_df = res_df[res_df["report_nm"] == "사업보고서"]

# 중복행 삭제
# res_df = res_df.drop_duplicates(subset=["corp_name","report_nm","rcept_dt"])


com500_df['사업보고서 제출 여부'] = com500_df['고유번호'].apply(is_company_anuual_repot)
# com500_df = com500_df.drop("사업보고서 제출 여부", axis=1)

def is_company_anuual_repot(corp_code):
    if str(corp_code) in res_df["corp_code"].unique():
        return "●"
    else:
        return "-"
com500_df.to_excel('2024년 기준 500대 기업(고유번호 및 종목코드, 사업보고서 제출 여부 포함).xlsx.xlsx')
res_df.to_excel('2024년 500대그룹 및 계열사 사업보고서.xlsx')