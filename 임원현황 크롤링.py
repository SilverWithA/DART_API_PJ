# dart 라이브러리를 이용해서 임원현황 크롤링 요구

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 1. ChromeOptions 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
chrome_options.add_argument("--window-size=1920,3000")
import pandas as pd
import requests
import time

# 500대기업 불러오기
df = pd.read_excel('2025년 500대기업.xlsx', sheet_name='2025년 500대기업',dtype=str)
corp_codes = list(df['기업고유번호'])


# API를 이용하여 임원 현황 불러오기
corp_codes= ["00156017","00104476","00137571","00311030","00426998","00101363","00262196","00104078","00136721"]
def raw_임원현황_api이용코드(corp_codes):
    """기업 고유번호를 기반으로 사업보고서 제출 여부를 확인하는 매서드
    사용한 API 설명 페이지: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001"""

    url = 'https://opendart.fss.or.kr/api/exctvSttus.json'

    # 빈 df 생성(API로 불러와지는 데이터에 맞게 미리 정의 필요)
    res_df = pd.DataFrame(columns=['rcept_no', 'corp_cls', 'corp_code', 'corp_name', 'nm', 'sexdstn',
       'birth_ym', 'ofcps', 'rgist_exctv_at', 'fte_at', 'chrg_job',
       'main_career', 'mxmm_shrholdr_relate', 'hffc_pd', 'tenure_end_on',
       'stlm_dt'])

    total = len(corp_codes)
    for index, corp_code in enumerate(corp_codes):

        print(index, "/", total, "-", round(index / total * 100, 1), "%")
        if corp_code is None or pd.isnull(corp_code):
            continue

        params = {"crtfc_key": api_key,
                "corp_code": str(corp_code).replace(" " , ""),
                "bsns_year": '2025',
                "reprt_code":'11013'    # 1분기 보고서
        }

        res = requests.get(url, params=params) # API 호출
        data = res.json()   # 불러온 json to dictionary 변환
        if data['message'] == '조회된 데이타가 없습니다.': #데이타 ㅎ
            continue
        try:
            new_data = pd.DataFrame(data["list"]) # dictionary to df 변환
            res_df = pd.concat([res_df, new_data], ignore_index=True)
        except Exception as e:
            print("에러 발생: ",e, "에러 발생 구역의 고유번호: ",corp_code)

    print("2025년 1분기 임원현황 불러오기 완료----------------------------------")

    return res_df
raw_res_df = raw_임원현황_api이용코드(corp_codes)
raw_res_df.to_excel('500대기업 1분기 raw 임원(API).xlsx', index=False)


# 웹크롤링을 위해 1분기 보고서 목록 불러오기
# from app.model.Info_collecter import API_info_finder
# finder = API_info_finder()
# report_1Q = finder.공시보고서_접수번호목록_가져오기_디테일버전(corp_codes, '20250101','20250530','A003') # 분기보고서
#
# # 1분기보고서 필터링을 위해 외부 저장
# report_1Q.to_excel('2025 30대그룹 1분기보고서_250530.xlsx', index=False)
# # 필터링완료된 분기보고서 불러오기
report_1Q = pd.read_excel('다양성지수 500대기업 임원.xlsx',sheet_name="1분기보고서",dtype=str)


# 1분기보고서 내 임원 현황 가져오기
def raw_임원현황_크롤링이용코드():

    # rept_no = '20250514000878'       # 단일 접수번호에 대한 테스트용 코드

    # 글로벌 변수 정의
    # raw_tables에 병합을 위한 스키마 지정
    column_names = ['접수번호', '회사명', '테이블순번', 'dummy3', 'dummy4', 'dummy5', 'dummy6', 'dummy7', 'dummy8', 'dummy9'
                                , 'dummy10', 'dummy11', 'dummy12', 'dummy13', 'dummy14', 'dummy15', 'dummy16', 'dummy17'
                                , 'dummy18', 'dummy19','dummy20', 'dummy21', 'dummy22', 'dummy23', 'dummy24']

    a_raw_tables = pd.DataFrame(columns=column_names) # raw 데이터를 담아줄 데이터
    total = len(report_1Q['rcept_no'])              # 크롤링 현황을 알기 위한 전체 1분기보고서 개수
    a_error_list = []                                 # 에러가 발생한 접수번호를 담기위한 리스트

    # 임원 현황 목차 table들 크롤링하는 loops
    for idx, rept_no in enumerate(report_1Q['rcept_no']):

        print(f"{idx}/{total} - (", round(idx / total * 100,1),")%")   # 진행상황 콘솔에 프린트
        corp_name = report_1Q['corp_name'][idx]

        time.sleep(2)
        try:
            driver = webdriver.Chrome(options=chrome_options)   # 백그라운드 실행(크롬 탭 보이지 않음)
            # driver = webdriver.Chrome()                       # 테스트용 코드(크롬 탭 보임)
            driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")   # 접수번호를 이용해 공시 보고서 접속


            # '임원 및 직원'이라는 이름을 가진 목차 선택 및 클릭
            director_section = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(normalize-space(text()), '임원 및 직원')]"))
            )
            director_section[0].click()

            # iframe 속으로 driver 전환
            iframe = driver.find_element(By.ID, "ifrm")
            driver.switch_to.frame(iframe)


            # 임원 및 직원 목차에 존재하는 모든 테이블들 요소
            table_elements = driver.find_elements(By.XPATH, '//table[@border="1"]')
            # table = driver.find_element(By.XPATH, '//table[@border="1"]') # 단일 접수번호에 대한 테스트용 코드

            # 각 테이블 요소 loop
            for i,table in enumerate(table_elements):


                html = table.get_attribute('outerHTML')             # table 요소를 html로 변환
                soup = BeautifulSoup(html, 'html.parser')   # html을 beautifulsoup로 파싱
                rows = soup.find_all('tr')                          # table에 row에 해당하는 tr요소를 모두 불러옴

                tmp = []
                for row in rows:
                    cols = row.find_all(['td', 'th'])

                    # tr에 있는 모든 text 불러서 list로 변환
                    col_list = [col.get_text(strip=True) for col in cols]

                    # 공시보고서 내 정보 외 필수 항목 추가하기
                    col_list.insert(0, i)                # 공시보고서 내 테이블 배치 순서
                    col_list.insert(0, corp_name)        # 회사 이름
                    col_list.insert(0, rept_no)          # 접수번호

                    # raw_tables와 스키마를 맞추기 위한 밑작업
                    # column 개수 맞춰주기
                    if len(col_list) < 25:
                        col_list += [None] * (25 - len(cols)-3)
                    else:
                        col_list = col_list[:25]
                    tmp.append(col_list)


                # tables의 정보를 저장한 tmp 리스트를 df화한 뒤 raw_tables와 row기준으로 병합
                tmp_df = pd.DataFrame(data= tmp, columns=column_names)
                a_raw_tables = pd.concat([a_raw_tables,tmp_df],axis=0)

            driver.quit()
        except:
            a_error_list.append(rept_no)
            continue


    a_raw_tables.to_excel('500대기업 1분기 raw 임원(크롤링).xlsx', index=False)

