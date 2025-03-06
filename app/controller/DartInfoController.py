from app.model import Info_API_collecter

class Company_info_finder():
    def __init__(self):
        self.model = Info_API_collecter()

    # 대규모기업집단 기본 정보
    def get_group_info(self):
        self.model.get_corpcode_by_name()

    # 500대기업 기본 정보
    def get_company_info(self):
        pass


