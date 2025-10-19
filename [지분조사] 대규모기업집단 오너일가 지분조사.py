
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import win32com.client
# import openpyxl           # 엑셀 백그라운드 실행
import win32com.client      # 엑셀 파일 경합할시 오류발생

chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
chrome_options.add_argument("--window-size=1920,3000")
import pandas as pd
import time


from app.model.Info_collecter import API_info_finder
finder = API_info_finder()


###################### 1. 고유번호 목록 불러오기 ####################
group_2024_df = pd.read_excel('2024년 대규모기업집단 오너일가 지분 재조사_250912.xlsx',sheet_name='대기업집단 계열사(24)', dtype=str)
corpe_codes = list(set(list(group_2024_df['고유번호'])))


###################### 2. 시보고서 목록 불러오기 ####################

def 반기_최대주주_대량보유보고서_목록():
    # 반기보고서 목록
    group_2Q = finder.공시보고서_접수번호목록_가져오기_디테일버전(corpe_codes, '20250601', '20250831', "A002")
    group_2Q.to_excel('25년 대규모기업집단 반기보고서 목록.xlsx',index=False)

    # 최대주주등소유주식변동신고서 > 거래소공시 > 지분공시(I004)
    group_지분공시 = finder.공시보고서_접수번호목록_가져오기_디테일버전(corpe_codes, '20250901', '20250908', "I004")
    group_지분공시.to_excel("상반기 대기업집단 최대주주소유주식변동신고_250908까지.xlsx",index=False)

    # "D001": "주식등의대량보유상황보고서" -- 수집 전
    group_주식대량 = finder.공시보고서_접수번호목록_가져오기_디테일버전(corpe_codes, '20250530', '20250909', "D001")
    group_주식대량.to_excel("상반기 대기업집단 주식등의대량보유상황보고서_250909.xlsx",index=False)

def 대규모기업집단현황공시_목록_불러오기():
    # 공정위 공시 > 기업집단현황공시 로 검색
    group_2024_기업집단현황공시 = finder.공시보고서_접수번호목록_가져오기_디테일버전(corpe_codes, '20240520', '20241231', "J004")
    group_2024_기업집단현황공시.to_excel('2024년 계열사 기업집단현황 공시 목록.xlsx',index=False)

    # 대표회사만 필터링하기
    datafilter = group_2024_기업집단현황공시['report_nm'].str.contains("1/4분기")
    valid_대표회사현황공시 = group_2024_기업집단현황공시[datafilter]
    datafilter2 = valid_대표회사현황공시['report_nm'].str.contains("대표회사")
    valid_news_data = valid_대표회사현황공시[datafilter2]

    valid_news_data.to_excel('2024_대규모기업집단_대표회사.xlsx',index=False)







###################### 3. 공시 보고서 raw table 크롤링하기 ####################
# (1) 대규모기업집단 오너일가 리스트의 기본은 대규모기업집단 소유주식현황 내 동일인 이나 친족으로 분류된 경우를 기준으로 함

group_대표_현황공시 = pd.read_excel('2024년 대규모기업집단 오너일가 지분 재조사_250912.xlsx',sheet_name='대기업집단 계열사(24)', dtype=str)
group_대표_현황공시 = group_대표_현황공시[group_대표_현황공시['대표회사'] == "●"]
rept_nums = group_대표_현황공시['대규모기업집단현황공시 접수번호']

# 문제점: 회사명 불완전 크롤링으로 전처리 과정 길어지는 문제
def raw_대규모기업집단_엑셀로_크롤링(rept_nums):
    """백그라운드 실행이 되지 않는 프로그램으로 실행시 다른 작업을 수행하지 못하게 됩니다"""

    total = len(rept_nums)
    a_error_list= []
    excel_file_path = rf'C:\Users\HP\OneDrive\바탕 화면\대규모기업집단.xlsx'
    pre_last_row = 1
    rept_no = "20240531001571"

    # 엑셀 열기위한 밑작업
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True  # 엑셀을 눈에 보이게 실행 (테스트용)

    for idx, rept_no in enumerate(rept_nums):

        print(f" {idx} / {total} - (", round(idx / total * 100,1),")%")   # 진행상황 콘솔에 프린트
        time.sleep(2)

        try:
            driver = webdriver.Chrome()                       # 테스트용 코드(크롬 탭 보임)
            driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")   # 접수번호를 이용해 공시 보고서 접속


            # '소유지분현황'이라는 이름을 가진 목차 선택 및 클릭
            director_section = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(normalize-space(text()), '소유지분현황')]"))
            )
            director_section[0].click()

            actions = ActionChains(driver)
            actions.move_to_element(director_section[0]).perform()  # 요소 위로 이동

            # 현재 창 크기의 최대 크기
            max_x = driver.execute_script("return window.innerWidth") - 10
            max_y = driver.execute_script("return window.innerHeight") - 10

            x = min(300, max_x)  # 300이 화면 너비를 초과하지 않도록 조정
            y = min(200, max_y)  # 200이 화면 높이를 초과하지 않도록 조정

            actions.move_by_offset(x, y).click().perform()

            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()  # 전체선택
            actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()  # 복사하기

            driver.quit()

            wb = excel.Workbooks.Open(excel_file_path)  # 미리 저장해 둔 엑셀 파일 열기
            sheet_element = wb.Sheets("raw")       # 시트 이동

            # 접수번호 추가하기
            sheet_element.Range(f"A{pre_last_row}").Select()  # 셀선택
            sheet_element.Cells(pre_last_row, 1).Value = rept_no


            # 값 붙여넣기
            sheet_element.Range(f"B{pre_last_row}").Select()  # 셀선택
            sheet_element.PasteSpecial()  # 클립보드에서 HTML 서식 포함

            pre_last_row = sheet_element.UsedRange.Rows.Count + sheet_element.UsedRange.Row +1
            # pre_last_row = sheet_element.Cells(sheet_element.Rows.Count, 2).End(-4162).Row   # -4162 = xlUp
            # pre_last_row += 1


         except:
            a_error_list.append(rept_no)
            continue
    print("작업이 끝났습니다. 엑셀 파일을 꼭 저장해주세요")

# 크롤링 시작
# raw_대규모기업집단_엑셀로_크롤링(rept_nums)




# (2) 최대주주변동 보고서 크롤링
def raw_report_최대주주보고서_크롤링(report_최대주주):

    # raw_tables에 병합을 위한 스키마 지정
    column_names = ['접수번호', '테이블순번', 'dummy3', 'dummy4', 'dummy5', 'dummy6', 'dummy7', 'dummy8', 'dummy9'
                                , 'dummy10', 'dummy11', 'dummy12', 'dummy13', 'dummy14', 'dummy15', 'dummy16', 'dummy17'
                                , 'dummy18', 'dummy19','dummy20', 'dummy21', 'dummy22', 'dummy23', 'dummy24','dummy25']

    a_raw_tables = pd.DataFrame(columns=column_names) # raw 데이터를 담아줄 데이터
    total = len(report_최대주주)                    # 크롤링 현황을 알기 위한 전체 1분기보고서 개수
    a_error_list = []                                 # 에러가 발생한 접수번호를 담기위한 리스트
    # rept_no = "20250530800802"
    # idx=0


    for idx, rept_no in enumerate(report_최대주주['rcept_no']):

        print(f" {idx} / {total} - (", round(idx / total * 100,1),")%")   # 진행상황 콘솔에 프린트

        time.sleep(2)
        try:
            driver = webdriver.Chrome(options=chrome_options)   # 백그라운드 실행(크롬 탭 보이지 않음)
            # driver = webdriver.Chrome()                       # 테스트용 코드(크롬 탭 보임)
            driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")   # 접수번호를 이용해 공시 보고서 접속

            # iframe 속으로 driver 전환
            iframe = driver.find_element(By.ID, "ifrm")
            driver.switch_to.frame(iframe)

            # border가 1인 table과 table에
            target_elemnets = driver.find_elements(By.XPATH,"//table[@border='1']")


            # 각 테이블 요소 loop
            for i,table in enumerate(target_elemnets):


                html = table.get_attribute('outerHTML')             # table 요소를 html로 변환
                soup = BeautifulSoup(html, 'html.parser')    # html을 beautifulsoup로 파싱
                rows = soup.find_all('tr')                          # table에 row에 해당하는 tr요소를 모두 불러옴

                tmp = []
                for row in rows:
                    cols = row.find_all(['td', 'th'])

                    # tr에 있는 모든 text 불러서 list로 변환
                    col_list = [col.get_text(strip=True) for col in cols]

                    # 공시보고서 내 정보 외 필수 항목 추가하기
                    col_list.insert(0, i)                # 공시보고서 내 테이블 배치 순서
                    col_list.insert(0, rept_no)          # 접수번호

                    # raw_tables와 스키마를 맞추기 위한 밑작업
                    # column 개수 맞춰주기
                    if len(col_list) < 25:
                        col_list += [None] * (25 - len(cols)-2)
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


    return a_raw_tables, a_error_list


# (3) 주식등의대량보유 보고서 크롤링
def raw_report_주식대량보고서_크롤링(report_주식대량):

    # raw_tables에 병합을 위한 스키마 지정
    column_names = ['접수번호', '테이블순번', 'dummy3', 'dummy4', 'dummy5', 'dummy6', 'dummy7', 'dummy8', 'dummy9'
                                , 'dummy10', 'dummy11', 'dummy12', 'dummy13', 'dummy14', 'dummy15', 'dummy16', 'dummy17'
                                , 'dummy18', 'dummy19','dummy20', 'dummy21', 'dummy22', 'dummy23', 'dummy24','dummy25']

    a_raw_tables = pd.DataFrame(columns=column_names) # raw 데이터를 담아줄 데이터
    total = len(report_주식대량)                    # 크롤링 현황을 알기 위한 전체 1분기보고서 개수
    a_error_list = []                                 # 에러가 발생한 접수번호를 담기위한 리스트
    # rept_no = "20250905000049"
    # idx=0


    for idx, rept_no in enumerate(report_주식대량['rcept_no']):

        print(f" {idx} / {total} - (", round(idx / total * 100,1),")%")   # 진행상황 콘솔에 프린트

        time.sleep(2)
        try:
            driver = webdriver.Chrome(options=chrome_options)   # 백그라운드 실행(크롬 탭 보이지 않음)
            # driver = webdriver.Chrome()                       # 테스트용 코드(크롬 탭 보임)
            driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")   # 접수번호를 이용해 공시 보고서 접속


            director_section = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(normalize-space(text()), '대량보유자에')]"))
            )
            director_section[0].click()

            # iframe 속으로 driver 전환
            iframe = driver.find_element(By.ID, "ifrm")
            driver.switch_to.frame(iframe)

            # border가 1인 table과 table에
            target_elemnets = driver.find_elements(By.XPATH,"//table[@border='1']")


            # 각 테이블 요소 loop
            for i,table in enumerate(target_elemnets):


                html = table.get_attribute('outerHTML')             # table 요소를 html로 변환
                soup = BeautifulSoup(html, 'html.parser')    # html을 beautifulsoup로 파싱
                rows = soup.find_all('tr')                          # table에 row에 해당하는 tr요소를 모두 불러옴

                tmp = []
                for row in rows:
                    cols = row.find_all(['td', 'th'])

                    # tr에 있는 모든 text 불러서 list로 변환
                    col_list = [col.get_text(strip=True) for col in cols]

                    # 공시보고서 내 정보 외 필수 항목 추가하기
                    col_list.insert(0, i)                # 공시보고서 내 테이블 배치 순서
                    col_list.insert(0, rept_no)          # 접수번호

                    # raw_tables와 스키마를 맞추기 위한 밑작업
                    # column 개수 맞춰주기
                    if len(col_list) < 25:
                        col_list += [None] * (25 - len(cols)-2)
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


    return a_raw_tables, a_error_list






