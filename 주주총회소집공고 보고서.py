## 일별 주주총회소집공고 보고서 조회
## 📌 주주총회소집결의 수집 가능 여부 테스트 필요
import os


####
# * 진행현황
## (1) 사외이사 = 2025년 3월 10일 이후부터 업데이트 X
## (2) ESG = 2025년 3월 14일이후부터 업데이트 X


#### 1. 주주총회소집공고 불러오기
# 500대 기업 여부 및 88개 대규모기업 집단 계열사에서 발표한 주주총회소집공고 info만 수집
def __call_raw_porxy_info_list__(start_date, end_date):
    """DART에서 공시하는 주주총회소집공고(proxy staement) 리스트를 불러와 반환하는 매서드"""

    url = 'https://opendart.fss.or.kr/api/list.json' # 일자별 특정 보고서 업로드 목록 API

    # 빈 df 생성(API로 불러와지는 데이터에 맞게 미리 정의 필요)
    proxy_info = pd.DataFrame(columns = ['corp_code', 'corp_name', 'stock_code'
                                , 'corp_cls', 'report_nm','rcept_no'
                                , 'flr_nm', 'rcept_dt', 'rm'])

    # 보고서 페이지별로 불러와 쌓아주기(concat 방식)
    page_no = 1
    while True:

        params = {"crtfc_key": api_key,
                  "bgn_de": start_date,
                  "end_de": end_date,
                  "pblntf_detail_ty": 'E006',  # 주주총회소집공고
                  "page_no": page_no,
                  "page_count": '100'
                  }


        res = requests.get(url, params=params) # API 호출
        data = res.json()   # 불러온 json to dictionary 변환

        if data['page_no'] != page_no:
            break

        page_df = pd.DataFrame(data["list"]) # dictionary to df 변환
        proxy_info = pd.concat([proxy_info, page_df], ignore_index=True)
        page_no += 1

    return proxy_info

def __is_vaild__(corp_code, vaild_corp_code_list):
    """매개변수 corp_code가 유효한 corp_code에 해당하는지 확인하여 반환하는 매서드"""
    if corp_code in vaild_corp_code_list:
        return "●"
    else:
        return ""

def __check_vaild_corp__(proxy_info, basic_df,added_col_name):
    """basic_df에는 500대기업, 88개대규모기업 집단 df가 들어와야함"""

    vaild_corp_code_list = list(basic_df['고유번호'])
    proxy_info[added_col_name] =  proxy_info.apply(lambda x: __is_vaild__(x.corp_code, vaild_corp_code_list), axis=1)
    return proxy_info

def porxy_statement_list_KR(start_date, end_date):

    raw_proxy_info = __call_raw_porxy_info_list__(start_date, end_date)

    # 500대기업 불러오기
    com500_df = pd.read_excel('2024년 기준 500대 기업(고유번호 및 종목코드 포함).xlsx',
                        dtype={"순위":int,"종목코드":str,"고유번호":str})

    proxy_info = __check_vaild_corp__(raw_proxy_info, com500_df, '500대기업 여부')

    # 88개 대규모기업집단 계열사 불러오기
    group88_df = pd.read_excel('2024 대규모기업집단 현황(고유번호 및 종목코드 포함).xlsx',
                           dtype={"연번": int,"법인등록번호": str,"고유번호": str,"종목코드": str})

    proxy_info = __check_vaild_corp__(proxy_info,group88_df,'대규모기업집단 여부')


    proxy_info = proxy_info.loc[(proxy_info['500대기업 여부'] != "") | (proxy_info['대규모기업집단 여부'] != ""),]
    return proxy_info

proxy_info = porxy_statement_list_KR(start_date = '20250310',end_date = '20250319')


#### 2. 원본보고서 불러오기
# 2. 보고서 원본 파일 불러오기
def __save_unique_rawDEF14A__(flr_nm, rcept_no):
    """rcept_no:공시보고서에 대한 고유 보고서 코드
    디렉토리 내 공시보고서 원본파일을 저장하는 매서드"""

    # 공시보고서 원본 문서를 불러오는 API(반환 결과 = zip file 포맷의 바이너리 파일(xml))
    url = 'https://opendart.fss.or.kr/api/document.xml'

    # 공시보고서의 고유 접수번호를 input으로 넣어줘야함
    params = {"crtfc_key": api_key, "rcept_no": rcept_no}


    # 파일 저장 경로(디렉토리) 지정
    sub_folder = "./주주총회소집공고보고서"
    doc_zip_path = os.path.abspath(f'./주주총회소집공고보고서/{rcept_no}.zip')
    doc_xml_path =os.path.abspath(f'./주주총회소집공고보고서/{rcept_no}.xml')

    if not os.path.isfile(doc_zip_path) and not os.path.isfile(doc_xml_path):
        res = requests.get(url, params=params)

        with open(doc_zip_path, 'wb') as f: # 바이너리 모드 = wb
            f.write(res.content)
    else:
        print("이미 디렉토리에 저장된 공시문서입니다.")

    with ZipFile(doc_zip_path, 'r') as zf:
        zf.extractall(sub_folder)             # 디렉토리 내 zip 압축 해제

    # 압축 파일 닫기
    zf.close()

    # 디렉토리 내 zip 파일 지우기
    os.remove(doc_zip_path)
    print(flr_nm, "의 주총공고 ", rcept_no,"를 저장했습니다.")



def save_unique_def14a():
    comp500_proxy_info = proxy_info.loc[proxy_info['500대기업 여부'] == "●"]
    group88_proxy_info = proxy_info.loc[proxy_info['대규모기업집단 여부'] == "●"]

    comp500_proxy_info.apply(lambda x: __save_unique_rawDEF14A__(x.flr_nm, x.rcept_no), axis=1)
    group88_proxy_info.apply(lambda x: __save_unique_rawDEF14A__(x.flr_nm, x.rcept_no), axis=1)