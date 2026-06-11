# 别把 `RSI enter→exit→re-enter` 状态机当成 breakout-short 的 shared follow-up：它在 15m 更像 Fib / EMA long 的稀疏 admission，不适合 short 侧默认放行
- 时间：2026-03-20 13:53 UTC
- 类型：GitHub 仓库 + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/rsi/state-machine/retest/admission/asymmetry/filter/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 代理快检（公开行情缓存）

## 1) 这次看了什么
这轮主看新仓库思路：**MoDiggler75 / crypto-trading-bot** 里的 `backtest_4hr_rsi_retest.py`，核心不是“RSI>70/<30 本身”，而是 **RSI 状态机**：
- `neutral -> in_oversold -> exited_oversold -> in_oversold` 才算一次 oversold retest；
- `neutral -> in_overbought -> exited_overbought -> in_overbought` 才算一次 overbought retest；
- 再叠加价格在 zone 外侧，触发 long/short。

这和我们三条收口线直接相关：它是一个典型的 **旁支过滤层**（不是 headline alpha），可快速映射到 `Fib retest_hold` / `EMA-PSAR continuation` / `breakout-short follow-up`。

## 2) 核心结论（先说人话）
- **一句话结论**：这套 RSI 状态机在 15m 上目前只看到 **long 侧可用的稀疏 admission 价值**，不适合当 breakout-short 的 shared gate。
- **为什么值得做而不是继续老题**：它直接回答三条收口线里最卡的“确认/否决条件怎么写得更诚实”，且可在现有信号文件上 1 次快检落地，不需要新重型数据管线。

## 3) 本地最小代理快检（15m）
### 3.1 数据与口径
- 资产：`BTC/ETH/SOL` perp
- 频率：`15m`
- 基础信号：`rank76` 三条 baseline（`fib_retest_long` / `ema_psar_long` / `breakout_short`）
- 价格缓存：本地 Binance 公共行情缓存（见产物路径）
- 评估：从 `entry_idx` 起看未来 `4/8 bars` signed return（本轮主看 `8 bars`）

### 3.2 这轮映射的状态机 gate
为了避免 30/70 过稀疏，先用一个 desk 友好的最小映射（lookback=8 bars）：
- long setup（Fib/EMA）：`min(RSI14)<=45` 且 `signal-bar RSI14>=50`
- short setup（breakout-short）：`max(RSI14)>=55` 且 `signal-bar RSI14<=50`

并同时测试更“严格”的双触发版本（近似 repo 风格的二次触碰），结果样本为 0（过稀疏）。

### 3.3 关键数据点
1. **Long 组合（Fib+EMA）**：
   - baseline：`n=137`，`win8=59.1%`，`mean8=+10.3 bps`
   - gated：`n=13`，`win8=69.2%`，`mean8=+72.9 bps`
   - 解释：更像“少做但更干净”的 admission（覆盖率仅约 `9.5%`）。
2. **Breakout-short**：
   - baseline：`n=61`，`win8=50.8%`，`mean8=+37.6 bps`
   - gated：`n=9`，`win8=22.2%`，`mean8=-51.8 bps`
   - 解释：short 明显被伤害，不应当 shared。
3. **严格状态机版本**：`n=0`（long/short 都触发不了）
   - 解释：直接照搬严格 retest 在当前 15m 样本下过于稀疏。

> 额外成本感知（粗口径）：若按 round-trip 12 bps，long gated 仍保留显著正边际；short gated 进一步恶化。

## 4) 对三条收口线的直接意义
- **V3 breakout-short follow-up**：
  当前证据不支持把该 RSI 状态机作为 short 侧 follow-up gate，默认应 `not-shared`。
- **Fibonacci confirmation / retest_hold**：
  可把它作为 long 侧“确认层”的候选稀疏 gate（先控交易频次，再看成本后稳定性）。
- **EMA / PSAR raw alpha focus**：
  更像 admission/filter，不是 raw alpha 替代触发器；可与 EMA/PSAR 主触发做 AND/score 组合评估。

## 5) 下一步怎么测（可直接开工）
做一个三臂、两频率、含成本的最小 OOS：
1. Baseline（不加 RSI 状态机）
2. Relaxed 状态机 gate（本轮口径）
3. Relaxed + 轻量趋势过滤（如 `EMA20>EMA50` 仅用于 long）

统一在 `5m execution / 15m signal` 与 `15m/15m` 双模式跑：
- 样本：滚动 `120d train + 60d test`
- 成本：`6 / 10 / 15 bps per side`
- 指标优先级：`post_cost_return`、`trade_count`、`positive_asset_ratio`、`MAE/fail-fast`

若 short 侧连续两个窗口仍劣化，直接把它冻结为 `breakout-short veto branch`（不再默认尝试 shared gate）。

## 6) 风险与保留
- 证据主体是 repo 工程逻辑 + 本地代理快检，不是完整策略回测。
- 当前 gated 样本偏小（尤其 Fib），需要滚动窗口验证稳定性。
- 这轮结论是“角色判断”：更偏 **long-side admission**，不是“新主信号发现”。

## 7) 来源
1. MoDiggler75. (2026, accessed). *crypto-trading-bot*. GitHub repository.  
   - Authors: MoDiggler75  
   - Year: 2026 (repository active)  
   - Title: crypto-trading-bot  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/MoDiggler75/crypto-trading-bot>  
   - Repo URL: <https://github.com/MoDiggler75/crypto-trading-bot>
2. MoDiggler75. (2026, accessed). *backtest_4hr_rsi_retest.py*. GitHub code file.  
   - Authors: MoDiggler75  
   - Year: 2026  
   - Title: backtest_4hr_rsi_retest.py  
   - Venue: GitHub code file  
   - DOI: N/A  
   - Readable URL: <https://raw.githubusercontent.com/MoDiggler75/crypto-trading-bot/master/backtest_4hr_rsi_retest.py>  
   - Repo URL: <https://github.com/MoDiggler75/crypto-trading-bot>
3. Binance. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data*.  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>  
   - Repo URL: N/A

## 8) 本轮落地产物
- `reports/artifacts/quant_digests/rsi_state_machine_setup_summary_2026-03-20.csv`
- `reports/artifacts/quant_digests/rsi_state_machine_asset_setup_summary_2026-03-20.csv`
- `reports/artifacts/quant_digests/rsi_state_machine_combo_summary_2026-03-20.csv`
