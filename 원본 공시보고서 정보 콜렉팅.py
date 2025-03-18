# 참고: https://yogyui.tistory.com/entry/%EA%B8%88%EC%9C%B5%EA%B0%90%EB%8F%85%EC%9B%90OPENDART-%EC%A0%84%EC%9E%90%EA%B3%B5%EC%8B%9C-Open-API-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0
from bs4 import BeautifulSoup


# 1. 주주총회소집공고 공시보고서 리스트 불러오기
def collect_statement_list(start_date, end_date,pblntf_detail_ty):
    """특정 조건에 맞는 공시보고서 리스트 불러오는 매서드"""

    url = 'https://opendart.fss.or.kr/api/list.json'

    # 빈 df 생성(API로 불러와지는 데이터에 맞게 미리 정의 필요)
    res_df = pd.DataFrame(columns = ['corp_code', 'corp_name', 'stock_code'
                                , 'corp_cls', 'report_nm','rcept_no'
                                , 'flr_nm', 'rcept_dt', 'rm'])
    page_no = 1
    while True:
        params = {"crtfc_key": api_key,
            "bgn_de":   start_date,
            "end_de": end_date,
            "pblntf_detail_ty": pblntf_detail_ty,
            "page_no": page_no,
            "page_count": '100'}

        res = requests.get(url, params=params) # API 호출
        data = res.json()   # 불러온 json to dictionary 변환


        if data['page_no'] != page_no:
            print("페이지가 맞지 않습니다, 조회한 페이지: ",data['page_no'],"!= param page_no: ",page_no)
            break

        # if data['message'] == '조회된 데이타가 없습니다.': #데이타 ㅎ
        #     continue

        try:
            new_data = pd.DataFrame(data["list"]) # dictionary to df 변환
            res_df = pd.concat([res_df, new_data], ignore_index=True)
        except Exception as e:
            print("에러 발생: ",e, "에러 발생 구역의 고유번호: ",corp_code)

        page_no += 1

    print("정기 보고서 불러오기 작업 완료----------------------------------")
    #
    res_df["report_nm"] = res_df["report_nm"].str.replace(r"\[.*?\]|\(.*?\)", "", regex=True).str.strip()
    return res_df

# 주주총회소집공고 수집
rep_df = collect_statement_list(start_date='20250314',end_date='20250317',pblntf_detail_ty='E006')

# 500대 기업의 보고서인지 체크
def is_500comp(corp_code):
    com500_df = pd.read_excel('2024년 기준 500대 기업(고유번호 및 종목코드 포함).xlsx',
                              dtype={"순위": int,
                                     "종목코드": str,
                                     "고유번호": str})

    if str(corp_code) in list(com500_df['고유번호']):
        return "●"
    else:
        return ""


rep_df['500comp'] = rep_df['corp_code'].apply(is_500comp)
rep_df = rep_df[rep_df['500comp']=="●"] # 500대 기업의 보고서 발표 정보만 남기기

# 2. 보고서 원본 파일 불러오기
def save_statement_report(rcept_no):
    """디렉토리 내 공시보고서 원본파일을 저장하는 매서드"""

    # 공시보고서 원본 문서를 불러오는 API
    # 반환 결과 = zip file 포맷의 바이너리 파일(xml)
    url = 'https://opendart.fss.or.kr/api/document.xml'

    # 공시보고서의 고유 접수번호를 input으로 넣어줘야함
    params = {"crtfc_key": api_key, "rcept_no": rcept_no}


    # 파일 저장 경로(디렉토리) 지정
    doc_zip_path = os.path.abspath(f'./{rcept_no}.zip')

    if not os.path.isfile(doc_zip_path):
        res = requests.get(url, params=params)

        with open(doc_zip_path, 'wb') as f: # 바이너리 모드 = wb
            f.write(res.content)

    zf = ZipFile(doc_zip_path)  # zip 파일열기
    zf.extractall()             # 디렉토리 내 zip 압축 해제


    # 파일 이름 불러오기
    zipinfo = zf.infolist()
    filenames = [x.filename for x in zipinfo]
    filename = filenames[0]

    # 압축 파일 닫기
    zf.close()

    # 디렉토리 내 zip 파일 지우기
    os.remove(doc_zip_path)
    print(rcept_no,"저장이 완료되었습니다.")


for rcept_no in rep_df['rcept_no']:
    save_statement_report(rcept_no)

# 3. 위원회 관련 xml 내 table를 df로 만들기
def read_statement_report():
    # 디렉토리 내 파일 불러오기
    with open(filename, "r", encoding="utf-8") as file:
        xml_content = file.read()

    # BeautifulSoup으로 XML 파싱
    soup = BeautifulSoup(xml_content, 'xml')

    # '이사회내 위원회'가 포함된 제목 찾기
    # 📌 이후에 '위원회'와 '활동내역'이 존재하는 제목 찾기로 리팩토링
    target_title = None
    for title in soup.find_all("TITLE"):
        if '이사회내 위원회' in title.text:
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