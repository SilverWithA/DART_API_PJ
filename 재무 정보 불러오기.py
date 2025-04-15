import pandas as pd

#### <API 정보>
# API 관련 페이지: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
## - 단일회사 전체 재무제표 개발가이드
### 삼성전자 고유번호 = 00126380

df = pd.read_excel('5대그룹 계열사.xlsx',sheet_name='2024_30대그룹_보고서제출', dtype={"고유번호":str})

url = url = 'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json'

#
fiance_df = pd.DataFrame(columns=['rcept_no', 'reprt_code', 'bsns_year', 'corp_code', 'stock_code',
       'fs_div', 'fs_nm', 'sj_div', 'sj_nm', 'account_nm', 'thstrm_nm',
       'thstrm_dt', 'thstrm_amount', 'frmtrm_nm', 'frmtrm_dt', 'frmtrm_amount',
       'bfefrmtrm_nm', 'bfefrmtrm_dt', 'bfefrmtrm_amount', 'ord', 'currency'])


error_list = []
compelte_cnt = 0
for idx, corp_code in enumerate(corp_list):

       params = {
              "crtfc_key": api_key,
              "corp_code": str(corp_code),  #고유번호
              "bsns_year": "2024",   # 사업년도
              "reprt_code": "11011" # 사업보고서
       }


       res = requests.get(url,params=params)
       data = res.json()
       try:
              tmp_data = pd.DataFrame(data["list"])  # dictionary to df 변환
              fiance_df = pd.concat([fiance_df,tmp_data])
              compelte_cnt += 1

       except Exception as e:
              print("에러 발생: ", e, "에러 발생 구역의 고유번호: ", corp_code)
              error_list.append(corp_code)


# error_list 내 있는 수집 안된 계열사 확인 = 사업보고서 미제출사로 처리

fiance_df.to_excel('5대기업 재무항목 raw.xlsx', index=False)