"""Local API credentials for exchanges.
This file is gitignored; manage sensitive keys here.

API 使用指引
================

1. Binance API
   - 必需: API_KEY + SECRET_KEY (建议将读取和交易权限分离)
   - REST 基础 URL: https://api.binance.com (现货) / https://fapi.binance.com (合约)
   - Header: {'X-MBX-APIKEY': BN_API_KEY_ACCOUNT2}
   - 必备参数: `timestamp` (毫秒 UTC, 服务器允许±5000ms) + 可选 `recvWindow` + `signature`
   - 签名: 对完整 query string 使用 HMAC-SHA256(secret)，结果转 hex 追加为 `signature`
   - GET 账户余额流程: 构造 query={'timestamp': epoch_ms(), 'recvWindow': 5000}; 计算签名后请求 `/api/v3/account`
   - POST 下单流程: 参数同 GET；body 采用 `application/x-www-form-urlencoded`; 接口 `/api/v3/order`
   - WebSocket 私有频道需先通过 REST 获取 listenKey，再使用 `wss://stream.binance.com:9443/ws/<listenKey>`

2. OKX API
   - 必需: API_KEY + SECRET_KEY + PASSPHRASE
   - REST 基础 URL: https://www.okx.com; 私有 WS: wss://ws.okx.com:8443/ws/v5/private
   - Headers 必须包含: `OK-ACCESS-KEY`, `OK-ACCESS-SIGN`, `OK-ACCESS-TIMESTAMP`, `OK-ACCESS-PASSPHRASE`, `Content-Type: application/json`
   - Timestamp: ISO-8601 字符串，建议使用 `/api/v5/public/time` 校时，容差 ±30 秒
   - 签名: message = f"{timestamp}{method.upper()}{requestPath}{body or ''}"; sign = Base64(HMAC-SHA256(secret, message))
   - GET 账户余额: requestPath = '/api/v5/account/balance'; body=''
   - POST 下单: body 为 JSON 字符串; 签名 message 最后拼接 body；WS 登录 payload 同样使用 sign/timestamp/passphrase

3. Bybit API
   - 必需: API_KEY + SECRET_KEY
   - REST 基础 URL: https://api.bybit.com; 私有 WS: wss://stream.bybit.com/v5/private
   - Headers: `X-BAPI-API-KEY`, `X-BAPI-SIGN`, `X-BAPI-TIMESTAMP`, `X-BAPI-RECV-WINDOW`
   - Timestamp: 毫秒 UTC；默认 `recv_window` 5000，可根据需要调整 (上限 50000)
   - 签名字符串: f"{timestamp}{api_key}{recv_window}{body}" (GET 时 body 为空字符串)；结果为 hex HMAC-SHA256(secret, payload)
   - GET 账户 info: endpoint '/v5/account/balance'; 将 `category`, `coin` 等参数写入 query/body 并加入签名
   - POST 下单: body 使用 JSON 字符串; `Content-Type: application/json`; WebSocket 登录参数与 REST 相同字段

4. Bitget API
   - 必需: API_KEY + SECRET_KEY + PASSPHRASE
   - REST 基础 URL: https://api.bitget.com; 私有 WS: wss://ws.bitget.com/v2/ws/private
   - Headers: `ACCESS-KEY`, `ACCESS-PASSPHRASE`, `ACCESS-TIMESTAMP`, `ACCESS-SIGN`, `Content-Type: application/json`
   - Timestamp: ISO-8601 字符串，官方容差 ±30 秒；推荐使用 `/api/spot/v1/public/time` 校对
   - 签名字符串: f"{timestamp}{method.upper()}{requestPath}{queryString}{body}"，其中 queryString 需包含 `?`；签名 = Base64(HMAC-SHA256(secret, payload))
   - GET 账户余额: requestPath = '/api/mix/v1/account/accounts'; queryString 包含产品线参数；body 为空
   - POST 下单: body 为 JSON 字符串; keepalive WS 登录字段与 REST 相同

通用注意事项
- 统一使用 UTC 时间并保持与交易所服务器同步 (建议每分钟校时)
- REST POST 默认使用 UTF-8 JSON 或 form data，必须与签名 payload 完全一致
- 签名前去除多余空格/换行；任何参数顺序或大小写错误都会导致 `signature not valid`
- 建议将下单与查询逻辑封装成辅助函数，以确保 timestamp/签名/headers 一致性
"""

BN_API_KEY_ACCOUNT2 = "p7naeu7TuhLxb252vBCzVXfdj6ArYgzWXtab13kzUp7EfEp7NXQDIJyxNlUmtVRx"
BN_SECRET_KEY_ACCOUNT2 = "GrNYlbAN4FumOpafwm02p8FaPepPMVrX8lJBZl725b8J6MnYTAP8rmyH8W2MCTSV"

OKX_API_KEY_JERRYPSY = "c1a964b1-f0be-4f2b-acb3-beac6b1ab7a3"
OKX_SECRET_KEY_JERRYPSY = "213417CA5F584406256FD910C5D724A4"
OKX_PASSPHRASE_JERRYPSY = "quantech20241207JERRY!"

BYBIT_API_KEY_ACCOUNT18810813576 = "kAK9hRVLRlFUOuJRTO"
BYBIT_SECRET_KEY_ACCOUNT18810813576 = "nOsUZK1Gxw6Lg8GewGdnKp04UFkWPOC018it"

BITGET_API_KEY_ACCOUNT18810813576 = "bg_3bb9b595dfb19c36d055d3698ad3ceb0"
BITGET_SECRET_KEY_ACCOUNT18810813576 = "8d2e1c7171e3bef5aeff886919e8297234519d7e287d9f1b2bce09e5992cff88"
BITGET_PASSPHRASE_ACCOUNT18810813576 = "quantech20241207JERRY"

# GRVT credentials for market data ingestion
GRVT_FUNDING_ACCOUNT_ADDRESS="0x59fdd25cfdd7a7038dbaf8634495c803a78a920f"
GRVT_API_KEY = "35Uv14uM7Ncz8oYuwkPrQv1tGgo"
GRVT_SECRET_KEY = "0xcfb15ae26781cbef74e7be222cadd694ce0f7b8e2964acea8f186aceda1024ce"
GRVT_TRADING_ACCOUNT_ID = "3058150716424287"
GRVT_ENVIRONMENT = "prod"

# LIGHTER 交易所
LIGHTER_NAME = "OKX-钱包A API"
LIGHTER_KEY_INDEX= "4"
LIGHTER_PUBLIC_KEY="14bf4cce6aa8daa85917becb244c6b569268c94a86c09f20a34a410137851af4b834d2cf9d3a5e16"
LIGHTER_PRIVATE_KEY="c8341f1346e110808ea496f398cfdb3c26cca99ba7b65b5f96ca680597842fcb820cef53bbf5a817"
LIGHTER_ACCOUNT_INDEX = 131771

# hyperliquid的密钥 hyperliquid
HYPERLIQUID_ACCOUNT="18810813576@163.com"
# HYPERLIQUID_WALLET_NAME="jerry01-hyperl"
HYPERLIQUID_WALLET_NAME="api-0221"
# HYPERLIQUID_WALLET_ADDRESS="0x4a3bbC5923048B7F6f52Eab473e2D236C3ACD1C1"
HYPERLIQUID_WALLET_ADDRESS="0xfBa8a4166B814D344955Dc18907533d8aEc06558"
# HYPERLIQUID_PRIVATE_KEY="0x45a1e6785954d05ad519b1f1a5fd304860ca5752e2df285c618b6384862d4aea"
HYPERLIQUID_PRIVATE_KEY="0x459b7185790e928848b17fabefcea92604596b1e38a4dad7eead2c5b2033ff91"
HYPERLIQUID_USER_ADDRESS="0x39d116F425E451184bDA6937690e3eF0BDd8eC50"



LIVE_TRADING_SPOT_ENABLED="1"
LIVE_TRADING_SPOT_ALLOWED_EXCHANGES="okx,binance,bybit,bitget"
LIVE_TRADING_SPOT_PER_LEG_NOTIONAL="50"

# Binance SOCKS5 proxy (REST + WS)
BINANCE_PROXY_URL = "socks5h://47.79.224.99:1080"
BINANCE_WS_PROXY_URL = "socks5h://47.79.224.99:1080"

# 8010 watchlist keepalive TTL (seconds)
MONITOR_8010_WL_TTL = "3600"
# FR_Monitor -> 8010 HTTP timeout (seconds)
MONITOR_8010_TIMEOUT_SEC = "8"
