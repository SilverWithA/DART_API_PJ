# 공시보고서에서 직접 정보를 크롤링할때 사용하는 매서드
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class E006_Kwd_Searcher():
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # 백그라운드 실행
        self.chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
        self.chrome_options.add_argument("--window-size=1920x1080")  # 화면 해상도 설정
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 2)

    def 접수번호로_보고서열기(self, rept_no):
        self.driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")

    def 공시보고서_팝업닫기(self):
        # btnClose 버튼을 기다리기
        close_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btnClose")))

        # 팝업 닫기 클릭
        close_button.click()

    def 특정이름_목차요소들_가져오기(self):

        # 주주총회소집공고 혹은 주주총회 소집공고라고 표기된 목차 가져오기
        idx_elements = self.wait.until(EC.presence_of_all_elements_located((
            By.XPATH,
            "//a[normalize-space(text())='주주총회소집공고' or normalize-space(text())='주주총회 소집공고']"
        )))
        return idx_elements

    def 특정목차요소_선택(self, target_index_elements,i):
        elem = target_index_elements[i]
        self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        elem.click()

    def iframe_선택후전환(self):

        # DART 공시보고서에서는 ifrme내에 데이터가 위치함

        # iframe 요소 로딩까지 기다림
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "ifrm"))
        )

        # 전환
        self.driver.switch_to.frame(iframe)

    def 키워드매칭(self,keywords):

        # body 아래 위치한 텍스트 가져오기
        text = self.driver.find_element(By.TAG_NAME, "body").text

        # 해당 text 아래 원하는 키워드가 있는지 확인
        matched_keyword = next((k for k in keywords if k in text), None)

        if matched_keyword:
            self.driver.quit()
            return matched_keyword
        else:
            self.driver.switch_to.default_content()






