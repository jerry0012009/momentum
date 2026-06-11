# 别把这个 funding-arb-bot 只读成“提醒机器人”：对 short-cycle crypto desk，更该先保留的是「跨所 funding spread carry × dip-tolerance 持仓门控」这条完整 raw alpha 壳
- 时间：2026-04-21 11:04 UTC
- 类型：GitHub repo source audit（`README.md` + `core/analyzer.py` + `core/executor.py` + `config.py` + `main.py`）
- 主题类型：raw alpha
- 基础 alpha：同一标的在不同永续交易所的 funding 年化差（尤其异号）可形成 delta-neutral carry；通过双边对冲赚 funding spread，而非赌方向
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/relative-value/stat-arb/delta-neutral/cross-exchange/apr-spread/dip-tolerance/child-execution/1m/5m/15m/repo/cost/risk

## 1) 这次看了什么
本次选题来自新仓 `kohtabeloff/funding-arb-bot`（2026，Python）。它不是回测 notebook，而是可运行的执行壳：扫描多交易所 funding、自动拼双腿、并带保护性平仓逻辑。对我们 desk 来说，价值不在“发 Telegram 提醒”，而在它把 **carry alpha 的全链路**写得很实：筛选→开仓→异常回滚→持仓巡检→保护性退出。

## 2) 一句话结论 + 证据
**一句话结论：**这份仓库里最可迁移的不是 UI，而是“`net_apr` 明确定义 + 异号 funding 优先 + dip 容忍持有 + 负 carry 强平”的完整策略壳，可直接映射成 `1m/5m` 子执行层。  
**它怎么证明：**`core/analyzer.py` 直接给出配对净 APR 计算与准入门槛；`core/executor.py` 给出双腿并发开仓与单腿失败回滚；`config.py` 与 `main.py` 给出负 APR/价格/清算距离的保护性退出参数。

## 3) 对 desk 最有用的可复用点（不是泛读后感）
- **Entry（准入）是硬门槛而非“感觉套利”**：
  - `MIN_PAIR_APR = 50`（年化阈值）
  - `MIN_VOLUME_USD = 50_000`
  - 对极端异常 funding 做过滤（如 `abs(apr) > 2000` 直接跳过）
- **Net APR 计算写得很清楚**：
  - 若两所 APR 异号：`net_apr = |apr_a| + |apr_b|`（最佳结构）
  - 若同号：`net_apr = ||apr_a|-|apr_b||`（只赚差值）
- **执行层不是纸面策略**：双腿并发下单；若一腿失败，另一腿自动回滚，避免裸方向暴露。
- **退出层有明确保护参数**：
  - `NEG_APR_HARD_CLOSE = -50`（净 carry 坏到阈值立即平）
  - `NEG_APR_WAIT_HOURS = 4`（软性负 carry 持续超时平）
  - 价格偏离与清算距离告警/强平阈值（`PRICE_AUTO_CLOSE_PCT=15` 等）

## 4) 为什么它和最近 digest 不重复
最近我们写过不少 funding/basis 主题，但多数聚焦单所 ranking、sign-flip 或 post-cost admission。这个仓的新增价值是：**把跨所双腿执行一致性（并发 + 回滚）和负 carry 持仓时钟（dip-tolerance）明确工程化**，对“从研究信号走到真实执行”更直接。

## 5) 下一步怎么测（最小可复现实验）
先不接私有 API，直接做公开数据版 first verdict：
1. **Universe**：先挑 8~15 个流动性好的共同上币（BTC/ETH/SOL/BNB/XRP 等）。
2. **Funding 快照频率**：每 1 分钟抓各所公开 funding/预测 funding（若仅 8h 发布则按最新值滚动），构建 `net_apr(t)`。
3. **准入规则**：`net_apr >= 40/50/60` 三档；并行比较是否需要 `same-sign veto`（只做异号）。
4. **持仓规则**：
   - 基线：固定持有至下一 funding 结算
   - 增强：引入 `dip-tolerance`（负 net_apr 持续 <4h 不平，>4h 平）
5. **成本口径**：双边 taker/maker 费率 + 滑点 + 资金占用；输出 post-cost 净 carry。
6. **评估指标**：净年化、回撤、负 carry 暴露时长、强平触发次数、执行失败回滚率。

> 对 `1m/3m/5m/15m` 的关系：funding alpha 本体是低频结算收益，但完全可以在 `1m` 做扫描与风控，在 `5m/15m` 做仓位重平衡与 child execution。

## 6) 风险与保留意见
- 这条 alpha 本质是 carry，不是每根 K 的方向预测；收益高度依赖费率层级与执行质量。
- 多交易所实盘会碰到 API 限频、下单拒绝、腿间滑点不对称，回滚逻辑必须真实压测。
- `APR` 看起来很高不等于可实现，必须统一到 post-cost 与可成交规模。

## 7) 来源
- Pavel Belov. (2026). *funding-arb-bot* (GitHub).
  - Repo URL: `https://github.com/kohtabeloff/funding-arb-bot`
  - Read files: `README.md`, `core/analyzer.py`, `core/executor.py`, `config.py`, `main.py`
- 关键代码口径（仓内参数）：
  - `MIN_PAIR_APR=50`, `MIN_VOLUME_USD=50000`
  - `NEG_APR_HARD_CLOSE=-50`, `NEG_APR_WAIT_HOURS=4`, `PRICE_AUTO_CLOSE_PCT=15`
