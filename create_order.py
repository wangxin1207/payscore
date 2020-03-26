#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020-03-25
# @Author  : Logan
import datetime
import json
import struct

from bson import ObjectId

import settings
from base import BaseWeiXinPayScore


class PayScoreCreateOrder(BaseWeiXinPayScore):
    """
        @ApiName 创建订单
        @ApiParam
            {str} out_order_no 商户系统内部服务订单号（不是交易单号），要求此参数只能由数字、大小写字母_-|*组成，且在同一个商户号下唯一
            {str} appid 微信公众平台分配的与传入的商户号建立了支付绑定关系的appid，可在公众平台查看绑定关系，此参数需在本系统先进行配置。
            {str} service_id 该服务ID有本接口对应产品的权限。
            {str} service_introduction 服务信息，用于介绍本订单所提供的服务 ，当参数长度超过20个字符时，报错处理
            {str} notify_url 商户接收用户确认订单和付款成功回调通知的地址。
            {str} openid 微信用户在商户对应appid下的唯一标识。 免确认订单：必填 需确认订单：不填
            {bool} need_user_confirm 枚举值：false：免确认订单 true：需确认订单

            {object} risk_fund 订单风险金信息
                {str} name 枚举值：【先免模式】（评估不通过可交押金）可填名称为 DEPOSIT：押金 ADVANCE：预付款 CASH_DEPOSIT：保证金
                                  【先享模式】（评估不通过不可使用服务）可填名称为 ESTIMATE_ORDER_COST：预估订单费用
                {int} amount 风险金额 单位为分
                {str} [description] 风险说明

            {object} time_range 服务时间范围
                {str} start_time 用户下单时确认的服务开始时间  支持三种格式：yyyyMMddHHmmss、yyyyMMdd和 OnAccept
                                                            ● 传入20091225091010表示2009年12月25日9点10分10秒。
                                                            ● 传入20091225默认认为时间为2009年12月25日
                                                            ● 传入OnAccept表示用户确认订单成功时间为【服务开始时间】。
                {str} [start_time_remark] 服务开始时间备注说明
                {str} [end_time] 预计服务结束时间  若传入时间精准到秒，则校验精准到秒：
                                                    1）【预计服务结束时间】>【服务开始时间】
                                                    2）【预计服务结束时间】>【商户调用接口时间+1分钟】
                                                 2、若传入时间精准到日，则校验精准到日：
                                                    1）【预计服务结束时间】>=【服务开始时间】
                                                    2）【预计服务结束时间】>=【商户调用接口时间】
                {str} [end_time_remark] 预计服务结束时间备注说明
    """

    @staticmethod
    def get_out_order_no():
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '%.10d' % int(str(struct.unpack('>Q', ObjectId().binary[-8:])[0])[-10:])

    def __init__(self):
        super(PayScoreCreateOrder, self).__init__()
        self.out_order_no = self.get_out_order_no()
        self.openid = settings.OPEN_ID
        self.app_id = settings.APP_ID
        self.service_id = settings.SERVICE_ID
        self.service_introduction = u'智慧零售'
        self.notify_url = ''
        self.need_user_confirm = False

    def get_params(self):
        params = {
            "out_order_no": self.out_order_no,
            "appid": self.app_id,
            "service_id": self.service_id,
            "service_introduction": self.service_introduction,
            "notify_url": self.notify_url,
            "openid": self.openid,
            "need_user_confirm": self.need_user_confirm,
            "risk_fund": {
                "name": "ESTIMATE_ORDER_COST",
                "amount": 20000
            },
            "time_range": {
                "service_start_time": "OnAccept"
            }
        }
        return json.dumps(params)

    def run(self):
        url = "/payscore/smartretail-orders"
        self._make_request("POST", url, self.get_params())


if __name__ == '__main__':
    order = PayScoreCreateOrder()
    order.run()

