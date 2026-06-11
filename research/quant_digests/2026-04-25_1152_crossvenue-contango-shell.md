# 别把这个 KRW premium 平台只读成“韩国搬砖工具”：对 short-cycle crypto desk，更该先拆的是「cross-venue cheap-spot × rich-perp contango capture」这条完整 raw alpha 壳
- 时间：2026-04-25 11:52 UTC
- 类型：GitHub / repo source audit
- 主题类型：raw alpha
- 基础 alpha：当不同交易所之间出现“最便宜现货 + 最贵永续”组合，且 perp 相对 spot 的 contango 足够厚时，做 **long cheap spot / short rich perp**，赌跨 venue 升贴水回归或至少不继续恶化
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但默认阈值仍需先过成本关）
- 主题标签：relative-value / stat-arb / carry / basis / cross-venue / spot-perp / delta-neutral / contango / funding / 1m / 3m / 5m / repo
- 证据类型：工程经验 / repo 规则壳

## 1. 这次看了什么
这次看的是 2026 GitHub repo **sueun-dev / crypto-market-neutral-platform**。表面上它更像“韩国上币溢价 + 海外对冲平台”，但对我们 desk 更值钱的读法不是跨境转币，而是先把里面那条 **overseas-only cross-venue contango shell** 单独拆出来：跨所找最便宜 spot、最贵 perp，满足阈值就做 delta-neutral 收敛。

## 2. 一句话核心结论
这份仓最值得留下来的不是“韩国溢价故事”，而是：**它把 cross-venue spot-perp contango capture 写成了可执行的完整策略壳；但当前默认 `PRICE_DIFF_THRESHOLD = 0.15%` 很可能还没厚到能稳定覆盖四腿费用与滑点，所以 first verdict 的第一件事不是回测收益，而是先做 honest fee ladder。**

## 3. 它是怎么证明这点的
不是靠宏大叙事，而是直接把可交易规则写死在配置和流程里：`ENTRY_AMOUNT = 100`、`MAX_ENTRIES = 40`、`PRICE_DIFF_THRESHOLD = 0.0015`、`SLEEP_SEC = 3`、`FUTURES_LEVERAGE = 1`，并且显式写了 **negative funding veto**、现货/永续腿数量对齐、自动/手动模式、真实交易所费率表与退出流程。

## 4. 核心结论展开
- 这篇东西的 **base alpha 很清楚**：不是赌方向，而是赌 **跨 venue 的 spot-perp contango 会回归**。
- repo 给的是完整壳，不只是 scanner：
  - entry：找 `cheapest spot` + `richest perp`，价差超过阈值才进；
  - sizing：默认每次 `100 USDT`、最多 `40` 次分批；
  - risk：`1x` futures、delta-neutral 对齐、负 funding 尽量回避；
  - monitoring：默认 `3s` 轮询；
  - exit：spread 收敛后平仓，韩国腿只是可选增强，不是 base alpha 本体。
- 但 repo 默认阈值和费率一对，马上暴露一个关键问题：
  - `0.15% = 15 bps` 的 admission，放在 cross-venue 四腿交易里并不宽；
  - 仅按 repo `config.py` 费率粗看，**Bybit spot taker `10 bps` + Gate futures taker `5 bps`**，单次开仓就已接近 `15 bps`；
  - 若算 round-trip，粗略就到 **`31 ~ 50 bps+`**（还没含滑点、转账、库存等待），说明它更像 **maker-first / event-driven / premium-enhanced** 的 raw alpha 壳，而不是默认 taker 化就能跑的免费午餐。

## 5. 为什么和当前项目有关
它补的是我们 raw alpha 素材池里一条很实用的 **cross-venue relative-value** 支线，而且和已有“同所 basis fade / funding carry”不完全一样：
- 同所 basis 更像一套 venue 内相对价值；
- 这条是 **跨 venue cheapest-spot / richest-perp 路由**；
- 若直接把韩国转币部分拿掉，它仍然是一个能映射到 `1m / 3m / 5m` 的完整最小实验。

## 5.5 策略拆解（必填）
- 方向属性：relative-value / stat-arb / carry-adjacent
- 基础 alpha：cross-venue spot-perp contango convergence
- regime：contango 为正、且 funding 不恶化到把 edge 吃掉
- filter / veto：negative funding veto、交易所可交易状态、费后 spread 不为正则不做
- risk / sizing / execution overlay：`1x` futures、分批建仓、现货/永续数量精确对齐、优先 maker / 低滑点 venue

## 6. 可复刻的最小实验
### 数据源
- Bybit / OKX / Gate.io 公开 spot ticker / book ticker
- Bybit / OKX / Gate.io 公开 perp ticker / mark / funding
- 公开性：公开可得
- 更新频率：秒级；最小实验可先聚合到 `1m`，再下钻到 `3s~10s`

### 最小实验口径
1. 先只做 `BTC / ETH / SOL`，每 `3s~10s` 抓一次三所 spot 与 perp 报价；
2. 对每个时点算：`best_perp_bid / best_spot_ask - 1 - explicit_fees`；
3. admission 不用 repo 裸 `15 bps`，而是分三档：`15 / 30 / 45 bps`；
4. exit 先用最朴素版本：净 spread 回到 `<= 0`、或 `30/60m` time stop；
5. 先看两件事：`fee-after positive snapshot ratio` 与 `gross/net bps per trade`；
6. 若 majors 不够厚，再转去新币、事件币、韩国上币前后或 funding 异常时段。

## 7. 风险与保留意见
- repo 的最大亮点是工程完整，不是已经证明“默认参数可赚钱”。
- 韩国 premium 变现涉及转账/上币/提现状态，这部分天然更像 **附加增强层**，不是我们 short-cycle 主实验的 base alpha。
- cross-venue 执行会遇到库存分散、到账延迟、maker 不成交、单腿 orphan risk、费率分层变化。
- 所以这条线当前最诚实的定位是：**值得进研究池，但先做 fee-aware admission check，再谈上线。**

## 8. 下一步怎么测
- 先把 repo 的 `0.15%` 改成 **fee-after threshold**，而不是毛价差阈值。
- 做 `maker/taker` 四象限回测：`maker-maker / maker-taker / taker-maker / taker-taker`。
- 把 `negative funding veto` 升级成明确 router：只有 `spread edge > fees + expected funding drag` 才进。
- 观察它更适合哪些场景：平时 majors、事件币、新上币、还是韩国 listing 前后。

## 9. 来源
- GitHub user `sueun-dev` (2026), **crypto-market-neutral-platform**. Repo URL: <https://github.com/sueun-dev/crypto-market-neutral-platform>
- Readable README URL: <https://github.com/sueun-dev/crypto-market-neutral-platform>
- Source audit 文件：`README.md`, `src/overseas_exchange_hedge/config.py`, `src/overseas_exchange_hedge/overseas/price_analyzer.py`, `src/overseas_exchange_hedge/overseas/trade_executor.py`
