# 认证类型
AUTH_TYPE = 'WECHATPAY2-SHA256-RSA2048'

# 请求url prefix
URL_PREFIX = 'https://api.mch.weixin.qq.com'

# 支付密钥路径
CLIENT_KEY = 'client_key/apiclient_key.pem'

# 微信支付平台证书路径
CERT_PATH = 'cert/{}.pem'

# 商户号
MCH_ID = ''

# APIv3密钥,不同于API密钥，需要单独配置
API_V3_KEY = ''

# 商户私钥证书序列号
SERIAL_NO = ''

# 微信用户在商户对应appid下的唯一标识。
OPEN_ID = ''

# 微信公众平台分配的与传入的商户号建立了支付绑定关系的appid，可在公众平台查看绑定关系，此参数需在本系统先进行配置。
APP_ID = ''


# 该服务ID有本接口对应产品的权限。
SERVICE_ID = ''
