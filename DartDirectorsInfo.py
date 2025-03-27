# corp_code = '00126380'  # 삼성전자
# 등기임원 현황 조회 api= https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019010

from library import api_key
import pandas as pd
import requests
import os
from zipfile import ZipFile
from bs4 import BeautifulSoup

df = pd.read_excel('삼성계열사_2024.xlsx',sheet_name='계열사 등기임원 목록',dtype={'고유번호':str})

class DirectorsInfoFinder():
    def __init__(self):
        self.api_key = api_key
        self.filenames = []

    # 등기임원 현황
    def laod_regist_direct(self, df, year):
        url = 'https://opendart.fss.or.kr/api/exctvSttus.json'

        # 빈 df 생성(API로 불러와지는 데이터에 맞게 미리 정의 필요)
        regist_direct_df = pd.DataFrame(columns = ['rcept_no', 'corp_cls', 'corp_code', 'corp_name', 'nm', 'sexdstn',
           'birth_ym', 'ofcps', 'rgist_exctv_at', 'fte_at', 'chrg_job',
           'main_career', 'mxmm_shrholdr_relate', 'hffc_pd', 'tenure_end_on',
           'stlm_dt'])

        for index, corp_code in enumerate(df['고유번호']):
            if corp_code is None or corp_code == '-':
                continue

            params = {
                "crtfc_key": api_key,
                "corp_code": corp_code,
                "bsns_year": year,      # 사업연도
                "reprt_code": '11011'   # 사업보고서
            }

            res = requests.get(url, params=params) # API 호출
            data = res.json()   # 불러온 json to dictionary 변환

            if data['message'] == '조회된 데이타가 없습니다.': #데이타 ㅎ
                continue
            try:
                tmp_df = pd.DataFrame(data["list"]) # dictionary to df 변환
                regist_direct_df = pd.concat([regist_direct_df, tmp_df], ignore_index=True)
            except Exception as e:
                print("에러 발생: ",e, "에러 발생 구역의 고유번호: ",corp_code)

        print("임원정보 불러오기 작업 완료----------------------------------")

        return regist_direct_df

    # 사업보고서 리스트 불러오기
    def __load_report_list__(self,df, start_date, end_date):
        print(" ----------보고서 발표 정보를 불러옵니다.")

        url = 'https://opendart.fss.or.kr/api/list.json'

        # 빈 df 생성(API로 불러와지는 데이터에 맞게 미리 정의 필요)
        report_list = pd.DataFrame(columns=['corp_code', 'corp_name', 'stock_code'
                , 'corp_cls', 'report_nm', 'rcept_no'
                , 'flr_nm', 'rcept_dt', 'rm'])

        for index, corp_code in enumerate(df['고유번호']):
            # print(df['사업보고서 기준 계열사'][index])

            if corp_code is None or corp_code == '-':
                continue

            params = {"crtfc_key": self.api_key,
                      "corp_code": str(corp_code).replace(" ", ""),
                      "bgn_de": start_date,
                      "end_de": end_date,
                      "pblntf_detail_ty": 'A001',
                      "page_no": '1',
                      "page_count": '100'
                      }

            res = requests.get(url, params=params)  # API 호출
            data = res.json()  # 불러온 json to dictionary 변환

            if data['message'] == '조회된 데이타가 없습니다.':
                continue
            try:
                tmp_df = pd.DataFrame(data["list"])  # dictionary to df 변환
                report_list = pd.concat([report_list, tmp_df], ignore_index=True)
            except Exception as e:
                print("에러 발생: ", e, "에러 발생 구역의 고유번호: ", corp_code)


        print("보고서 리스트 불러오기 작업 완료----------------------------------")

        return report_list

    def __save_raw_report__(self,rcept_no):
        url = 'https://opendart.fss.or.kr/api/document.xml'

        # 공시보고서의 고유 접수번호를 input으로 넣어줘야함
        params = {"crtfc_key": api_key, "rcept_no": rcept_no}

        # 파일 저장 경로(디렉토리) 지정
        doc_zip_path = os.path.abspath(f'./{rcept_no}.zip')

        if not os.path.isfile(doc_zip_path):
            res = requests.get(url, params=params)

            with open(doc_zip_path, 'wb') as f:  # 바이너리 모드 = wb
                f.write(res.content)

        zf = ZipFile(doc_zip_path)  # zip 파일열기
        zf.extractall()  # 디렉토리 내 zip 압축 해제

        # 파일 이름 불러오기
        zipinfo = zf.infolist()
        self.filenames.append([x.filename for x in zipinfo][0])

        # 압축 파일 닫기
        zf.close()

        # 디렉토리 내 zip 파일 지우기
        os.remove(doc_zip_path)
        print(rcept_no, " 원본 보고서가 디렉토리에 저장 완료되었습니다.")

    def __read_statement_report__(self, filename):
        # 디렉토리 내 파일 불러오기
        with open(filename, "r", encoding="utf-8") as file:
            xml_content = file.read()

        # BeautifulSoup으로 XML 파싱
        soup = BeautifulSoup(xml_content, 'xml')

        # 미등기 임원
        target_title = None
        for title in soup.find_all("TITLE"):
            if '미등기' in title.text:
                target_title = title
                break  # 첫 번째로 찾은 것을 사용

        # 제목 바로 아래에 있는 table
        target_table = None
        if target_title:
            next_sibling = target_title.find_next_sibling("TABLE")
            if next_sibling:
                target_table = next_sibling

        # 테이블이 존재할 때만 변환
        if target_table:
            rows = target_table.find_all("TR")  # 모든 <TR> 태그 찾기
            table_data = [[col.get_text(strip=True) for col in row.find_all(["TH", "TD"])] for row in rows]

            # Pandas DataFrame 생성
            df = pd.DataFrame(table_data)

            # 출력
            print(df)

    # 미등기임원 불러오기(TEST)
    def laod_unregist_direct(self, df,start_date,end_date):

        # 보고서 목록 불러오기
        report_list = self.__load_report_list__(df,start_date,end_date)

        # 원본 보고서 디렉토리에 저장하기
        for recpt_no in report_list['rcept_no']:
            self.__save_raw_report__(recpt_no)

        # xml파일 보고서 불러와서 분석하기



# 삼성전자 미등기임원 불러오기 실습
direct_finder1 = DirectorsInfoFinder()
report_list = direct_finder1.__load_report_list__(df, '20160101','20250327')
report_list.to_excel('(2015-2024) 삼성계열사 사업보고서 제출 리스트.xlsx')

# 삼성전자 사업보고서(2015-2024)
test_df = report_list[report_list['corp_name'] =='삼성전자']


for rcept_no in test_df['rcept_no']:
    direct_finder1.__save_raw_report__(rcept_no)

print(direct_finder1.filenames)

filename = direct_finder1.filenames[0]