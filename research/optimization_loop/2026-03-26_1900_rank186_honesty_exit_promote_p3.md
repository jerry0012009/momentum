# Rank 186 / CME expiry postfix short BTC — P2 exit decision promote_P3（honesty / execution realism）
- 时间：2026-03-26 19:00 UTC
- 对象：`Rank 186 / CME expiry postfix short BTC`
- 本轮角色：bot3 对 `Active P2` 做出口决策轮，只围绕唯一剩余的 `honesty / execution realism` blocker 做最小 decisive check，并直接回答 `promote_P3 / one-time P2->P1 re-scope / drop_to_background`

## 结论
**单一出口 verdict：`promote_P3`。**

更具体地说，当前更诚实的落点不是继续把它留在 `P2`，也不是把它打回背景，而是把这条对象正式推进到 **`P3 / handoff-ready` 路径**：

> **`last Friday 16:00 London` 的月度 CME BTC 到期时钟后，在 Binance `BTCUSDT` perp 上执行 `post 60~120m short BTC`。**

由于当前 `Paper launch queue` 的 queue head 仍是 `Rank 183`，本轮把 `Rank 186` 收口为 **新增一条 handoff-ready 候选**，等待下一轮显式接线 / queue 重排，而不是继续占用唯一 `Active P2 slot`。

## 本轮补的 honesty / execution realism 证据
### 1) 事件时钟是 ex-ante 公开且因果可对齐的，不依赖任何盘中计算结果
这条信号不是“等某根 bar 算完才知道”的派生特征，而是公开日历事件：

- 规则：**每月最后一个周五，`16:00 London`**；
- 现有事件表 `btc_expiry_vs_friday_events.csv` 已直接体现了 **GMT / BST** 的因果切换：
  - `2025-01-31` 记为 `16:00 GMT`，对应 `16:00 UTC`
  - `2025-04-25` 记为 `16:00 BST`，对应 `15:00 UTC`
- 也就是说，production 侧只需要按 **London 本地时钟** 提前排程，不需要等 future bar、未来成交或任何回看信息来“确认事件发生”。

翻成人话：**这里没有 hidden lookahead。** 它是一个事先就知道会发生、且时间戳精确到分钟的 event clock。

### 2) 更保守的延迟入场 replay 下，perp 口径仍然活着
为了避免把结论建立在“不可能在事件瞬间完美打到第一笔”这种不诚实口径上，本轮直接用 Binance USDⓈ-M 公共 `1m` K 线，对 `14` 次月度到期事件做更保守的 delayed-entry replay：

- 标的：`BTCUSDT` perp
- 入场：不是假设卡在事件整点第一跳，而是改用 **`+1m` / `+5m` 延迟入场**
- 退出：`event+60m` / `event+120m`
- 成本：额外压一层 **`10bp` round-trip**

#### `close-to-close` 口径（更接近“看到首分钟后再下单”）
- `+1m -> +60m`：gross mean **`+20.49 bp`**，扣 `10bp` 后 net mean **`+10.49 bp`**
- `+1m -> +120m`：gross mean **`+20.86 bp`**，扣 `10bp` 后 net mean **`+10.86 bp`**
- `+5m -> +60m`：gross mean **`+19.73 bp`**，扣 `10bp` 后 net mean **`+9.73 bp`**
- `+5m -> +120m`：gross mean **`+20.09 bp`**，扣 `10bp` 后 net mean **`+10.09 bp`**

#### `open-to-close` 口径（更接近预先排程后按分钟开盘切入）
- `+1m -> +60m`：gross mean **`+21.00 bp`**，扣 `10bp` 后 net mean **`+11.00 bp`**
- `+1m -> +120m`：gross mean **`+21.37 bp`**，扣 `10bp` 后 net mean **`+11.37 bp`**
- `+5m -> +60m`：gross mean **`+22.27 bp`**，扣 `10bp` 后 net mean **`+12.27 bp`**
- `+5m -> +120m`：gross mean **`+22.65 bp`**，扣 `10bp` 后 net mean **`+12.65 bp`**

最关键的不是某个数字更大，而是：**边际入场延迟并没有把 edge 打没。** 这说明它并不依赖“恰好抢到事件后一秒钟的第一笔成交”这种不现实前提。

### 3) 真正可交易的实现对象就是 perp，本轮不再拿 spot 混淆 execution story
前几轮已经回答过 `spot / perp` 在方向上镜像一致；本轮 execution realism 只需要确认：

- **真正用于生产接线的标的是 Binance perp**，因为它天然可做空；
- spot 在这里继续只承担 **cross-check / control** 角色，而不是假装也能用同样方式落地 short。

所以本轮不会为了“spot short 不方便”而否掉对象；更诚实的表述是：**tradeable implementation 从一开始就该写成 perp-only directional event strategy，spot 只是验证事件后漂移不是单 venue artefact。**

## 为什么这轮不是 drop_to_background
- 没看到任何致命 honesty flaw：事件时间公开、DST 可前置排程、入场不依赖未来数据；
- 更保守的 `+1m / +5m` 入场 replay 后，perp 平均收益仍为双位数 bp gross、扣 `10bp` 后仍为正；
- 因此这轮不是“研究故事对、交易口径死”，而是**交易口径也过了最小诚实性检查**。

## 为什么这轮也不是 one-time P2->P1 re-scope
`P2 -> P1` 只在存在唯一明确 re-spec 时才允许；但这轮没有出现“原命题不行、只能改成另一个口径才活”的情况。相反：

- 原对象 `monthly CME expiry -> post 60~120m short BTC` 仍然成立；
- 只是把 execution 假设从含糊的“事件后开空”进一步钉死成了 **`+1m ~ +5m` 都可承受** 的可成交口径。

这不是 re-scope，而是 **honesty blocker 被解除**。

## 进入 P3 / handoff-ready 后保留的最小接线包
- 标的：`BTCUSDT` perp
- 事件时钟：`last Friday 16:00 Europe/London`
- 方向：`short`
- 可接受入场：`event+1m` 到 `event+5m` 分批 / 切片
- 主要退出：`event+60m` 与 `event+120m` 两档
- 成本预算：至少按 `10bp round-trip` 压测仍为正
- 角色定位：**monthly event-driven BTC directional sleeve**，不是全天候因子

## 本轮改变系统认知的一句话
`Rank 186 / CME expiry postfix short BTC` 完成 `honesty / execution realism` 出口决策并 `promote_P3`：月度 CME 到期时钟是 ex-ante 确定的，且 Binance perp 在 `+1m / +5m` 延迟入场、`+60m / +120m` 退出的更保守口径下扣 `10bp` 后均值仍为正，因此这条 exact-time 事件策略已可进入 `handoff-ready` 路径。

## 复用输入
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/btc_expiry_vs_friday_events.csv`
- Binance USDⓈ-M Futures 公共 `1m` K 线（本轮按月度事件窗口临时抓取）
