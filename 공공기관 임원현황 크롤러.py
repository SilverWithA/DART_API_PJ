from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import pandas as pd

chrome_options = Options()
chrome_options.add_argument("--headless=new")  # 최신 크롬 headless 모드
chrome_options.add_argument("--window-size=1920,1080")  # 화면 크기 지정
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


공공기관2025_df = pd.read_excel('공공기관 기관장 상임감사 임원현황_v8_20250610의 사본.xlsx',dtype='str',sheet_name='2025 공공기관')
공공기관명_2025 = list(공공기관2025_df['기관명'])
total_cnt = len(공공기관명_2025)

########## 공공기관 임원현황 크롤러 ################ -> 클래스화 필요
def __기관명_드롭다운_클릭__(driver):
    # 기관명입력 드롭다운 요소 찾기 및 클릭
    기관명검색 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='기관명검색']")))
    기관명검색.click()
def __기관명_드롭다운에_입력후조회__(driver, 공공기관명):
    search_box = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field"))
    )
    search_box.clear()
    search_box.send_keys(공공기관명)
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".select2-results__option"))
    )
    search_box.send_keys(Keys.ENTER)

    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='조회']]"))
    )
    driver.execute_script("arguments[0].click();", button)
def 공공기관_임원현황_크롤러(공공기관명_2025, 각기관당수집보고서개수):

    column_names = ['공공기관명', '테이블순번', '등록일', '사유발생일', 'dummy4', 'dummy5', 'dummy6', 'dummy7', 'dummy8', 'dummy9'
        , 'dummy10', 'dummy11', 'dummy12', 'dummy13', 'dummy14', 'dummy15', 'dummy16', 'dummy17'
        , 'dummy18', 'dummy19', 'dummy20', 'dummy21', 'dummy22', 'dummy23', 'dummy24']
    a_raw_tables = pd.DataFrame(columns=column_names)  # 최종 크롤링 취합본을 담아줄 데이터 df
    수집실패_공공기관명 = []  # 크롤링 실패한 공공기관 모음

    # 공공기관명 = 공공기관명_2025[0]
    # 각기관당수집보고서개수 = 1
    for index, 공공기관명 in enumerate(공공기관명_2025):
        time.sleep(1)

        print(f' {index} / {total_cnt} - {int(index/total_cnt*100)} %')

        driver = webdriver.Chrome(options=chrome_options)  # 백그라운드 실행(크롬 탭 보이지 않음)
        # driver = webdriver.Chrome()                      # 테스트용 코드(크롬 탭 보임)
        driver.get('https://alio.go.kr/item/itemOrganList.do?apbaId=C1327&reportFormRootNo=20305')         # 공공기관 임원현황 웹페이지 열기

        try:
            __기관명_드롭다운_클릭__(driver)

            # 드롭다운 검색창에 공공기관명 입력하여 해당 공공기관 보고서리스트 페이지로 이동
            __기관명_드롭다운에_입력후조회__(driver,공공기관명)

            time.sleep(1)

            # 임원현황 보고서 요소 추출
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list-inner2"))
            )             # 리스트 로딩 대기

            임원현황보고서_elements = driver.find_element(By.CLASS_NAME, "list-inner2")
            li_count = min(각기관당수집보고서개수, len(임원현황보고서_elements.find_elements(By.TAG_NAME, "li")))


            # 임원 현황 열기
            # idx = 0
            for idx in range(li_count):
                try:
                    임원현황보고서_elements = driver.find_element(By.CLASS_NAME, "list-inner2")
                    li_list = 임원현황보고서_elements.find_elements(By.TAG_NAME, "li")
                    li = li_list[idx]

                    # 등록일, 사유발생일
                    try:
                        등록일 = li.find_element(By.XPATH, ".//p[span='등록일']/em").text
                    except:
                        등록일 = None
                    try:
                        사유발생일 = li.find_element(By.XPATH, ".//p[span='사유발생일']/em").text
                    except:
                        사유발생일 = None

                    # 임원현황 클릭
                    임원현황 = li.find_element(By.XPATH, ".//span[@class='tit' and contains(text(), '임원')]")
                    driver.execute_script("arguments[0].click();", 임원현황)
                except StaleElementReferenceException:
                    임원현황보고서_elements = driver.find_element(By.CLASS_NAME, "list-inner2")
                    li_list = 임원현황보고서_elements.find_elements(By.TAG_NAME, "li")
                    li = li_list[idx]

                # 새 창이 열릴 때까지 대기
                WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[-1])  # 새창으로 스위치
                time.sleep(0.5)

                # border = 1인 테이블 요소 모두 추출
                target_tables = driver.find_elements(By.XPATH, "//table[@border='1']")


                # i = 3
                # table = target_tables[i]
                for i, table in enumerate(target_tables):
                    html = table.get_attribute('outerHTML')  # table 요소를 html로 변환
                    soup = BeautifulSoup(html, 'html.parser')  # html을 beautifulsoup로 파싱
                    rows = soup.find_all('tr')  # table에 row에 해당하는 tr요소를 모두 불러옴


                    # 임원현황 보고서 내 table 요소를 돌며 데이터 수집
                    tmp = []
                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        # tr에 있는 모든 text 불러서 list로 변환
                        col_list = [col.get_text(strip=True) for col in cols]
                        # 공시보고서 내 정보 외 필수 항목 추가하기
                        col_list.insert(0, 사유발생일)
                        col_list.insert(0, 등록일)
                        col_list.insert(0, i)  # 공시보고서 내 테이블 배치 순서
                        col_list.insert(0, 공공기관명)  # 접수번호

                        # raw_tables와 스키마를 맞추기 위한 밑작업
                        # column 개수 맞춰주기
                        if len(col_list) < 25:
                            col_list += [None] * (25 - len(cols) - 4)
                        else:
                            col_list = col_list[:25]
                        tmp.append(col_list)
                    # tables의 정보를 저장한 tmp 리스트를 df화한 뒤 raw_tables와 row기준으로 병합

                    tmp_df = pd.DataFrame(data=tmp, columns=column_names).copy()
                    a_raw_tables = pd.concat([a_raw_tables, tmp_df], axis=0)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "list-inner2"))
                )
            driver.quit()

        except:
            수집실패_공공기관명.append(공공기관명)
            driver.quit()
            continue

    return a_raw_tables, 수집실패_공공기관명

# # 임원현황 크롤러 실행 예시 코드
# 공공기관_임원현황2025_크롤링, 수집실패_공공기관명 = 공공기관_임원현황_크롤러(공공기관명_2025 , 1)
# 공공기관_임원현황2025_크롤링.to_excel('공공기관_임원현황2025_크롤링.xlsx')


########## 공공기관 임원모집공고 크롤러 ################
def 공공기관_임원모집공고_크롤러(불러올_페이지수):
    column_names = ['기관명', '공고명', '날짜']
    a_raw_tables = pd.DataFrame(columns=column_names)  # 최종 크롤링 취합본을 담아줄 데이터 df

    # driver = webdriver.Chrome(options=chrome_options)  # 백그라운드 실행(크롬 탭 보이지 않음)
    driver = webdriver.Chrome()                      # 테스트용 코드(크롬 탭 보임)
    driver.get('https://www.alio.go.kr/mobile/occasional/officerList.do')  # 공공기관 임원현황 웹페이지
    time.sleep(2)

    wait = WebDriverWait(driver, 10)

    # 페이지 불러오기(더보기 클릭 -> 페이지 스크롤)
    불러올_페이지수 = 3
    i = 0
    while True:
        if i == 불러올_페이지수:
            break
        더보기버튼 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "p.more-bt")))
        더보기버튼.click()
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # 페이지 스크롤
        i += 1

    div_list = driver.find_element(By.CLASS_NAME, "list")
    li_elements = div_list.find_elements(By.TAG_NAME, "li")
    # li = li_elements[0]

    raw_data = []
    for idx, li in enumerate(li_elements):

        print(f" {idx} / {len(li_elements)} - {int(idx/len(li_elements)*100)} %")
        기관명 = li.find_element(By.CSS_SELECTOR, "p.label").text.strip()
        공고명 = li.find_element(By.CSS_SELECTOR, "p.tit").text.strip()
        날짜 = li.find_element(By.CSS_SELECTOR, "p.date span").text.strip()

        tmp = [기관명, 공고명, 날짜]
        raw_data.append(tmp)

    공공기관_임원모집_df = pd.DataFrame(raw_data, columns=column_names)
    공공기관_임원모집_df.to_excel('공공기관_임원모집_251017.xlsx')
