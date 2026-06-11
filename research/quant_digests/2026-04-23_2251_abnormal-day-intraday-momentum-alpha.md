# 别把这篇 2020 abnormal-return 论文只读成“日频异象”：更该先拆的是「异常日内小时级延续 × 次日跟随」这条 raw alpha
- 时间：2026-04-23 22:51 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：当 BTC / ETH / LTC 出现“一天级异常收益”后，当天剩余小时和下一天更可能继续同向走；把这个异常日当作入场门控，做顺势延续。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：single-asset / intraday / momentum / abnormal-return / hourly-timing / BTC / ETH / LTC / 1h / 15m / event-gate
- 证据类型：论文证据

## 1. 这次看了什么
看的是 Caporale, Plastun 在 *Financial Markets and Portfolio Management* 发表的 **Momentum effects in the cryptocurrency market after one-day abnormal returns**。它不是深网模型，也不是复杂 pairs，而是很直接地问：**如果某天已经出现异常涨跌，小时级回报会不会继续同向？** 作者用 BTC、ETH、LTC 对美元汇率，覆盖 `2015-01-01 ~ 2019-09-01`，并配了 trading simulation。

## 2. 核心结论
- **一句话核心结论：** 这篇最值得记住的不是“又一个动量论文”，而是 **异常日本身可以当作短周期顺势的入场门控**：一旦当天出现异常收益，小时级价格往往继续沿着异常方向走到收盘，甚至延续到下一天。
- **一句话证明方式：** 作者直接检验了 3 个假设（异常日内小时收益是否不同、异常日是否存在动量、异常后一天是否仍有动量），并用统计检验 + trading simulation 证明这个效果不是纯口号。
- 论文里一个很值钱的细节是：**异常收益的存在通常能在当天结束前被识别出来**，这意味着它更像“日内门控 + 后半段追随”，而不是一开盘就盲追。
- 但它也提醒我们：并非所有币都同样单边；论文明确提到 **BTC 正异常、ETH 负异常这两种情形里都出现过反向（contrarian）例外**。
- 最值得复用/复现的点：**把“异常日”翻成可计算门槛，再测 15m / 1h 的后半日延续和次日 follow-through。**

## 3. 为什么和当前项目有关
这篇对当前 `momentum` 主线的价值，不在于把它当完整系统，而在于补一块 **event-gated intraday momentum** 素材：
- 它是 **raw alpha**，不是纯 filter；base alpha 很清楚。
- 它天然能落到我们熟悉的 `1m / 3m / 5m / 15m` 执行层：先识别“异常日”，再测小时级延续。
- 它和之前那些纯趋势 / 纯 pairs 不同，提供的是 **“先有异常，再决定追不追”** 的时间结构，适合做 desk 侧的 admission gate。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 事件驱动
- 基础 alpha：异常收益日后的小时级延续与次日 follow-through
- regime：只有在当日收益已经偏离常态、且波动/方向信号足够强时才开机
- filter / veto：异常幅度不足、尾段不够强、流动性太差、方向已被反转吞掉时不做
- risk / sizing / execution overlay：按异常强度做仓位缩放；持有 1~4 根 `15m` 或 1 根 `1h` 做 A/B；成本前后分别评估

## 4. 可复刻的最小实验
**研究假设**：若当天的 `24h` 回报达到异常门槛，则该日剩余 `15m/1h` 回报更可能继续同向，且次日早段仍有残余延续。

**一个可计算定义：**
1. 先用最近 `N` 天日回报的 z-score 定义异常日：`|ret_1d| > k * std(ret_1d)`；
2. 把异常日分成正异常 / 负异常两类；
3. 在异常日之后，统计剩余 `15m` / `1h` 的同向延续概率与平均回报；
4. 过夜后再看下一交易日早段是否还有 follow-through。

**最小回测切口：** Binance `BTCUSDT / ETHUSDT / LTCUSDT` perp，先跑最近 `90d~180d`；主执行层用 `15m`，再压到 `5m` 做 child-exec。

**最该先看：**
- `avg net bps/trade`
- 异常日命中后的胜率 / 延续概率
- 正异常与负异常是否对称

## 5. 风险与保留意见
- 论文样本是 BTC/ETH/LTC 的美元汇率，不是 24/7 perp；**迁移到 Binance perp 需要先确认异常门槛怎么定义。**
- 论文里已经提示存在少数反向例外，说明这不是“单边永远有效”的故事。
- 这里的 edge 更像 **门控后的短窗延续**，不适合被硬包装成全天候常开信号。
- 如果异常定义太松，信号会变成噪音筛选器；太严，则 trade count 可能断崖。

## 6. 来源
- Guglielmo Maria Caporale, Alex Plastun. (2020). *Momentum effects in the cryptocurrency market after one-day abnormal returns*. Financial Markets and Portfolio Management.
- DOI: `10.1007/s11408-020-00357-1`
- Readable URL: `https://link.springer.com/article/10.1007/s11408-020-00357-1`
- Publisher page: `https://link.springer.com/article/10.1007/s11408-020-00357-1`
