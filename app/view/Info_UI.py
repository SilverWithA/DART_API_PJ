class Info_view():
    def __init__(self):
        pass

    def show_xml_info(self, country):
        print("회사명: ", country.findtext("corp_name"))
        print("종목코드: ", country.findtext("stock_code"))
        print("고유번호: ", country.findtext("corp_code"))
        print()
    def print_start_UI(self, content):
        print(f"{content} 작업을 시작합니다. ---")

    def print_end_UI(self, content):
        print(f"{content}작업을 마쳤습니다. ---")

    def print_res_UI(self,content):
        print(f"{content}를 저장햇습니다. ---")