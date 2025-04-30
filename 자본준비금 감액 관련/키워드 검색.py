## 공시보고서 내 특정 키워드가 존재하면 체크해주는 기능

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from urllib3.util.proxy import connection_requires_http_tunnel

# 1. ChromeOptions 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
chrome_options.add_argument("--window-size=1920x1080")  # 화면 해상도 설정

# 접수번호로 검색
import pandas as pd
from tqdm import tqdm
import re
tqdm.pandas()
key_df = pd.read_excel('상장사 감액배당 실태조사_20250428_v1 (2).xlsx', sheet_name='2023_part2',dtype=str)
# key_df = pd.read_excel('2023년 상장사 주총공고.xlsx',dtype=str)
error_rept_list = []

# rept_no = '20250317000669' # 테스트용 접수번호

# 의안 항목에 해당 키워드 있는지 확인
key_word_1 = "자본준비금"
key_word_2 = "자본잉여금"
key_word_3 = "전입"
key_word_4 = "감소"
key_word_5 = "감액"

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

                    if any(k in text for k in [key_word_1, key_word_2, key_word_3, key_word_4, key_word_5]):
                        driver.quit()
                        return text
                        # print("있다")

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

key_df_head = key_df.head(3)
key_df['자본준비금 감액'] = key_df['rcept_no'].progress_apply(find_keywords)
key_df.to_excel('2023 part2 자본준비금 감액 표기.xlsx', index=False)

res = find_keywords(rept_no)
