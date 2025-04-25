### (new)MVC 구조로 리팩토링
### project_DART 파일트리
|MVC레벨|모듈명|설명|
|------|---|---|
|controller|||
|model|Info_API_collector|기본 정보를 불러오는 모델|
|model|Director_API_collector|임원 현황을 불러오는 모델|
|model|statement_API_collector|재무제표를 불러오는 모델|

## Model
## Info_collerctor.py
### (1) xml_info_finder: 기본정보를 불러오는 클래스

|클래스|매서드|매서드 설명|
|------|---|---|
|xml_info_finder||[기업개황](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019002) 내에 있는 기본정보를 불러오는 클래스 |
||추가필요|xml 파일최신 정보로 업데이트하는 클래스|
||get_corpcode_by_name|xml파일 기반 회사명으로 고유번호 찾기|
||apply_corpcode_by_name|찾은 정보를 기반으로 '고유번호' 컬럼 추가하기|
||get_corpcode_by_stock|xml파일 기반 종목코드로 고유번호 찾기|
||apply_get_corpcode_by_stock|찾은 정보를 기반으로 '고유번호' 컬럼 추가하기|
||print_Info_by_name|xml파일 기반 종목코드로 회사명 출력 보기|
||print_Info_by_stock|xml파일 기반 회사명으로 기본정보 출력 보기|
||print_Info_by_corpcode|xml파일 기반 고유번호로 기본정보 출력 보기|

### (2) API_info_collector: API를 통해 직접 기본정보에 관한 사항을 불러오는 클래스
|클래스|매서드|설명|
|------|---|---|
|API_info_collector|---|API를 통해 직접 기본정보에 관한 사항을 불러오는 클래스|
||get_jurir_no|고유번호를 통해 법인등록번호를 찾기|
||apply_jurir_no|찾은 정보를 기반으로 '법인등록번호' 컬럼 추가하기|
||is_equal_jurir_no|기존 법인등록번호와 불러온 정보가 일치하는지 확인|
||추가필요|고유번호를 기반으로 기간내 제출한 사업보고서 리스트를 가져오기|
||추가필요|사업보고서를 제출하는 유일한 고유번호만 남기기|
||추가필요|사업보고서 제출여부를 확인하여 '사업보고서 제출' 컬럼 만들기|
||추가필요|유효하다고 판단되는 컬럼만 데이터프레임에 남기기|



## Controller
### 기본정보 조회 클래스
|No|매서드|비고|
|------|---|---|
|1|고유번호 조회 매서드|유효성 검증 매서드 => 최근 1년간 대규모기업집단현황 공시有면 유효로 검증|
|2|종목코드 조회 매서드|진행예정|
|3|KRX기준 종목코드 보충 매서드|dart기준과 경합시 krx기준으로 대체|
|4|사업보고서 제출 여부 확인 매서드|상위 클래스 정의하여 상속하여 사용할 것|


### DartDirectorsInfo: 임원현황 조회 클래스
|No|매서드|비고|
|------|---|---|
|1|등기임원 조회 매서드|API이용|
|2|미등기임원 조회 매서드|크롤링 방식으로 진행|




-----------------------------------------------------
### [데이터 작업 플로우 관련]
## Database 연결 플로우
* 데이터베이스 제품 선택 - mysql로 테스트
* archive_yyyy Database 생성
* 11월 이후 작업한 최종 데이터 업데이트

* 500대기업 및 88개 대규모기업집단 계열사 정보 DATABASE에 업로드
* DATABASE 테스트버전과 파이썬 연동하여 구축

## 오케스트레이션을 통한 자동화 구축
* python으로 자동화 플로우 구축하기
* airflow 혹은 dagster 등 오케스트레이션을 통한 자동화 구축
  


