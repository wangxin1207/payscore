#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020-03-25
# @Author  : Logan

import json
from urllib.parse import urlencode
import settings
from base import BaseWeiXinPayScore


class PayScoreQueryContract(BaseWeiXinPayScore):
    """
        @ApiName 签约查询
        @ApiParam
            {str} openid 微信用户在商户对应appid下的唯一标识。
            {str} appid 微信公众平台分配的与传入的商户号建立了支付绑定关系的appid，可在公众平台查看绑定关系，此参数需在本系统先进行配置。
            {str} service_id 该服务ID有本接口对应产品的权限。
    """
    
    def __init__(self):
        super(PayScoreQueryContract, self).__init__()
        self.openid = settings.OPEN_ID
        self.app_id = settings.APP_ID
        self.service_id = settings.SERVICE_ID

    def run(self):
        params = {
            "service_id": self.service_id,
            "appid": self.app_id,
            "openid": self.openid
        }
        url = "/payscore/user-service-state" + "?" + urlencode(params)
        result = self._make_request("GET", url)

        return json.loads(result.text)["use_service_state"]  # UNAVAILABLE：用户未授权服务 AVAILABLE：用户已授权服务


if __name__ == '__main__':
    pay = PayScoreQueryContract()
    print(pay.run())
