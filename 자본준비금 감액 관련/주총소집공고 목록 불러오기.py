# 테스트 페이지
import pandas as pd
import requests

df = pd.read_excel('상장사 감액배당 실태조사_20250428_v1.xlsx', sheet_name='상장사 정보',dtype=str)

import xml.etree.ElementTree as ET
xml_file = "CORPCODE.xml"  # 파일 경로를 지정하세요
tree = ET.parse(xml_file)
root = tree.getroot()

def __fill_corp_code_by_stock__( find_stock):
    """종목코드로 고유번호 찾는 매서드
        * find_stcok = 고유번호를 찾고자하는 회사의 종목코드"""

    cnt = 0
    corp_code_list = []

    for country in root.iter("list"):
        if country.findtext("stock_code") == find_stock:
            cnt += 1
            corp_code_list.append(country.findtext("corp_code"))

    if cnt > 1:

        return corp_code_list

    elif cnt == 1:
        return corp_code_list[0]
df['고유번호'] = df['종목코드'].apply(__fill_corp_code_by_stock__)

def collect_report_list(df):
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
                "corp_code": str(corp_code).replace(" " , ""),
                "bgn_de":   '20220101',
                "end_de":'20221231',
                "last_reprt_at":"Y",
                "pblntf_detail_ty": 'E006',   #사업보고서만 조회 # https://dart-fss.readthedocs.io/en/latest/dart_types.html
                "page_no": '1',
                "page_count": '100'
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

        # print(res_df)

    print("주주총회 소집 공고 공시 목록 불러오기 작업 완료----------------------------------")

    return res_df

E006_2022df = collect_report_list(df)
E006_2022df.to_excel('2022년 상장사 주총공고.xlsx', index= False)