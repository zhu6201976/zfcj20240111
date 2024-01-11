"""
@Time : 2024/01/11 12:18
@Author : Tesla
@File : test.py
@Software: PyCharm
@Csdn : https://blog.csdn.net/zhu6201976
"""
import base64
import re

import execjs
import requests
from loguru import logger
from scrapy import Selector


class Test(object):
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' +
                                                   ' (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        self.host_name = base64.b64decode('aHR0cDovL3pmY2ouZ3ouZ292LmNu').decode('utf-8')
        self.url1 = base64.b64decode(
            'aHR0cDovL3pmY2ouZ3ouZ292LmNuL3pmY2ovZnl4eC94a2I/c1Byb2plY3RJZD05MzBlMDQ0MmJjNjA0MTBkYTgzNzQ0MmQ5ZGRiN2UwMiZzUHJlU2VsbE5vPTIwMjQwMDA1').decode(
            'utf-8')
        self.url2 = base64.b64decode('aHR0cDovL3pmY2ouZ3ouZ292LmNuL3pmY2ovZnl4eC94bXhrYnh4Vmlldw==').decode('utf-8')
        self.ctx = execjs.compile(self.read_js_code())

    def read_js_code(self):
        with open('./test.js', 'r', encoding='utf-8') as f:
            return f.read()

    def parse_building(self):
        resp = self.session.get(self.url1)
        resp_str = resp.content.decode('utf-8', 'ignore')

        # 提取ak
        search_ak = re.search(r'var ak = "(.+?)";', resp_str)
        ak = search_ak.group(1) if search_ak else ''

        s = Selector(response=resp)
        tr_s = s.xpath('//input[@id="buildingId"]/..')
        logger.info(f'提取到 {len(tr_s)} 楼栋')
        for tr in tr_s:
            building_name = tr.xpath('string(.)').get('').strip()
            buildingId = tr.xpath('./input/@value').get('')

            sProjectId = re.search(r'sProjectId=(.+?)&', self.url1).group(1)
            houseFunctionId = '0'
            unitType = ''
            houseStatusId = '0'
            totalAreaId = '0'
            inAreaId = '0'
            token = self.ctx.call('DoSearch', ak, sProjectId, buildingId, houseFunctionId, unitType, houseStatusId,
                                  totalAreaId, inAreaId)
            data = {
                'sProjectId': sProjectId,
                'token': token,
                'modeID': 1,
                'houseFunctionId': 0,
                'unitType': '',
                'houseStatusId': 0,
                'totalAreaId': 0,
                'inAreaId': 0,
                'buildingId': buildingId
            }
            resp = self.session.post(self.url2, data=data)
            logger.info(f'{building_name} --> {buildingId} --> {token} --> {resp.status_code}')

    def run(self):
        self.parse_building()


if __name__ == '__main__':
    obj = Test()
    obj.run()
