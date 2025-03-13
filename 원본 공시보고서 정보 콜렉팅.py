# 참고: https://coding-kindergarten.tistory.com/97
import os.path
import zipfile
import os

# 조회할 공시 보고서의 접수번호가 필요함
# 사업보고서 제출 확인.py에서 참고(매서드 만들기)

def collect_statement_list(df, start_date, end_date,pblntf_detail_ty):

    url = 'https://opendart.fss.or.kr/api/list.json'

    # 빈 df 생성(API로 불러와지는 데이터에 맞게 미리 정의 필요)
    res_df = pd.DataFrame(columns = ['corp_code', 'corp_name', 'stock_code'
                                , 'corp_cls', 'report_nm','rcept_no'
                                , 'flr_nm', 'rcept_dt', 'rm'])

    for index, corp_code in enumerate(df['고유번호']):
        if corp_code is None:
            continue

        params = {"crtfc_key": api_key,
            "corp_code": '00126380',
            "bgn_de":   str(20240101),
            "end_de": str(20250313),
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

    print("정기 보고서 불러오기 작업 완료----------------------------------")
    #
    res_df["report_nm"] = res_df["report_nm"].str.replace(r"\[.*?\]|\(.*?\)", "", regex=True).str.strip()
    return res_df


url = 'https://opendart.fss.or.kr/api/document.xml'

params = {"crtfc_key": api_key, "rcept_no": '20250218001524'}
doc_zip_path = os.path.abspath('./원본파일.zip')

if not os.path.isfile(doc_zip_path):
    res = requests.get(url, params=params)
    with open(doc_zip_path, 'wb') as f:
        f.write(res.content)


zf = zipfile.ZipFile(doc_zip_path)
zf.extractall()

