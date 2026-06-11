# 别把这份跨平台研究只读成“预测市场行为报告”：对 crypto short-cycle desk，更该先测的是「Binance 末窗先行 × Polymarket 5m 价格滞后」这条 raw alpha
- 时间：2026-04-09 23:34 UTC
- 类型：GitHub 仓库 + 配套研究论文（repo 内 PDF）
- 主题类型：raw alpha
- 基础 alpha：**Binance 现货在结算前最后几十秒先反映方向，Polymarket 5m 合约价格短暂滞后；在末窗按 Binance 方向打滞后腿，靠到期结算兑现。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：prediction-market / relative-value / stat-arb / lead-lag / event-window / latency
- 证据类型：工程经验 + 实证统计（repo 内大样本）

## 1) 这次看了什么
看的是 `OffGrid0xDAO/cross-platform-arbitrage`（2026），核心材料包括 `README.md`、`paper/short_results.pdf(.tex)`、`analysis/detect_arbitrage.py`、`analysis/binance_arb_link.py` 与 `data/cross_arb_15m_results.json`。

## 2) 核心结论（先说人话）
- 一句话核心结论：**这不是“观点交易”，而是一个可执行的末窗信息差 alpha：Binance 先动、Polymarket 后动，窗口很短但可被系统化抓取。**
- 一句话证明方式：作者用约 **10.5M trades（11 天）** 做交易级别回放，直接统计末窗入场、命中率、跨平台同步、OOS 衰减与 oracle 偏差风险。
- 数据里最硬的一组信号：
  1) `5m` 市场里有 **29 个钱包** 在最后 `15s` 交易，胜率 `>98%`；
  2) 当 BTC 末窗波动 `>$80` 时，命中率约 `97%~100%`，而小波动场景接近 `50%`（说明 edge 来自“信息差”，不是普遍预测能力）；
  3) `15m` 跨平台检测到 **161,577** 组同秒配对交易（W1），OOS（W2）仍有 **148,142**；但 repo 同时给出衰减：latency arb 单笔从约 `+0.49` 变到 `-0.31`，并有 `-$31/window/day` 的下滑斜率。

## 3) 为什么和当前项目有关
这条线能直接扩充我们的 **raw alpha 素材池**（relative-value / stat-arb / lead-lag），而且不是“只讲过滤器”：
- 有明确 entry 触发（末窗 + Binance move 阈值 + Polymarket 价格滞后）；
- 有明确 exit（到期结算或窗口硬平仓）；
- 有明确可量化风险（容量衰减、oracle 偏差、延迟与滑点）。

它比继续做纯结构确认更值钱，因为它天然带了“可交易性审计”：edge、衰减、失败场景都在同一份材料里。

## 3.5) 策略拆解（必填）
- 方向属性：相对价值 / 事件驱动（lead-lag）
- 基础 alpha：Binance 末窗先行信息 -> Polymarket 同窗滞后定价
- regime：仅在“末窗绝对波动足够大”与“盘口可成交”时启用
- filter / veto：
  - `|ΔBTC_last_xs| < threshold` 不做；
  - 盘口滑点 > 预设阈值不做；
  - 跨平台对冲时若 oracle 偏差风险过高不做
- risk / sizing / execution overlay：
  - 单窗固定风险预算；
  - 每窗最多 1 次入场（防过度追单）；
  - 窗口结束强制平；
  - 记录端到端延迟，超阈值直接 veto

## 4) 可复刻的最小实验（先跑这个）
**研究假设**：在 `5m` 结算前最后 `15~30s`，若 Binance 末窗位移超过阈值，Polymarket 方向单价格仍未充分反映该位移，则下一步到结算的期望收益为正。

**可计算定义（最小版）**：
- 触发：`abs(BTC_t - BTC_window_start) >= X`（先试 `X=$60/$80/$100`）
- 信号：
  - 若 `BTC_t > BTC_start` 且 `P(UP)` 低于同类窗口经验映射价差 `edge_min`，买 `UP`
  - 反之买 `DOWN`
- 退出：到该 `5m` 窗口结算；或提前 `time-stop=10s`

**最小回测切口**：
- 资产/市场：Polymarket BTC 5m + Binance BTC spot
- 频率：事件驱动（秒级）
- 样本：先复刻 repo 同期（2026-02-19~2026-03-02），再滚动到近 30 天做 OOS

**先看 2 个指标**：
1) `post-cost expectancy / trade`（扣手续费+滑点+延迟冲击后）
2) `high-move bin vs low-move bin` 的分层命中率差（验证 edge 是否真的来自“大波动末窗”）

## 5) 风险与保留意见
- 这类 alpha 衰减快，repo 已给出 week2 明显走弱；
- 若做 Polymarket-Kalshi 对冲，存在 oracle 不一致（文中约 `5.7%~6.2%`）导致“双边都错”的尾部风险；
- 真正可实盘与否，核心在 **端到端延迟 + 可成交深度 + 手续费**，不是 paper 命中率本身。

## 6) 来源
1) 0x0010110 / Chainsaw Research. (2026). *Cross-Platform Arbitrage in Cryptocurrency Prediction Markets: An Empirical Analysis*. Venue: repo working paper.
   - DOI: N/A（未见正式 DOI）
   - Readable URL: `https://github.com/OffGrid0xDAO/cross-platform-arbitrage`
   - Repo URL: `https://github.com/OffGrid0xDAO/cross-platform-arbitrage`
   - Full paper (repo PDF): `https://github.com/OffGrid0xDAO/cross-platform-arbitrage/raw/master/paper/cross_platform_arbitrage.pdf`
2) 同仓库核心实现与结果文件：
   - `analysis/detect_arbitrage.py`
   - `analysis/binance_arb_link.py`
   - `data/cross_arb_15m_results.json`
   - `data/whale_analysis.json`
