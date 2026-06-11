# 别把这份 regime-aware XSM 仓只读成“又一个横截面动量项目”：对 short-cycle crypto desk，更该先拆的是「cross-sectional relative momentum × BTC-vol / dispersion exposure scaling」这条 raw alpha 壳
- 时间：2026-04-21 18:17 UTC
- 类型：GitHub / repo source audit + working-paper draft audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：把一篮子币按过去一段时间的相对收益排序，做 `winner long / loser short`（或至少 `top-quintile long-only`）；这篇 repo 的真正主线不是单纯预测，而是 **横截面相对动量在高波动、低分化 regime 下会失真**，所以用 `BTC realized vol + cross-asset correlation/dispersion` 去缩放仓位
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：cross-sectional / relative momentum / regime-aware scaling / BTC vol / dispersion / overlap / router / Binance / 15m
- 证据类型：repo 工程骨架 + working paper draft + public-data first probe

## 1. 这次看了什么
这轮主来源是一个 2026 的 GitHub 研究仓：`Regime-Aware Crypto Momentum`。它不是单纯在讲“横截面动量”，而是在问更 desk-friendly 的问题：**同样的 XSM 信号，能不能在危险 regime 里少拿一点、在顺风 regime 里多拿一点。**

仓库里真正值得 intake 的点有两个：
1. **base alpha**：跨币种相对动量（cross-sectional relative momentum / XSM）
2. **overlay**：用 `BTC realized vol`、`cross-asset correlation / dispersion` 做 exposure scaling

### 来源
- **Repo / draft**：Olorato MacDonald Makgolo (2026), *Regime-Aware Crypto Momentum* / *Regime-Aware Exposure Scaling in Cross-Sectional Relative Momentum Cryptocurrency Strategies*
- **Repo URL**：<https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies>
- **Readable URL**：<https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies/blob/main/README.md>
- **Draft URL**：<https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies/blob/main/main1.tex>
- **关键代码**：`macro_state_test.py` / `coordination_overlay_test.py`

## 2. 核心结论
- **一句话核心结论：**这篇东西的 base alpha 不是“BTC 方向”，而是 **跨币种 winner/loser 相对动量**；它真正想补的，是这个 alpha 在 crypto 里太吃 regime，所以要加一个 `vol/dispersion` 的 exposure gate。
- Repo draft 里的写法很直白：
  - baseline XSM：年化收益约 `21.7%`、年化波动约 `49.3%`、Sharpe `0.44`、最大回撤约 `-85.9%`
  - regime-aware XSM：年化收益约 `16.7%`、年化波动约 `32.8%`、Sharpe `0.51`、最大回撤约 `-66.4%`
  - `PC1` 解释约 `66%` 横截面方差，`PC1` 与 `BTC` 相关约 `0.85`
- 我们自己的 Binance USDⓈ-M `15m` quick probe（10 个 liquid majors，约 `45d`）显示：
  - **静态 long-short XSM**（过去 `48` 根 `15m` 观察、下一根执行）gross 约 `-0.36 bps/bar`，粗成本后约 `-1.40 bps/bar`
  - 但 **top1 strongest-only router**（过去 `16` 根 `15m` 观察）gross 约 `+0.36 bps/bar`，Sharpe 约 `2.22`，累计约 `+14.5%`
  - 对应的 next `2/4/8 bars` gross 约 `+0.56 / +0.63 / +0.18 bps`
- **第一性结论：**这不是一个“静态全池 long-short 就能直接搬去 15m”的 alpha；更像是 **cross-sectional relative momentum + strongest-only router + regime-aware sizing** 的组合壳。

## 3. 为什么和当前项目有关
这轮最值得保留的不是“又一个动量项目”，而是它把 XSM 拆成了两层：
- **alpha 本体**：谁相对更强，谁相对更弱
- **风险/仓位层**：什么时候该少拿，什么时候该多拿

对现在的短周期 desk，这正好补了一个很实用的缺口：
- 如果你只看单币 trend，容易漏掉横截面轮动；
- 如果你只看横截面排序，又容易在高共振、高波动时被一锅端；
- 所以这类东西更适合被读成 **raw alpha + shared gate / overlay**，而不是纯综述。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对动量
- 基础 alpha：过去窗口里相对更强的币，下一段时间更可能继续相对强；相反，落后币更可能继续落后
- regime：`BTC realized vol` + `cross-asset correlation / dispersion`
- filter / veto：高波动、低分化时降杠杆 / 降暴露
- risk / sizing / execution overlay：这篇的核心增量就在这里；不是改信号，而是改 exposure

## 4. base alpha 到底是什么
先按用户要求，明确回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：是 `cross-sectional relative momentum`。**
>
> 不是 BTC 单边方向，也不是纯风控门控，而是：**一篮子币里，过去跑赢的相对更可能继续跑赢；但这种关系强烈依赖市场 regime，所以最好配 exposure scaling。**

因此它是标准 **raw alpha**，overlay 只是把它变得更可活。

## 5. 这条壳为什么可能在 crypto 上成立
1. **crypto 横截面共振很强。**
   repo draft 里 `PC1 ~66%`、`PC1` 与 `BTC` 相关约 `0.85`，说明很多币其实在吃同一个大因子。

2. **这会让横截面动量在 stress regime 里变脆。**
   当市场一起抖、一起涨跌时，单纯 winner/loser 排序的边际会被压扁。

3. **所以 exposure management 比“再调一点信号参数”更重要。**
   这也是这份 repo 最像 desk 作品的地方：它承认 alpha 有，但不相信 alpha 可以不管 regime 独活。

## 6. 可复刻的最小实验
### 本轮 public-data quick probe 口径
- 市场：Binance USDⓈ-M perpetual
- universe：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/TRX/AVAX/LINK`
- 周期：`15m`
- base signal：过去 `16` 或 `48` 根 bar 的 cross-sectional relative momentum
- 组合：
  - `long_top1`：只做最强的 1 个币（router 版本）
  - `ls_q20`：top/bottom `20%` long-short 版本
- 执行：下一根 bar
- 成本：粗略 `4 bps` round-trip proxy

### 本轮产物
- `reports/artifacts/quant_digests/2026-04-21_xsm_regimeaware_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-21_xsm_regimeaware_probe_detail.csv`

## 7. first verdict：怎么读这些数字
### 7.1 静态 long-short 不够厚
`15m` 上的 `ls_q20` 在这次 probe 里 gross / net 都不好看，说明这条 alpha **不适合被当成全池同权 long-short 主信号**。

### 7.2 strongest-only router 还有东西
`lookback=16` 的 `long_top1` 版本 gross 为正，Sharpe 也不错，说明它更像是：
- **挑最强 pocket 做 router**
- 而不是把整个宇宙都拉进来一起做

这和 repo 的主张其实一致：**不是信号本体万能，而是 exposure 和 pocket selection 更重要。**

### 7.3 overlay 逻辑是对的，但不能指望它救所有短周期 edge
我们自己的简化 gate（BTC vol 高 + 横截面分化低 → 半仓）触发率不低，但并没有把粗成本后的结果翻正。意思很简单：
- **overlay 的方向是对的**
- 但在 `15m` 上，静态信号本身还是太薄
- 所以真正该推进的是 **router + admission + child execution**，不是再加一层花里胡哨的门控

## 8. 和最近 digest 的关系：为什么这轮没重复
这篇和前面几篇动量/趋势类 digest 的差异在于：
- 它不是单资产方向；
- 也不是纯 breakout；
- 它是 **cross-sectional relative momentum**，并且把 **regime-aware exposure scaling** 作为主角。

所以它补的是：
- `raw alpha` 素材池里的 **cross-sectional / relative value** 分支
- 以及一个可复用的 **shared overlay**

## 9. 下一步怎么测
1. **把 `long_top1` 做成真正的 router。**
   先只允许 1 个仓位，按相对强度打分，测 `1m/3m/5m` child entry 能不能提高 `15m` 父信号的净边。

2. **把 regime gate 做成独立因子卡。**
   不要再把它藏在大脚本里，单独测：
   - `BTC rv` 分位
   - `cross-asset dispersion` 分位
   - `PC1 / BTC correlation`
   看谁最能解释 short-cycle 下的回撤收缩。

3. **先做 cost ladder。**
   这类 XSM 最怕 turnover。下一轮至少要测 `0 / 2 / 4 / 8 bps`，否则很容易把 gross 误当 alpha。

4. **把 `5m` 作为 child execution，不要直接替代 `15m`。**
   这条壳更像“谁值得做”的判断器，不像“每根都要出手”的强 alpha。

## 10. 风险与提醒
- 这份 repo 目前更像工作论文 / 研究仓，不是完整可直接上车的成品策略。
- `XSM` 在 crypto 上很容易被市场共振压扁，所以如果不加 regime / router，净边会很脆。
- 我们这轮的 15m probe 也说明：**不是所有看起来像动量的东西都能扛住 friction。**

## 11. 一句话收尾
**这篇东西最值得保留的不是“横截面动量还能不能赚钱”，而是：横截面动量在 crypto 里要活下来，先得学会按 regime 缩暴露。**
