import unittest
from app.model.Info_API_collecter import Info_API_Collecter


class TestInfoAPICollecter(unittest.TestCase):
    def setUp(self):
        self.collector = Info_API_Collecter()

        # 테스트용 dummy XML 데이터 설정
        from xml.etree.ElementTree import fromstring
        dummy_xml = fromstring('''
        <root>
            <list>
                <corp_name>삼성전자</corp_name>
                <stock_code>123456</stock_code>
                <corp_code>005930</corp_code>
            </list>
            <list>
                <corp_name>삼성전자</corp_name>
                <corp_code>123456</corp_code>
            </list>
            <list>
                <corp_name>LG전자</corp_name>
                <stock_code>985412</stock_code>
                <corp_code>066570</corp_code>
            </list>
        </root>
        ''')

        # config 값을 직접 오버라이드 (또는 mock)
        self.collector.corp_code_xml = dummy_xml


    # get_corpcode_by_name 테스트
    def test_get_corpcode_by_name_multiple_results(self):
        result = self.collector.get_corpcode_by_name("삼성전자")
        self.assertEqual(result, ["005930", "123456"])

    def test_get_corpcode_by_name_single_result(self):
        result = self.collector.get_corpcode_by_name("LG전자")
        self.assertEqual(result, "066570")

    def test_get_corpcode_by_name_no_result(self):
        result = self.collector.get_corpcode_by_name("한화")
        self.assertIsNone(result)


    # get_corpcode_by_stock 테스트
    def test_get_corpcode_by_stock_results(self):
        result = self.collector.get_corpcode_by_stock("123456")
        self.assertEqual(result, "005930")

    def test_get_corpcode_by_stock_no_result(self):
        result = self.collector.get_corpcode_by_stock("468521")
        self.assertIsNone(result)


    # get_jurir_no 테스트
    def test_get_jurir_result(self):
        result = self.collector.get_jurir_no("00126380")    # 삼성전자 고유번호
        self.assertEqual(result, "1301110006246")

    def test_get_jurir_no_result(self):
        result = self.collector.get_jurir_no("1234567")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
