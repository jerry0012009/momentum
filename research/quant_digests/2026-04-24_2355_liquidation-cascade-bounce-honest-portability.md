# 别把这个 liquidation-cascade repo 只读成“抄底叙事”：对 short-cycle crypto desk，更该先拆的是「跨资产联动爆仓下杀 × 恐慌后反弹」这条 raw alpha——但先做诚实去前视检验

- 时间：2026-04-24 23:55 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `Liquidation Cascade Project - Nitish Kaza.ipynb`）+ Binance USDⓈ-M public-data honest portability probe（16-asset universe，`1h` parent）
- 主题类型：raw alpha
- 基础 alpha：**如果一批币在同一时段一起出现“放量急跌 / 连环爆仓”，这更像被杠杆强平出来的暂时性错杀，随后 `1~2h` 往往有一段超跌反弹。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/single-asset-plus-cross-asset/mean-reversion/liquidation-cascade/panic-bounce/volume-spike/joint-crash/binance-perpetual/1h/15m/5m/repo/public-data/cost/risk
- 证据类型：repo notebook rule audit + public-data honest portability probe

## 1. 这次看了什么
这轮看的是 Nitish Kaza 的 2025 GitHub repo **Crypto-Liquidation-Cascades**。它最值得 desk 拿出来的，不是“危机里抄底”这句口号，而是一个很具体的 raw alpha 壳：

- 某币 `1h` 跌超 `5%`，或 `2h` 累计跌超 `8%`；
- 同时伴随异常放量；
- 并且不是单币抽风，而是 **至少 3 个币同时触发**；
- 然后去赌这类下杀里掺了很多被动平仓，后面会有一小段反弹。

翻成人话：**不是见跌就接，而是只接“很多人被一起挤下车”的那种跌。**

## 2. 一句话结论
- **一句话核心结论：** 这条线值得 intake，因为 base alpha 很清楚：`联动爆仓 -> 暂时性错杀 -> 短时反弹`；但 repo 原结果带明显前视成分，做成诚实版后，最近样本里更像“少数 alt pocket 有肉、整体直接抄底不够稳”。
- **一句话证明方式：** repo notebook 用 `1h` Binance 数据把“急跌 + 放量 + 多币同步”写成规则；我再把其中前视部分拿掉，只保留因果上可交易的 crash gate，做 Binance USDⓈ-M `1h` honest probe，看成本后还能剩多少。

## 3. 为什么和当前项目有关
这题和当前 desk 直接相关，原因有四个：
1. **它是 raw alpha。** 基础判断不是 filter 冒充 alpha，而是非常明确的 `panic liquidation bounce`。
2. **它补的是“事件型均值回复”池子。** 最近 intake 里 pairs / basis / low-volume fade 都有了，这条补的是“系统性挤仓”分支。
3. **它天然适合 `1h parent -> 15m/5m child`。** 父层负责判断是不是联动爆仓，子层再优化入场，不必一看到血就立即 taker 冲进去。
4. **它能顺手产出 shared gate。** 哪怕最后不单独成策略，这个 `joint crash + abnormal volume` 事件也能服务 crowding-fade / reversal / basis 收敛等别的逆势腿。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 事件驱动 / 单资产均值回复（带跨资产确认）
- 基础 alpha：多币同时出现放量急跌时，价格里混入了被动平仓的“超卖”，后续 `1~2h` 容易反弹
- regime：更适合高杠杆挤仓、恐慌传播、相关性突然抬升的时段；慢跌阴跌不一定适用
- filter / veto：可加 `OI / liquidation prints / funding crowding / spread widening veto`，避免把“真基本面崩塌”误当成错杀
- risk / sizing / execution overlay：先用 `1h` 事件做父层 admission，再在 `15m/5m` 里等第一段止跌失败不再创新低、或回收事件 bar 下半区再进；仓位应按事件级别限额，不宜对同一 crash cluster 重复加码

## 4. repo 里最值得复用的 4 个点
1. **事件定义够具体。** `1h/2h` 跌幅 + 放量分位 + 至少 3 币同步，这比“看起来像爆仓”强得多。
2. **它知道要做 cross-asset confirmation。** 不是把单币新闻针当成 liquidation alpha。
3. **Notebook 暴露了真正要改的地方。** 作者用了 `confirmed_bounce = 下一小时收益为正`，又用 `如果下一小时涨超 2% 就只持有 1h，否则持有 2h`；这两步都有前视，正好提醒我们别把 headline 结果直接当可交易策略。
4. **它很适合拆成 gate + child execution。** repo 的核心价值不一定是“原样抄 notebook”，而是把 `joint liquidation event` 作为可复用事件层组件留下来。

## 5. 本轮 honest portability probe
我先把 repo 里的前视部分拿掉，只保留因果上站得住脚的 crash gate：
- **数据：** Binance USDⓈ-M 公共 `1h` klines，`BTC/ETH/SOL/XRP/DOGE/ADA/BNB/LINK/AVAX/LTC/BCH/DOT/UNI/SUI/TRX/AAVE`
- **样本：** 约 `5000` 根 `1h` bar，`2025-09-28 16:00 UTC` 到 `2026-04-24 23:00 UTC`
- **事件：** `1h <= -5%` 或 `2h <= -8% 且最近 1h 未继续跌超 3%`，再配 `7d` rolling 成交额 `90/95` 分位放量，并要求 **>=3 个币同小时触发**
- **交易：** 下一根 `1h` 开盘做多触发币
- **离场：** 固定持有 `1h` 或 `2h`
- **成本：** 同时看 `8 bps` 与 repo notebook 里的 `20 bps` round-trip

先给 repo 最该记住的 3 个数：
1. README 样本 `2023-01-01 ~ 2024-01-31` 给出 **`98` 笔、总收益 `50.71%`、Sharpe `1.81`**
2. Notebook 真实规则里用了 **“下一小时先涨了才算 confirmed_bounce”**
3. Notebook 离场还用了 **“若下一小时收益 > 2% 就持有 1h，否则持有 2h”** —— 这也是前视

再给我这轮 honest probe 最有用的 6 个数：
1. **联合事件很稀少：** 16 币、约 7 个月样本里只有 **`6` 个事件时点 / `44` 笔资产级触发**
2. **trade-level pooled，持有 `1h`：** 平均 net **`-189.05 bps/笔`**（`8 bps` 成本）
3. **trade-level pooled，持有 `2h`：** 平均 net **`-112.36 bps/笔`**，但 median net **`+126.51 bps/笔`**、胜率 **`61.4%`**
4. **equal-weight event basket，持有 `2h`：** 只有 `6` 次事件，平均 net **`-199.35 bps/事件`**
5. **正 pocket 主要在 liquid alt：** `AAVE +2h` 约 **`+259.68 bps/笔`**（`3` 笔），`LINK +2h` **`+247.75 bps/笔`**（`4` 笔），`SUI +2h` **`+237.69 bps/笔`**（`4` 笔）
6. **最大的坑是 crash cluster 重复接飞刀：** `2025-10-10 20:00 UTC` 这一组事件的 equal-weight `2h` gross 约 **`-1480.2 bps`**

翻成人话：
- **这条线不是“见联动暴跌就无脑接”的稳赚钱按钮。**
- 它更像：有些被挤得最狠的 alt 确实会弹，但如果你把所有联动暴跌都一把接，很容易在真正的趋势性崩塌里被继续碾。
- 所以它当前更适合作为 **事件 admission / child-exec 候选**，而不是裸 `1h next-open long everything`。

## 6. 风险与保留意见
1. **repo headline 有前视污染。** 这不是小瑕疵，是会直接抬高回测表现的结构性问题。
2. **事件数太少。** 最近样本只有 `6` 个联合事件时点，任何乐观结论都得打折。
3. **同一 crash cluster 的重复开仓很危险。** 连续几个小时都满足条件时，第二枪第三枪未必还是“错杀”，可能已经是趋势腿。
4. **缺少真正的 liquidation / OI 数据。** 目前只用价格和成交额做代理，能抓到“像爆仓”的东西，但抓不到“确实在爆仓”的强确认。

## 7. 下一步怎么测
1. **先改成 `1h parent -> 15m child`。** 父层只负责报“这是联动爆仓候选”，子层等 `15m` 出现第一次止跌结构（不再创新低 / 收回事件 bar 下半区 / microprice 转正）再进。
2. **做 cluster cooldown。** 同一事件簇里只允许首枪，或要求距离上次事件至少 `4~6h`，看能不能避开 `2025-10-10` 这种连环补刀。
3. **补真实 crowding 数据。** 接 Coinglass/交易所 `OI / liquidation / funding`，把“像爆仓”升级成“确实有挤仓证据”的版本。
4. **只保留 alt-bounce pocket。** 先分 `BTC/ETH/BNB` 与 liquid alts，验证这条线是不是本质上只该在 `AAVE/LINK/SUI` 这类高弹性品种上开机。

## 8. 来源
- Nitish Kaza. (2025). *Crypto-Liquidation-Cascades*. GitHub repository.
- Repo URL: <https://github.com/kazan04/Crypto-Stat-Arb>
- Notebook URL: <https://github.com/kazan04/Crypto-Stat-Arb/blob/main/Liquidation%20Cascade%20Project%20-%20Nitish%20Kaza.ipynb>
- Readable URL: <https://github.com/kazan04/Crypto-Stat-Arb>

## 9. 本轮 artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/liquidation_cascade_honest_probe_summary_2026-04-24.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/liquidation_cascade_honest_probe_trades_2026-04-24.csv`
