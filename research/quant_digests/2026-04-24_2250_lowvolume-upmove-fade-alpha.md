# 别把这个 2025 `momentum-reversal-crypto` 仓只读成“daily reversal 练习”：对 short-cycle crypto desk，更该先拆的是「低成交量上冲 × 次段回吐」这条 raw alpha

- 时间：2026-04-24 22:50 UTC
- 类型：2025 GitHub repo source audit（`README.md`）+ Binance USDⓈ-M public-data portability probe（`BTC/ETH/SOL/ADA/DOGE/XRP`，`15m/5m`）
- 主题类型：raw alpha
- 基础 alpha：**如果一根上涨 bar 看起来很猛，但其实成交量没跟上，这更像“虚冲”而不是“真突破”，下一小段更容易回吐。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/single-asset/mean-reversion/low-volume-fade/up-move-exhaustion/volume-filter/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：repo rule write-up + public-data portability probe

## 1. 这次看了什么
这轮看的是 Chase Keskinyan 的 2025 GitHub repo **Momentum & Reversal Signals on BTC and Altcoins**。

README 里最值得 desk 拿出来单独看的，不是 daily 组合 H4/H5/H6 整包，而是其中的 **H6 – Low-Volume Fade**：
- 先找一根“涨得明显”的 bar；
- 但要求这次上涨发生在 **低于平常的成交量** 上；
- 然后反着做，赌它不是健康趋势延续，而是弱参与的虚冲回吐。

翻成人话：**不是所有上涨都该追；没量配合的上涨，反而更像该 fade。**

## 2. 一句话结论
- **一句话核心结论：** 这条线值得 intake，因为 base alpha 很清楚：`弱参与上冲 -> 短时回吐`；但目前更像 **15m gross 有点东西、5m 基本被成本吃掉** 的 raw alpha 候选，而不是可直接上线的完整策略。
- **一句话证明方式：** repo 先在 daily BTC/alt 样本上说明 H4/H5/H6 单腿在 20 bps 成本后仍有正 Sharpe；我再把 H6 的核心逻辑压到 Binance USDⓈ-M `15m/5m`，做最小 portability probe，看 short-cycle 下还有没有毛边和净边。

## 3. 为什么和当前项目有关
这条题目和当前 desk 有直接关系，原因有四个：
1. **它是 raw alpha，不是 filter 假扮 alpha。** 基础判断很明确：`弱量上冲更容易回吐`。
2. **它能补 mean reversion 素材池。** 最近 intake 里 pairs / basis / cross-sectional 已经不少，这条是更干净的 single-name 逆势分支。
3. **它天然适合 `15m -> 5m` 两层表达。** 父层先判“是不是虚冲”，子层再决定要不要更细地找入场点。
4. **它很适合先做成本生存检验。** 如果连最粗糙的 taker 口径都完全不行，就没必要继续美化执行层。

相比再写一个大而全的趋势系统，这条更像一个能快速出 first verdict 的独立 raw alpha intake。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产均值回复
- 基础 alpha：上涨 bar 如果涨幅明显，但成交量低于常态，后续更容易回吐
- regime：更像发生在短时冲高、但没有真正量能确认的环境；不适合拿去硬抗高质量放量突破
- filter / veto：可加更强的“假突破”约束，比如只做 `ret1 > k * rolling_vol` 且 `vol_ratio < 0.8`，再避开重大事件前后 bar
- risk / sizing / execution overlay：先固定持有 `1~3` 根，粗扣 `8 bps` round-trip；后续再测 `ATR stop / time stop / maker-first`，以及只在 spread 较窄币上开机

## 4. repo 里最值得复用的 4 个点
1. **假设写得够朴素。** H6 不是黑箱模型，就是“涨很多但量不跟”的弱走势回吐。
2. **成本意识是在线的。** README 明确说 daily 回测里按 `20 bps` turnover 成本处理，不是只看裸收益。
3. **不是只看 BTC。** repo 至少把规则迁到 `ETH/SOL/XRP/ADA/LTC/DOGE`，说明作者知道要做 cross-asset robustness check。
4. **组合思想可借，但本轮不必整包照搬。** README 里 H4/H5/H6 会做 equal-weight / risk-parity 组合；对我们更值钱的是先把 H6 单独 desk 化，而不是把 daily 三腿打包照抄。

## 5. 本轮最小 portability probe
我先把 H6 desk 化成一个最小快检：
- **数据：** Binance USDⓈ-M 公共 klines，`BTC/ETH/SOL/ADA/DOGE/XRP`
- **周期：** `15m` 与 `5m`
- **信号：** 当前 bar 满足 `ret1 > 1.5 * rolling_std_20(ret1)` 且 `volume / volume_ma20 < 0.8`
- **交易方向：** 下一根开盘做空
- **离场：** 固定持有 `1` 或 `3` 根 bar
- **成本：** 粗扣 `8 bps` round-trip

先给 repo README 里最该记住的 2 个点：
1. **H4 / H5 / H6 单腿在 BTC daily 上，按 `20 bps` 成本后仍为正 Sharpe**（README 文字结论）
2. **三腿组合后 BTC 年化 Sharpe 大约 `0.8~1.0`**，而且回撤更浅（README 文字结论）

再给我这轮 short-cycle probe 最有用的 5 个数：
1. **`15m` pooled，持有 `1` 根：** 平均 gross `+3.94 bps/笔`，但 net `-4.06 bps/笔`
2. **`15m` pooled，持有 `3` 根：** 平均 gross `+3.61 bps/笔`，net `-4.39 bps/笔`
3. **最好看的 pocket 是 `DOGE 15m + hold 1`：** avg net `+0.90 bps/笔`，`26` 次事件
4. **另一个可留样本的是 `BTC 15m + hold 3`：** avg net `+9.40 bps/笔`，`13` 次事件
5. **`5m` 基本被成本打穿：** pooled `hold 1 / 3` 分别约 `-7.76 / -7.52 bps/笔`

翻成人话：
- **这条 raw alpha 在 `15m` 毛边还没死。**
- 但它很薄，说明“只靠下一根直接 taker 反手空”大概率不够。
- `5m` 口径更像噪音 + 成本双杀，当前不值得直接当高频主信号。

## 6. 风险与保留意见
1. **repo 原始证据是 daily，不是 intraday。** 我这轮只是把同一条经济直觉压到短周期，不能说等价复现。
2. **low volume 在 crypto 里有双重含义。** 有时它代表“虚冲”，有时只是正常时段切换；所以这条线很依赖 session / clock-time / liquidity state。
3. **当前 pocket 很稀疏。** `BTC 15m hold 3` 虽然净值看起来最好，但事件数只有 `13`，绝对不能直接乐观。
4. **固定持有太粗糙。** 这类 fade 很可能需要更好的 exit（例如回到 VWAP / 中轨就走），否则容易把到手回吐又坐没。

## 7. 下一步怎么测
1. **先做 `15m parent -> 5m child` 入场。** 父层仍用 `低量上冲` 判定，但子层等 `5m` 出现第一次 failed follow-through 或跌回事件 bar 中位价再进，看看能不能把 `8 bps` 成本口径救回来。
2. **把 exit 改成“回到事件 bar 半身 / VWAP / Bollinger 中轨”对照固定持有。** 这类信号本质是回吐，不一定需要拿满 `3` 根。
3. **做 clock-time / vol-regime 分层。** 先分亚洲/欧洲/美盘段、再分 realized-vol 四分位，确认 edge 是不是只在“安静时段里的假冲高”才存在。
4. **补 tradability veto。** 只保留 `spread 更窄 / volume 更高 / funding 不极端` 的币，看 DOGE/BTC pocket 是真 alpha 还是只是样本巧合。

## 8. 来源
- Chase Keskinyan. (2025). *Momentum & Reversal Signals on BTC and Altcoins*. GitHub repository.
- Repo URL: <https://github.com/chase-keskinyan/momentum-reversal-crypto>
- Readable URL: <https://github.com/chase-keskinyan/momentum-reversal-crypto>
- GitHub API metadata（repo created_at=`2025-11-27`, updated_at=`2025-12-05`）

## 9. 本轮 artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/low_volume_fade_probe_summary_2026-04-24.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/low_volume_fade_probe_detail_2026-04-24.csv`
