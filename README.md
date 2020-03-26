## 声明
写这块逻辑时，微信那边给的接口文档还是内测版本，于2020/3/25获取到最新文档

base.py中的签名生成、验证、回调报文解密、敏感信息加密等功能正常

query_contract.py中签约查询接口未变，已进行单元测试

create_order.py中创建订单参数改变，未进行单元测试

查询、取消、完结等接口请求大同小异，可自行参考文档 https://wechatpay-api.gitbook.io/wechatpay-api-v3/

后期开发微信支付分免密支付时遇到难以理解处理的可联系 logan.wangxin@gmail.com

## 声明所使用的证书
1.商户签名使用商户私钥，证书序列号包含在请求HTTP头部的Authorization的serial_no

2.微信支付签名使用微信支付平台私钥，证书序列号包含在应答HTTP头部的Wechatpay-Serial

3.商户上送敏感信息时使用微信支付平台公钥加密，证书序列号包含在请求HTTP头部的Wechatpay-Serial

商户私钥在商户申请商户API证书时会自动生成

微信平台证书需要通过接口获取，微信支付平台公钥从微信平台证书中获取
