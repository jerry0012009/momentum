# 2026-04-20 14:05 UTC — bot3 fresh intake first verdict: EMA cross × volume confirmation × bracket exit pocket

## 当前小点
- target: `research/quant_digests/2026-04-19_1712_emacross-volume-bracket-pocket-alpha.md`
- action: conditional fresh intake first verdict
- 最小 blocker: 成交量确认后的 EMA cross bracket TP/SL 是否在 next-bar entry、固定 stop/TP、统一成本梯度与 TIME exit / 月份 / 资产切片 realism 后仍保留独立 after-cost pocket。

## 读取的原始证据
- Digest 给出的原始 15m probe（近 120d，8 liquid majors，6bps roundtrip）显示：
  - `ALL_EQ`: `88` 笔，`avg_net_bps≈+0.35`，整体只是贴线。
  - `BTCUSDT`: `14` 笔，`avg_net_bps≈+61.10`。
  - `ETHUSDT`: `7` 笔，`avg_net_bps≈+31.12`。
  - `SOL/XRP/AVAX` 明显为负。

## 本轮最小 honesty 复核
我没有扩展成第二个小点，只把原 probe 口径压到本轮 success criterion 要求的最小 honesty：
- next-bar entry 保持不变；
- 固定 `2% stop / 4% TP / 64-bar timeout` 保持不变；
- 成本统一改为 `8bps` roundtrip；
- 输出 `BTC/ETH/SOL/core3/majors8`、月份切片与 TIME exit rate。

关键结果：

```text
BUCKET ALL n=88 avg_net8_bps=-1.81 time_rate=0.523
BUCKET CORE3 n=33 avg_net8_bps=16.77 time_rate=0.606
BUCKET BTC n=14 avg_net8_bps=59.10 time_rate=0.714
BUCKET ETH n=7 avg_net8_bps=29.12 time_rate=0.571
BUCKET SOL n=12 avg_net8_bps=-39.80 time_rate=0.500
SYMBOL XRPUSDT n=17 avg_net8_bps=-29.46
SYMBOL AVAXUSDT n=8 avg_net8_bps=-50.05
MONTH ALL 2025-12 n=10 avg_net8_bps=-6.11
MONTH ALL 2026-01 n=28 avg_net8_bps=-13.20
MONTH ALL 2026-02 n=17 avg_net8_bps=-46.91
MONTH ALL 2026-03 n=13 avg_net8_bps=16.34
MONTH ALL 2026-04 n=20 avg_net8_bps=42.84
MONTH ETHUSDT 2026-01 n=3 avg_net8_bps=-101.50
MONTH SOLUSDT 2026-04 n=2 avg_net8_bps=-155.01
```

## Verdict
`EMA cross × volume confirmation × bracket exit pocket` 的 fresh intake first verdict 直接收口为 `background/P0`。

原因：
1. `8bps` 后 majors8 全样本已经转负（`avg_net8≈-1.81bps/trade`），不满足独立 broad-book alpha。
2. 正边际主要来自 BTC 与少量 ETH 样本；`SOL/XRP/AVAX` 是稳定拖累，不满足 BTC/ETH/SOL/majors 分层稳定。
3. 月份切片不稳：`2026-01/02` 明显为负，最近转正不足以抹掉前段负 regime。
4. TIME exit rate 高（ALL `52.3%`，BTC `71.4%`，ETH `57.1%`），显示 bracket TP/SL 并没有形成足够快的兑现路径；正收益更像少数趋势段和宽 bracket 的选择性暴露。

## Runtime update
- Fresh intake slot 仍保留当前 state 的 slot 对象不重排；仅写入本小点结论。
- Background pool 追加本对象为 latest parked。
- cycle_plan 第 2 项写为 `done`，result 为一句会改变系统认知的话。
