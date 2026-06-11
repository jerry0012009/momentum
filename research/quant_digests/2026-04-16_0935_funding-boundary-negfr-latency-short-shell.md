# 别把这份 funding-boundary 仓只读成“测速脚本”：对 short-cycle desk，更该先拆的是「极端负 funding × 结算边界延续」这条 raw alpha 壳

- 时间：2026-04-16 09:35 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `main.py` + `streams.py` + `short_order.py` + `analyze_latency.py` + GitHub API metadata）+ Binance 公共 API 快检（`premiumIndex` 实时快照 + `fundingRate`/`1m klines` 事件窗抽样）
- 主题类型：raw alpha
- 基础 alpha：**在 funding 结算前后（尤其 T-30s ~ T+15m），极端负 funding 合约常伴随拥挤空头/流动性不均，存在“结算边界价格延续”可交易窗口；可先用 `most-negative funding` 横截面做 short-only 事件驱动壳。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（先从单腿事件驱动 baseline 起，随后再加对冲腿）
- 主题标签：raw-alpha/event-driven/funding/boundary/settlement/latency/microstructure/continuation/short-only/cross-sectional/admission/5m/15m/1m/3m/repo/public-data/cost/risk
- 证据类型：repo 代码证据 + 公共行情快检

## 1) 先回答：这篇东西的 base alpha 是什么？

一句话：**base alpha 不是“测延迟”本身，而是“极端负 funding 标的在结算边界附近的短窗可交易延续”。**

这份 repo 的关键线索是：
- `streams.py` 先做横截面筛选：`funding_rate < -0.003`（阈值可调）；
- `main.py` 在“离结算 30 秒”触发记录；
- `short_order.py` 给出“定点发 market SELL”的执行骨架（目标是结算边界打点）。

所以它不是纯监控工具，更像 **funding 边界事件 alpha 的执行母板**。

## 2) 来源信息（repo-based）

- Authors / Maintainer：wangshaofu
- Year：2026（`created_at=2026-02-19`）
- Title：*LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps*
- Venue：GitHub Repository
- DOI：N/A（仓库）
- Readable URL：<https://github.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps>
- Repo URL：<https://github.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps>

## 3) 为什么这条线值得进当前素材池

1. **raw alpha 明确且短周期友好**：事件时钟清楚（funding settlement），天然贴合 `1m/3m/5m/15m`。
2. **admission 不是拍脑袋**：先横截面找“最极端 funding”再打点，不是全市场乱做。
3. **执行壳已有最小闭环**：边界时刻触发、WS 到达延迟记录、下单时戳记录都在 repo 里。
4. **可快速扩展成完整策略**：在现有 short-only 骨架上补 exit/sizing/risk/cost 即可。

## 3.5) 策略拆解（必填）

- 方向属性：事件驱动 / 单资产 / funding-crowding continuation
- 基础 alpha：`extreme-negative funding cross-section × settlement-boundary continuation`
- regime：仅在极端负 funding + 结算临近窗口激活（其余时间不交易）
- filter / veto：
  - `funding_rate <= threshold`（建议从 `-0.001`、`-0.002`、`-0.003` 三档测试）
  - `nextFundingTime - now <= 30s`（或 60s）
  - `bid-ask spread` / 深度 / 最小成交额 veto
- risk / sizing / execution overlay：
  - 单笔风险固定（如账户权益 `0.25%~0.5%` 风险预算）
  - 首版 `time-stop` 为核心（如 `+5m` 或 `+15m` 强平）
  - 先 taker baseline，再评估 maker 改造

## 4) 本轮关键数据点（公开可复核）

### 4.1 Binance 全市场 funding 快照（本轮）
基于 `fapi/v1/premiumIndex`（718 合约）：
- `lastFundingRate <= -0.003` 的只有 **3** 个；
- `lastFundingRate <= -0.001` 的有 **8** 个；
- 说明 `-0.003` 是明显尾部事件，不是常态信号。

同时，next funding 时间分布高度集中：
- `12:00 UTC`：**487** 个
- `16:00 UTC`：**191** 个

这意味着事件触发适合做“批量候选→集中执行”的排班式引擎。

### 4.2 事件窗抽样（`fundingRate` + `1m klines`）
对近期极端负 funding 样本（`funding <= -0.001`）做小样本抽样，得到 **61** 个事件（5 个符号）：
- 事件前 `-5m→0m`：中位约 **-27.8 bps**（已出现明显下压）
- 事件后 `0m→+5m`：中位约 **+9.2 bps**（短窗噪声大）
- 事件后 `0m→+15m`：中位约 **-20.5 bps**，`<-10 bps` 占比 **55.7%**

first verdict：**`+15m` 方向更像“延续空头 pocket”，`+5m` 更混合。**

> 这也是为什么首版建议优先测 `15m` 事件持有，不先锁死超短 scalp。

## 5) 与 `1m/3m/5m/15m` 的关系

- `1m/3m`：用于事件打点与执行质量（边界时钟、滑点、到达延迟）
- `5m`：用于检测“结算后立即反抽 vs 延续”分岔
- `15m`：当前抽样里更像可交易 horizon（延续信号更稳定）

结论：这是典型 **秒级触发 + 分钟级持有评估** 的 short-cycle alpha。

## 6) 最小可复现实验（今天可开）

- 研究假设：极端负 funding 的合约在结算后 15 分钟更易延续下行。
- 数据源（公开可得）：
  - Binance Futures `fapi/v1/premiumIndex`
  - Binance Futures `fapi/v1/fundingRate`
  - Binance Futures `fapi/v1/klines`（1m）
- 公开性：公开 API
- 更新频率：实时（premium/funding state）+ 分钟级 K 线
- 最小实验口径：
  1. 每个结算点前 30s，筛 `funding <= {-0.001,-0.002,-0.003}`
  2. 对候选按 funding 绝对值排序，取 top1 / top3
  3. `t=settlement` 市价做空
  4. `exit = min(time_stop, stop_loss, take_profit)`：先测 `time_stop=5m/15m`
  5. 评估成本后 EV、命中率、最大不利偏移（MAE）

## 7) 直接可落地 baseline（entry/exit/sizing/risk/cost）

### Entry
- 触发：`nextFundingTime-now <= 30s`
- Admission：`funding <= -0.002`（baseline）
- 执行：market SELL（首版）

### Exit
- 主退出：`time_stop = 15m`
- 风险退出：`stop_loss = +35 bps`（价格上行不利）
- 收益退出：`take_profit = -45 bps`

### Sizing
- 单笔名义 = `min(账户权益×8%, 交易对容量上限)`
- 同时持仓上限 2 笔（避免同一 funding 时段过度拥挤）

### Risk
- 每次 funding 窗口最大亏损预算 `<= 0.8%` 权益
- 极端滑点/深度异常直接 veto（不成交优先于硬上）

### Cost
- 首版按 taker 双边 + 滑点压力测试三档：`8/12/20 bps`
- 必须报告成本后 EV，不接受只看毛收益

## 8) 风险与保留意见

1. 当前证据偏“事件统计 + 工程壳”，并非完整 OOS 生产验证。  
2. 小币种样本（如 RAVE/BARD）可能受流动性噪声影响，需做容量分层。  
3. `short-only` 可能在反抽行情被快速打脸，必须保留硬 time-stop 与止损。  
4. 若要上实盘，必须先补下单回报与盘口重放，验证“信号存在≠可成交可留存”。

## 9) 下一步怎么测（本轮后直接动作）

1. **事件路由实验**：同一 admission 下比较 `top1` vs `top3 equally-weighted`。
2. **时窗实验**：固定入场，比较 `hold=3m/5m/15m` 的成本后 EV 曲线。
3. **阈值实验**：`-0.001/-0.002/-0.003` 三档 funding admission，对比样本量与边际收益。
4. **容量实验**：按成交额分 bucket，检查低流动性是否吞噬全部 edge。

---

## 参考

1. wangshaofu. *LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps* (GitHub repo, 2026).  
   <https://github.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps>
2. Repo source file: `main.py`  
   <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/main.py>
3. Repo source file: `streams.py`  
   <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/streams.py>
4. Repo source file: `short_order.py`  
   <https://raw.githubusercontent.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps/main/short_order.py>
5. Binance USDⓈ-M Futures API docs (funding/premium/klines).  
   <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api>
