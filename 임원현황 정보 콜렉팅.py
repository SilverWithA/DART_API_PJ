import requests

corp_code = '00126380'  # 삼성전자
# 임원현황 조회 api= https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019010
def call_officer_list(corp_code):
    url = 'https://opendart.fss.or.kr/api/exctvSttus.json'

    param = {
        "crtfc_key": api_key,
        "corp_code":corp_code,
        "bsns_year": 2024,      # 사업연도
        "reprt_code": '11011'   # 사업보고서
    }

    res = requests.get(url, param)
    data = res.json()                   # request의 Reseponse to json

    df = pd.DataFrame(data["list"])     # json to df

    # df에 기업명, 고유번호, 출처보고서, 회계년도, 보고서공시일 추가하기