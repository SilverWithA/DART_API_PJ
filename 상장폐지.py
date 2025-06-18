import pandas as pd
from app.model.Info_collecter import API_info_finder
finder = API_info_finder()
import pandas as pd
from app.view.Info_UI import Info_view
import config
from urllib.request import urlopen
from zipfile import ZipFile
import io
import os
import requests
from sqlalchemy import create_engine
from pandas import isnull


api_key = '2ae5aede864cda8f26e03f216d7662056b0944d2'
api_key = '603f5dd4ebc7e868fc411b673caa69783b5d6b63'


# "I003": "시장조치/안내"
# 3개월치씩 확인


def 공시보고서_접수번호목록_가져오기_디테일_no고유번호(start_date, end_date, pblntf_detail_ty):
    """(기간은 3개월 미만으로 지정해야함 주의)
    고유번호 없이 공시보고서 리스트를 반환하는 매서드"""

    res_df = pd.DataFrame(
        columns=['corp_code', 'corp_name', 'stock_code', 'corp_cls', 'report_nm', 'rcept_no', 'flr_nm', 'rcept_dt',
                 'rm'])

    url = "https://opendart.fss.or.kr/api/list.json"

    page_no = 0
    while True:
        page_no += 1
        params = {"crtfc_key": api_key,
                  "bgn_de": str(start_date),
                  "end_de": str(end_date),
                  "last_reprt_at": 'Y',
                  "pblntf_detail_ty": str(pblntf_detail_ty),
                  "page_no": str(page_no),
                  "page_count": '100'}
        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data['message'] == '조회된 데이타가 없습니다.':
                continue
            if data['message'] == "corp_code가 없는 경우 검색기간은 3개월만 가능합니다.":
                break
            elif str(data['page_no']) != str(page_no):
                break
            elif data['message'] == "사용한도를 초과하였습니다.":
                break
            elif data['list']:
                tmp_df = pd.DataFrame(data['list'])
                res_df = pd.concat([res_df, tmp_df])
        except Exception as e:
            pass

    return res_df


# "I003": "시장조치/안내"
# 3개월치씩 확인
# 2025년
report_df= 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20250317','20250616','I003')
report_df0 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20241217','20250316','I003')


# 2024년
report_df1 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20240917','20241216','I003')
report_df2 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20240617','20240916','I003')
report_df3 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20240317','20240616','I003')
report_df4 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20231217','20240316','I003')

# 2023년
report_df5 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20230917','20231216','I003')
report_df6 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20230617','20230916','I003')
report_df7 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20230317','20230616','I003')
report_df8 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20221217','20230316','I003')


# 2022년
report_df10 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20220917','20221216','I003')
report_df11 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20220617','20220916','I003')
report_df12 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20220317','20220616','I003')
report_df13= 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20211217','20220316','I003')


# 2021년
report_df14 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20210917','20211216','I003')
report_df15 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20210617','20210916','I003')
report_df16 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20210317','20210616','I003')
report_df17= 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20201217','20210316','I003')


# 2020년
report_df18 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20200917','20201216','I003')
report_df19 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20200617','20200916','I003')
report_df20 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20200317','20200616','I003')
report_df21 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20191217','20200316','I003')


# 2019년
report_df22 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20190917','20191216','I003')
report_df23 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20190617','20190916','I003')
report_df24 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20190317','20190616','I003')
report_df25 = 공시보고서_접수번호목록_가져오기_디테일_no고유번호( '20181217','20190316','I003')




report_df = pd.concat([report_df, report_df0, report_df1, report_df2, report_df3, report_df4, report_df5,report_df6 ,report_df7 ,report_df8 , report_df10,report_df11,report_df12,report_df13, report_df14,report_df15,report_df16,report_df17, report_df18,report_df19,report_df20,report_df21, report_df22,report_df23,report_df24,report_df25],axis=0)
report_df.to_excel('시장조치안내_2019_2025.xlsx', index=False)

