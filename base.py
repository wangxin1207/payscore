#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020-03-25
# @Author  : Logan

import base64
import json
import os
import random
import string
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography import x509
import requests
import settings


class BaseWeiXinPayScore(object):
    """
        支付分免密支付
    """

    def __init__(self):
        self.auth_type = settings.AUTH_TYPE
        self.url = settings.URL_PREFIX

        self.mch_id = settings.MCH_ID
        self.api_v3_key = settings.API_V3_KEY
        self.client_key = settings.CLIENT_KEY
        self.serial_no = settings.SERIAL_NO
        self.cert_path = settings.CERT_PATH

    @staticmethod
    def get_nonce_str(num=32):
        """
            生成随机字符串
        :param num: 字符串长度
        :return:
        """
        nonce_str = ''.join([random.choice(string.ascii_letters) for _ in range(num)])
        return nonce_str

    @staticmethod
    def get_timestamp():
        """
            获取当前时间时间戳
        :return:
        """
        return str(int(time.time()))

    def _make_signature(self, method, url, nonce_str, timestamp, body):
        """
            计算签名值
        :param method: HTTP请求的方法
        :param url: 获取请求的绝对url
        :param nonce_str: 请求随机串
        :param timestamp: 当前时间戳
        :param body: 请求报文主体，method=="GET"为空
        :return: 进行base64编码的签名值
        """
        # 构造签名串
        sign_str = '\n'.join([method, url, timestamp, nonce_str, body]) + '\n'

        with open(self.client_key, "rb") as f:
            private_key_data = f.read()

        # 获取私钥
        private_key = serialization.load_pem_private_key(
            private_key_data,
            password=None,
            backend=default_backend()
        )

        # 私钥SHA256签名
        signature = private_key.sign(
            sign_str.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return bytes.decode(base64.b64encode(signature))

    def _make_headers(self, nonce_str, timestamp, signature):
        """
            构造请求头
        :param nonce_str: 请求随机串
        :param timestamp: 当前时间戳
        :param signature: 签名
        :return:
        """
        # 构造auth头部，注意value必须用双引号
        auth = self.auth_type + \
               ' mchid="{}",'.format(self.mch_id) + \
               'nonce_str="{}",'.format(nonce_str) + \
               'signature="{}",'.format(signature) + \
               'timestamp="{}",'.format(timestamp) + \
               'serial_no="{}"'.format(self.serial_no)
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        return headers

    def get_public_key(self, serial):
        """
            根据证书编号获取公钥信息
        :param serial: 证书编号（微信平台证书） ！= 商户API证书
        :return: 公钥
        """

        with open(self.cert_path.format(serial), "rb") as f:
            cert_data = f.read()

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        return cert.public_key()

    def generate_certificates(self, response):
        """
            根据返回信息生成证书
        :return:
        """
        body = json.loads(response.text)["data"]
        aesgcm = AESGCM(self.api_v3_key.encode())
        for i in body:
            serial_no = i["serial_no"]
            encrypt_certificate = i["encrypt_certificate"]
            algorithm = encrypt_certificate["algorithm"]
            nonce = encrypt_certificate["nonce"]
            associated_data = encrypt_certificate["associated_data"]
            ciphertext = encrypt_certificate["ciphertext"]

            cert = aesgcm.decrypt(nonce.encode(), base64.b64decode(ciphertext), associated_data.encode())

            with open(self.cert_path.format(serial_no), "wb") as f:
                f.write(cert)

    def verify_sign(self, response):
        """
            验证应答签名
        :return:
        """
        weixin_serial = response.headers["Wechatpay-Serial"]  # 微信平台证书序列号
        verify_sign = base64.b64decode(response.headers["Wechatpay-Signature"])
        verify_nonce = response.headers["Wechatpay-Nonce"]
        verify_time = response.headers["Wechatpay-Timestamp"]
        verify_data = verify_time + "\n" + verify_nonce + "\n" + response.text + "\n"

        if not os.path.exists(self.cert_path.format(weixin_serial)):
            self.generate_certificates(self.get_certificates())

        public_key = self.get_public_key(weixin_serial)

        # 签名验证失败会触发名为exceptions.InvalidSignature
        public_key.verify(
            verify_sign,
            verify_data.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

    def _make_request(self, method, url, body=''):
        nonce_str = self.get_nonce_str(32)
        timestamp = self.get_timestamp()
        signature = self._make_signature(method, url, nonce_str, timestamp, body)
        headers = self._make_headers(nonce_str, timestamp, signature)
        url = self.url + url
        if method == "GET":
            request = requests.get(url, headers=headers)
        else:
            request = requests.post(url, headers=headers, data=body)

        if request.status_code != 200:
            raise PayScoreException(request)

        # 微信支付平台公钥对验签名串和签名进行SHA256 with RSA签名验证
        # 微信建议验证，可关闭
        self.verify_sign(request)

        return request

    def get_certificates(self):
        """
            获取平台证书
        :return:
        """
        url = "/v3/certificates"
        result = self._make_request("GET", url)
        return result


class PayScoreException(Exception):

    def __init__(self, request):
        super().__init__()
        self.status_code = request.status_code
        self.error_msg = request.text

    def __str__(self):
        return '[{}] {}'.format(self.status_code, self.error_msg)
