# 别把这份 Coinbase 多 agent repo 只读成“AI trader”：对 short-cycle desk，更该先拆的是「oversold confluence score × fee-floor scalp shell」这条 raw alpha
- 时间：2026-04-15 08:23 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `backend/agents/scalp_agent.py` + `backend/agents/signal_generator.py` + `backend/tests/test_scalp_agent.py` + `backend/agents/order_executor.py`）+ Binance Spot `BTCUSDT/ETHUSDT 1m` 近 `10d` portability probe
- 主题类型：raw alpha
- 基础 alpha：单资产、超短周期的 **oversold mean reversion**——当 `RSI(7) / BB(20,2) / VWAP(20) / StochRSI / MFI / OBV slope` 同时指向“跌过头但还没彻底失控”时，未来 `5~15m` 更容易反弹；`ADX` 在这里主要是 **regime gate**，不是 alpha 本体
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-asset / mean-reversion / oversold-confluence / RSI / Bollinger / VWAP / StochRSI / MFI / OBV / ADX / scalp / cost / BTC / ETH / 1m / 3m / 5m / 15m
- 证据类型：repo 源码 + public-data portability probe

先回答 base alpha：**它的 base alpha 很清楚，不是“大模型帮你交易”，而是 1 分钟级过冲后的均值回归。** 这个 repo 真正值得 intake 的，也不是前端或多 agent 架构，而是 `ScalpAgent` 里那条已经写成可下单壳的 **long-only oversold scalp**。

## 1. 这次看了什么
看的是 `gl4500/coinbase-ai-trader`。repo 表面是 Coinbase 多 agent 交易系统，但真正对当前 desk 有价值的，不是 AI 包装，而是 `backend/agents/scalp_agent.py` 里那条非常具体的短周期策略：

- 只做 `BTC-USD / ETH-USD`，明确把标的限制在 **tight-spread majors**；
- 每 `60s` 扫一次 entry，每 `1s` 检查 exit；
- 用一个 **0~10 分的 oversold confluence score** 触发入场：
  - `RSI(7) < 25` 给 `+2`，`<35` 给 `+1`
  - `price <= BB lower band` 给 `+2`，`<= BB mid` 给 `+1`
  - `VWAP distance < -0.5` 给 `+2`，`<0` 给 `+1`
  - `StochRSI K < 20` 给 `+1`
  - `OBV slope > 0.15` 给 `+1`
  - `MFI(7) < 25` 给 `+1`
- `ADX(10)` 只拿来分市场状态：
  - `ADX > 25` 视作 trend regime，最低入场分数 `5`
  - `ADX < 20` 视作 range regime，但要求更高，最低分数 `6`
  - 中间 dead zone 直接不做
- 出场壳也很完整：
  - 固定 `TP = +0.30%`
  - 固定 `SL = -0.25%`
  - `ATR(7) * 1.5` trailing stop
  - `15m` time exit
  - 单仓最多 `20%` 资金、最多 `2` 个并发仓位、单日回撤超 `3%` 直接停机
- 代码里还把 **成本门槛** 明写了：Coinbase maker `0.006%`/side，round-trip `0.012% = 1.2 bps`，并据此写明最小可行 TP 大约 `0.15%`，实际用 `0.30%` 给 `2.5x` cushion。

这就不是“指标拼盘 idea”，而是已经接近 production shell：**entry / regime / exit / sizing / risk / cost floor** 都在源码里。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值得 intake 的，是「**oversold confluence score × fee-floor scalp shell**」这条完整 raw alpha，而不是它的 AI 外壳。
- **一句话证明方式：** repo 代码先把完整规则写死；我再把这套 long-only 过冲反弹壳迁到 Binance Spot `BTCUSDT/ETHUSDT 1m` 做近 `10d` portability probe，看未来 `5m/15m` 回报和简单 `TP/SL/time-exit` 壳是否还活着。
- **最重要的不是“分数越高越好”，反而是：`5 分入场` 比 `7~8 分极端入场` 更健康。** 这点很值钱，因为它说明更深的 oversold 不一定更有 edge，很多时候只是接更掉落的刀。
- 这条线天然适合当前 desk：
  - 原生就是 `1m`；
  - 最大持有期就是 `15m`；
  - 能直接向 `3m/5m` 降噪迁移；
  - 而且明确把 **交易成本** 当成策略设计约束，而不是事后补丁。

## 3. public-data portability probe：first verdict
我做了一个**快速移植版**：把 repo 的 confluence 打分、`ADX` gate、`TP/SL/time-exit` 迁到 Binance Spot `BTCUSDT/ETHUSDT 1m` 近 `10d`（各 `14,400` 根 bar）上；为保持速度，这里没复刻 Coinbase tick 级 live entry，也暂时没加 trailing stop，只保留最核心的 TP/SL/time 壳。

### 3.1 未来收益先看方向对不对
对所有触发 entry 的 bar：

- `BTCUSDT`
  - entry bars：`1,989`（约 `13.8%` bar）
  - 未来 `5m` 平均：`+0.07 bps`
  - 未来 `15m` 平均：`+1.17 bps`
  - 未来 `15m` 中位数：`+1.60 bps`
- `ETHUSDT`
  - entry bars：`2,001`（约 `13.9%` bar）
  - 未来 `5m` 平均：`+0.03 bps`
  - 未来 `15m` 平均：`+0.94 bps`
  - 未来 `15m` 中位数：`+2.85 bps`

这说明一件事：**这条 alpha 更像 `10~15m` 的 bounce，不是 1~2 根 bar 内立刻完成的 ultra-instant scalp。**

### 3.2 最有意思的细节：高分不等于更强
按 entry score 分桶后，未来 `15m` 表现是：

- `BTCUSDT`
  - `score=5`：`+3.17 bps`
  - `score=6`：`-0.02 bps`
  - `score=7`：`-0.10 bps`
  - `score=8`：`+0.97 bps`
- `ETHUSDT`
  - `score=5`：`+3.14 bps`
  - `score=6`：`+0.52 bps`
  - `score=7`：`+0.00 bps`
  - `score=8`：`-1.32 bps`

这比“又一个 BB/RSI 反转壳”更值钱的地方就在这：

> **repo 里的 confluence score 不该被读成“越多指标同时极端越该冲”，反而更像“至少要够，但太极端就可能进入 knife-catching zone”。**

也就是说，这套源码更值得 desk 拿走的 branch，不是“无脑追高分”，而是：
1. 先保留 `score >= 5` 这条 oversold bounce 母线；
2. 再单独测试 `5分`、`6分`、`7分+` 三个 pocket；
3. 看看是不是中等偏强的 oversold 最好，而极端 oversold 需要更强 veto。

### 3.3 简化交易壳 first pass 也还没死
用一个很朴素的 long-only 壳：entry bar 收盘进场，之后最多持有 `15m`，优先触发 `+30 bps TP / -25 bps SL / TIME`：

- `BTCUSDT`
  - 模拟交易数：`441`
  - 平均单笔 gross：`+1.00 bps`
  - 胜率：`51.25%`
  - `TP / SL / TIME`：`15.2% / 18.1% / 66.7%`
- `ETHUSDT`
  - 模拟交易数：`481`
  - 平均单笔 gross：`+0.61 bps`
  - 胜率：`53.01%`
  - `TP / SL / TIME`：`20.0% / 27.9% / 52.2%`

这不是“已经能上线”的意思，因为 gross 还不厚；但它至少说明：**结构有迁移性，不是换个 venue 就瞬间翻负。**

## 4. 为什么它和现有素材池不重复
库里当然已经有不少 `VWAP / BB / RSI` 的 mean reversion 摘要；但这条 intake 仍然有新增量，原因是它补的不是单个指标，而是下面这四件事一起出现：

1. **原生 `1m`，而不是把 `15m/1h` 的 envelope 生硬下采样；**
2. **源码明确写出 cost floor**，不是事后再问“手续费怎么办”；
3. **`ADX` 不是方向信号，而是 market-state admission；**
4. **最值得测的研究问题不是 alpha body 本身，而是 `score saturation`：为什么 `5分` 常常比 `7分+` 更好？**

所以这篇更像是在现有 mean reversion 素材池里补一块：
**“多指标 oversold confluence 不一定越极端越好，真正要做的是找到最能反弹、又没跌成事故现场的 pocket。”**

## 4.5 策略拆解（必填）
- 方向属性：单资产、long-only、逆势 bounce / mean reversion
- 基础 alpha：短周期 oversold 过冲后，未来 `5~15m` 向均值回摆
- regime：`ADX` 低于 `20` 的 range 可做，但要更高分；`ADX > 25` 的 trend 也可做，前提是 oversold 只是 pullback 而不是结构性崩塌
- filter / veto：`score saturation`、dead-zone `ADX`、tight-spread majors only
- risk / sizing / execution overlay：`TP/SL/time exit`、ATR trailing、单仓 `20%`、最多 `2` 仓、日内 `-3%` halt、fee floor

## 5. 可复刻的最小实验
### 5.1 最小研究假设
**单币 1m oversold bounce 在 crypto majors 上确实存在，但最佳 pocket 不是“极端 oversold”，而是“够深、但还没烂掉”的中等强度 confluence。**

### 5.2 一个可计算定义
在 `1m` bar 上计算：
- `RSI(7)`
- `BB(20,2)`
- `VWAP(20)` 偏离
- `StochRSI(14)`
- `MFI(7)`
- `OBV slope(10)`
- `ADX(10)`

然后按 repo 原逻辑打分，比较：
- `score = 5`
- `score = 6`
- `score >= 7`

三档在未来 `5m / 10m / 15m` 的回报与 hit-rate 差异。

### 5.3 先怎么测
1. **先做 pocket test，不要先做总分回归。**
   - `score=5`、`6`、`7+` 分开跑；
   - `TREND` vs `RANGE` 分开跑。
2. **把 holding period 扫清楚：**
   - `3m / 5m / 10m / 15m`；
   - 看它到底是 quick bounce 还是慢一点更稳。
3. **成本先测三档：**
   - `1.0 / 2.0 / 4.0 bps` round-trip；
   - 因为这条壳虽然源码自带 cost awareness，但 transfer 到别的 venue 后不一定还够厚。
4. **加一个“更极端先别接”的 veto 测试：**
   - 比如 `score>=7` 时，要求 `1m realized vol` 不爆、或 `5m return` 不能过大负斜率；
   - 直接验证 knife-catching 是否主要来自波动失控。
5. **再决定迁到 `3m/5m`：**
   - 如果 `1m` 费后太薄，就把同一套 score 改成 `3m` 触发、`15m` 管理，测试是否更像 production 版本。

## 6. 风险与保留意见
- 这是 **long-only 单资产 bounce**，不是 market-neutral 组合；容量、回撤路径、单边暴跌适应性都有限。
- repo 原始执行环境是 Coinbase spot + live tick；我的 portability probe 用的是 Binance spot `1m` OHLCV proxy，执行 realism 明显更弱。
- quick sim 里暂时没加 trailing stop，真实壳可能略好，也可能因为更高换手变差。
- 目前 first verdict 还是偏谨慎：**结构活着，不代表费后已经足够肥。**

## 7. 本轮产出文件
- 研究笔记：`research/quant_digests/2026-04-15_0823_oversold-confluence-scalp-shell.md`
- portability artifacts：
  - `reports/artifacts/quant_digests/coinbase_scalp_confluence_probe_20260415_0815/summary.csv`
  - `reports/artifacts/quant_digests/coinbase_scalp_confluence_probe_20260415_0815/btcusdt_score_bucket_returns.csv`
  - `reports/artifacts/quant_digests/coinbase_scalp_confluence_probe_20260415_0815/ethusdt_score_bucket_returns.csv`
  - `reports/artifacts/quant_digests/coinbase_scalp_confluence_probe_20260415_0815/btcusdt_sim_trades.csv`
  - `reports/artifacts/quant_digests/coinbase_scalp_confluence_probe_20260415_0815/ethusdt_sim_trades.csv`
  - `reports/artifacts/quant_digests/coinbase_scalp_confluence_probe_20260415_0815/meta.json`

## 8. 来源
1. **gl4500. (2026). _coinbase-ai-trader_. GitHub repository.**
   - Repo URL: `https://github.com/gl4500/coinbase-ai-trader`
   - Readable URL: `https://github.com/gl4500/coinbase-ai-trader`
2. **Key files used in this digest**
   - `https://github.com/gl4500/coinbase-ai-trader/blob/main/README.md`
   - `https://github.com/gl4500/coinbase-ai-trader/blob/main/backend/agents/scalp_agent.py`
   - `https://github.com/gl4500/coinbase-ai-trader/blob/main/backend/agents/signal_generator.py`
   - `https://github.com/gl4500/coinbase-ai-trader/blob/main/backend/tests/test_scalp_agent.py`
   - `https://github.com/gl4500/coinbase-ai-trader/blob/main/backend/agents/order_executor.py`
