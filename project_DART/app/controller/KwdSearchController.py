# 공시보고서 내 키워드 검색관련 컨트롤러
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from app.model.Raw_repot_crawler import E006_Kwd_Searcher

class KwdSearchController():
    def __init__(self):
        self.E006_md = E006_Kwd_Searcher()

    # 🔥 백그라운드 모드로 실행시 에러 발생 -> 에러 해결 안됐으므로 사용 유의
    def 주주총회의안_키워드검색하기(self, rept_no):
        keywords = ["자본준비금", "자본잉여금", "전입", "감소", "감액"]


        # chrome에서 공시보고서 열기
        self.E006_md.접수번호로_보고서열기(rept_no)

        # 팝업 닫기
        try:
            self.E006_md.공시보고서_팝업닫기()
        except:
            pass

        # 특정 제목을 가진 목차 목록 가져오기
        target_index_elements = self.E006_md.특정이름_목차요소들_가져오기()
        target_idx_cnt = len(target_index_elements)


        for i in range(target_idx_cnt):
            try:
                # 리스트 매번 가져오기
                target_index_elements = self.E006_md.특정이름_목차요소들_가져오기()

                # 인덱스 유효성 체크
                if i >= len(target_index_elements):
                    break

                self.E006_md.특정목차요소_선택(target_index_elements, i)

                time.sleep(1)

                self.E006_md.iframe_선택후전환()

                is_keywords = self.E006_md.키워드매칭(keywords)
                if is_keywords:
                    return is_keywords


            except Exception as e:
                print(f"[ERROR] 루프 중 예외 발생: {e}")
                continue

    # 작업 미완상태
    def 현금배당보고서_검색하기(self,rept_no):
        keywords = ["준비금", "재원", "과세", "비과세"]

        self.E006_md.접수번호로_보고서열기(rept_no)

        self.E006_md.iframe_선택후전환()










