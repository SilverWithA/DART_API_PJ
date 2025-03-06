from multiprocessing.forkserver import connect_to_new_process

import pandas as pd
import requests


corp_code = "00126380"
df = pd.read_excel('(2022-2024) 500대기업 이사보상배율_v1_20250415.xlsx',sheet_name="2024 500대기업", dtype={"고유번호":str, "종목코드":str})


error_corp_list = []
# 영업이익 크롤링
def 재무제표_주요항목(df, cnt = 0):
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"


    res_df = pd.DataFrame(columns=['rcept_no', 'reprt_code', 'bsns_year', 'corp_code', 'stock_code',
       'fs_div', 'fs_nm', 'sj_div', 'sj_nm', 'account_nm', 'thstrm_nm',
       'thstrm_dt', 'thstrm_amount', 'frmtrm_nm', 'frmtrm_dt', 'frmtrm_amount',
       'bfefrmtrm_nm', 'bfefrmtrm_dt', 'bfefrmtrm_amount', 'ord', 'currency'])

    for index, corp_code in enumerate(df['고유번호']):

        if not corp_code:
            print(df['회사명'][index],"는 고유번호 누락으로 건너뜁니다.")
            continue

        params = {"crtfc_key": api_key,
                      "corp_code": corp_code,
                      "bsns_year":'2024',
                  "reprt_code":"11011",
                      "fs_div":"CFS"}

        try:
            res = requests.get(url, params=params)
            data = res.json()

            if data['message'] == '조회된 데이타가 없습니다.':
                continue

            if data['list']:
                tmp = pd.DataFrame(data['list'])
                res_df = pd.concat([res_df, tmp], ignore_index=True)

            cnt += 1
        except Exception as e:
            print(e, end=' ')
            error_corp_list.append(corp_code)
            print(df['종목명'][index], "의 유상증자 결정 호출중 에러가 발생했습니다.")

    print("총 ", cnt,"개 사의 재무제표 정보를 모았습니다.")
    return res_df

res_df = 재무제표_주요항목(df)
res_df.to_excel('2023년 재무주요계정.xlsx', index=False)



OFS_corp_code = ["00148504" ,"00382001" ,"00389013" ,"00382834" ,"00396518" ,"00383019" ,"01032422" ,"00186513" ,"00393636" ,"00908155" ,"00909349" ,"00103176" ,"00158307" ,"00113562" ,"01133217" ,"01629495" ,"01323032" ,"00895985" ,"00105466" ,"00104069" ,"00164308" ,"00277499" ,"00332468" ,"00367862" ,"00530343" ,"00245357" ]

def 재무제표_전체항목(df, cnt = 0):
    cnt = 0
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"


    res_df = pd.DataFrame(columns=['rcept_no', 'reprt_code', 'bsns_year', 'corp_code', 'sj_div', 'sj_nm',
       'account_id', 'account_nm', 'account_detail', 'thstrm_nm',
       'thstrm_amount', 'frmtrm_nm', 'frmtrm_amount', 'bfefrmtrm_nm',
       'bfefrmtrm_amount', 'ord', 'currency', 'thstrm_add_amount'])

    for corp_code in OFS_corp_code:

        if not corp_code:
            print(corp_code,"는 고유번호 누락으로 건너뜁니다.")
            continue

        params = {"crtfc_key": api_key,
                      "corp_code": corp_code,
                      "bsns_year":'2024',
                  "reprt_code":"11011",     # 사업보고서
                      "fs_div":"OFS"}       # 연결 기준

        try:
            res = requests.get(url, params=params)
            data = res.json()

            if data['message'] == '조회된 데이타가 없습니다.':
                continue

            if data['list']:
                tmp = pd.DataFrame(data['list'])
                res_df = pd.concat([res_df, tmp], ignore_index=True)

            cnt += 1
        except Exception as e:
            print(e, end=' ')
            # error_corp_list.append(corp_code)
            # print(df['종목명'][index], "의 재무제표 전체 게정 호출중 에러가 발생했습니다.")

    print("총 ", cnt,"개 사의 재무제표 정보를 모았습니다.")
    return res_df

raw_finance_df = 재무제표_전체항목(df)
res_df.to_excel('raw 30대그룹 연결아닌재무33.xlsx', index=False)
