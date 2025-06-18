## 공시보고서 내 특정 키워드가 존재하면 체크해주는 기능

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. ChromeOptions 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화

chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
chrome_options.add_argument("--window-size=1920x1080")  # 화면 해상도 설정
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

key_df = pd.read_excel('(최종본)2022-2025 상장사 감액배당 실태조사_20250509_v2 (1).xlsx', sheet_name='raw_주총공고 준비금 감액', dtype=str)

# key_df = key_df[key_df['조사완료']=="0"]
error_rept_list = []

# rept_no = '20250317000669' # 테스트용 접수번호


######## 주주총회 내 감액 결정 확인하기

keywords = ["자본준비금","자본잉여금","전입","감소","감액"]
def 전체문서로_전환(driver):
    # 전체문서 검색 선택
    radio_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "searchGubun2"))
    )
    radio_button.click()

    # 검색어 입력으로 전체문서 모드로 전환
    search_box = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "searchWord"))
    )
    search_box.send_keys("ㅁㄴㅇㄹ")
    search_box.send_keys(Keys.ENTER)

    # 전체문서 검색시 뜨는 팝업 처리
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())  # 팝업이 뜰 때까지 최대 5초 대기
        alert = driver.switch_to.alert  # 팝업으로 전환
        alert.accept()  # '확인' 누르기
        time.sleep(1)
        alert.accept()  # '확인' 누르기
    except:
        pass
def find_keywords(rept_no):

        time.sleep(1)
        try:
            # 1. DART 접속
            driver = webdriver.Chrome(options=chrome_options) # 백그라운드 실행
            # driver = webdriver.Chrome() # 테스트용 코드
            driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")    # 웹페이지 접속

            # 팝업닫기
            try:
                # btnClose 버튼을 기다리기
                close_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btnClose"))
                )
                close_button.click()
            except:
                pass


            # 목차 선택
            wait = WebDriverWait(driver, 2)
            elements = wait.until(EC.presence_of_all_elements_located((
                By.XPATH,
                "//a[normalize-space(text())='주주총회소집공고' or normalize-space(text())='주주총회 소집공고']"
            )))

            count = len(elements)

            # 목차 개수만큼 루프
            for i in range(count):
                # print(f"[INFO] 현재 인덱스: {i}")

                try:
                    # 리스트를 매번 새로 가져오기 (DOM 변경 대응)
                    elements = wait.until(EC.presence_of_all_elements_located((
                        By.XPATH,
                        "//a[normalize-space(text())='주주총회소집공고' or normalize-space(text())='주주총회 소집공고']"
                    )))

                    # 인덱스 유효성 체크
                    if i >= len(elements):
                        print(f"[WARNING] 현재 elements 길이보다 인덱스 {i}가 큼")
                        break

                    elem = elements[i]
                    driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                    elem.click()

                    time.sleep(1)

                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ifrm"))
                    )

                    driver.switch_to.frame(iframe)  # 해당 요소로 전환
                    text = driver.find_element(By.TAG_NAME, "body").text

                    matched_keyword = next((k for k in keywords if k in text), None)
                    if matched_keyword:
                        driver.quit()
                        return matched_keyword
                    else:
                        driver.switch_to.default_content()

                except Exception as e:
                    print(f"[ERROR] 루프 중 예외 발생: {e}")
                    continue

            driver.quit()
            return "x"

        except Exception as e:
            error_rept_list.append(rept_no)
            driver.quit()
            print(rept_no,"report is not collected: ", e)

key_df_head = key_df.head(10)
key_df_head['테스트중'] = key_df_head['접수번호'].progress_apply(find_keywords)


######## 현금ㆍ현물배당결정 보고서 크롤링
rept_no = "20220310801825" # 20250228800995  # 20240223800795
keywords = ["준비금", "재원", "과세", "비과세"]


# 키워드가 유효한 컬럼만
def find_keyword2(rept_no):
    time.sleep(1)
    try:
        # 1. DART 접속
        driver = webdriver.Chrome(options=chrome_options)  # 백그라운드 실행
        # driver = webdriver.Chrome() # 테스트용 코드
        driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")  # 웹페이지 접속

        iframe = driver.find_element(By.ID, "ifrm")
        driver.switch_to.frame(iframe)

        # 키워드가 존재하는지 확인

        text = driver.find_element(By.TAG_NAME, "body").text

        # 키워드가 있으면 존재하는 키워드 값을 반환
        matched_keyword = next((k for k in keywords if k in text), None)
        if matched_keyword:
            rows = driver.find_elements(By.XPATH, "//tr")

            for row in rows:
                if "배당금총액(원)" in row.text:
                    # 해당 tr 내의 td 요소 가져오기
                    tds = row.find_elements(By.TAG_NAME, "td")
                    if len(tds) > 1:
                        # 보통 텍스트는 두 번째 td에 있음
                        amount_text = tds[1].text
                        driver.quit()
                        # print(matched_keyword)
                        return f"{matched_keyword}" +"/" + f"{amount_text}"

                    else:
                        # print("없음")
                        return
        else:
            # print("없음")
            driver.switch_to.default_content()
        driver.quit()

    except Exception as e:
        error_rept_list.append(rept_no)
        driver.quit()
        print(rept_no, "report is not collected: ", e)

# 2023-2025 작업
# not_2022 = key_df['접수연도'] == '2022'
# allo_2023_df = key_df[~not_2022]


key_df['크롤링정보'] = key_df['접수번호'].progress_apply(find_keyword2)
key_df.to_excel('감액배당 나머지 조사 크롤링.xlsx', index = False)