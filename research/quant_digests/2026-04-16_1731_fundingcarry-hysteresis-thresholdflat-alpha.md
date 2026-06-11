# 别把这份 funding-rate-arb 仓只读成“收租复盘”：对 short-cycle desk，更该先拆的是「entry/exit hysteresis + threshold-flat robustness」这条完整 raw alpha

- 时间：2026-04-16 17:31 UTC
- 类型：GitHub repo source audit（`README.md` + `src/backtest.py` + `src/sensitivity.py` + `src/basis_trade.py` + `src/data_fetcher.py`）
- 主题类型：raw alpha
- 基础 alpha：`long spot + short perp` 的 delta-neutral carry（高 funding 入场，funding 回落离场；价格腿主要承担 basis 漂移）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/relative-value/stat-arb/delta-neutral/hysteresis/threshold-robustness/1m/3m/5m/15m/repo/cost/risk
- 证据类型：工程实现证据（含源码与回测结果）

## 1) 这次看了什么
- **Authors/Org**：zwmjj（GitHub）
- **Year**：2026
- **Title**：*Crypto Funding Rate Arbitrage*
- **Venue**：GitHub repository
- **DOI**：N/A（工程仓库）
- **Readable URL**：<https://github.com/zwmjj/funding-rate-arb>
- **Repo URL**：<https://github.com/zwmjj/funding-rate-arb>

这个仓库不是“概念讲解”，而是完整链路：`ccxt` 拉数据 → 策略回测（含成本）→ 阈值敏感性扫描 → 与 dated futures basis 对照。

## 2) base alpha 先说清
一句话：
> **当永续 funding 足够高时，做 `long spot + short perp` 收 carry；当 funding 衰减到阈值以下就平仓。**

所以它是标准 `raw alpha`（carry / relative-value / stat-arb），不是 filter 或 overlay。

## 3) 核心结论（对 desk 最值钱）
1. **可直接落地的规则完整**：源码里给了明确的 `entry_bps / exit_bps / taker_bps / max_hold_periods`，并把开平双腿成本显式计入（round-trip 16 bps）。
2. **阈值鲁棒性比“最优点”更重要**：敏感性扫描显示 `entry` 在约 `1~3 bps` 区间收益较平坦，不是靠单点参数吃饭；`exit=0` 往往优于更早离场，说明“轻微 funding 回落不必急着砍”。
3. **regime 依赖非常强**：README 给出的分段结果里，2021 年 carry 很肥，2025+ 明显变薄（BTC/ETH 年化约 `4%` 左右），接近交易摩擦生死线。
4. **默认参数下有可读收益-风险画像**（repo 报告）：BTC/ETH 年化约 `9.0% / 11.2%`，最大回撤约 `-0.34% / -1.80%`，但资金利用率仅约 `32%~37%`，本质是“稀疏开仓的机会型 carry”。

## 3.5) 策略拆解（必填）
- 方向属性：相对价值 / carry（市场中性）
- 基础 alpha：`funding rich -> short perp + long spot`，等待 funding 均值回落
- regime：资金费率整体分布与市场杠杆拥挤度（bull 更肥，低杠杆期变薄）
- filter / veto：可加 `spread-cap`、流动性阈值、结算前后禁入窗口
- risk / sizing / execution overlay：按 funding 强度分层仓位；双腿成交成本上限；最大持有期与负 carry 连续时长止损

## 4) 可复刻的最小实验（映射 1m/3m/5m/15m）
- **研究假设**：同样是 funding carry，短周期能否通过执行与 admission 把净收益从“接近成本线”拉回正值。
- **可计算定义**：
  - 状态变量：`f_t`（8h funding，向 1m/3m/5m/15m 前向填充）
  - 入场：`f_t > q80` 或固定 `f_t > 1bp`
  - 离场：`f_t < q50` 或固定 `f_t < 0.5bp`
  - 成本：按两腿 round-trip bps + 滑点阶梯
- **最小回测切口**：BTC/ETH，Binance spot+perp，先做 `15m`（稳健基线）→ `5m`（主战）→ `3m/1m`（结算窗口高强度版本）。
- **先看 2 个指标**：`net_bps_per_trade`、`post-cost win rate`（再看 `max_dd` 与 `exposure`）。

## 5) 风险与保留意见
- 当前仓库以 8h funding 驱动，短周期迁移后最容易被**执行摩擦和腿间滑点**吃掉。
- 若只看年化、不看 `exposure` 与容量，会高估可部署性。
- README 结果是仓库作者口径；落地前要做统一成本梯度（maker/taker/混合）与多交易所复核。

## 6) 下一步怎么测（执行清单）
1. 在 `15m` 先做固定阈值 vs 分位阈值 A/B（同一成本口径）。
2. 在 `5m` 加入 `spread-cap veto`（只做价差未恶化样本）。
3. 在 `1m/3m` 只做 funding 结算前后事件窗（例如 `[-30,+30]` 分钟），验证是否存在可交易 pocket。
4. 四周期统一输出：`trade_count / net_bps / max_dd / exposure / implementation_shortfall`，先过 admission 再谈放大仓位。

## 7) 来源
1. zwmjj. (2026). *Crypto Funding Rate Arbitrage*. GitHub repository. DOI: N/A.  
   Readable URL / Repo URL: <https://github.com/zwmjj/funding-rate-arb>
2. Repo source files:  
   - <https://raw.githubusercontent.com/zwmjj/funding-rate-arb/main/src/backtest.py>  
   - <https://raw.githubusercontent.com/zwmjj/funding-rate-arb/main/src/sensitivity.py>  
   - <https://raw.githubusercontent.com/zwmjj/funding-rate-arb/main/src/basis_trade.py>  
   - <https://raw.githubusercontent.com/zwmjj/funding-rate-arb/main/src/data_fetcher.py>