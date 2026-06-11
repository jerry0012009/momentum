# 别把“自动化炼策略”只当黑箱：这份 2026 新仓库更值得先复现的是「6 信号投票 + 快慢退出 + 统一仓位」完整 raw alpha 骨架
- 时间：2026-03-24 00:52 UTC
- 类型：近 5 年新仓库 + 本地 split 复现实验（train/val/test）
- 主题类型：raw alpha
- 基础 alpha：trend / momentum continuation（多信号共识后做顺势延续）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/ensemble/voting/atr/rsi/exit/fullstack/repo/hyperliquid/crypto/1m/3m/5m/15m
- 证据类型：仓库源码 + 固定回测引擎 + 本地可复现实验

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“短中窗口动量共识后的趋势延续捕获”，不是 filter。**

本轮选题来自高信号新仓库 **Nunchi-trade/auto-researchtrading (2026)**。它不是只给一个指标，而是给了完整策略骨架：
- entry：6 信号投票（动量、超短动量、EMA、RSI、MACD、BB 压缩）
- exit：ATR trailing stop + RSI 过热/过冷退出 + 反向投票翻仓
- sizing：统一仓位（去掉了大部分“花哨动态缩放”）
- risk/cost：回测引擎内置 fee/slippage/funding + 杠杆约束 + 时间预算

这符合当前 desk 优先级：**可独立复现且可直接落地为完整策略的 raw alpha 候选**。

## 2. 核心结论
- **一句话结论：** 这份仓库最值得偷的不是“AI 自动改代码”叙事，而是“把 trend/momentum 做成可拆件、可回滚、可审计的完整策略工厂”。
- **一句话证据：** 我用仓库固定引擎、同一策略代码在 train/val/test 三段都重跑了一次，三段 score 都维持在高位（16~19 区间），且交易笔数足够，说明不只是单一窗口偶然。

关键数据点（本地复现实验）：
1. `train score=16.01, sharpe=16.01, trades=3274, maxDD=0.21%`
2. `val score=19.51, sharpe=19.51, trades=3666, maxDD=0.27%`
3. `test score=18.86, sharpe=18.86, trades=3552, maxDD=0.20%`

补充观察：
- 三段回测都打满了引擎 `120s` 时间预算，说明该框架本身是“固定算力预算下的策略筛选器”；迁移到我们 desk 时要同步考虑研究速度与计算成本。

## 3. 为什么和当前 desk 直接相关
这不是“再加一个确认层”，而是一个 **raw alpha 全链路模板**：
- 方向层：trend/momentum（可直接映射到 5m/15m、也可下探 1m/3m）
- 触发层：多信号投票降低单指标噪声
- 出场层：快慢结合（RSI 快出 + ATR 慢跟）
- 研究层：每次修改只动一个策略文件，天然适合做可追溯实验日志

对我们素材池的价值是：它把“alpha 想法 → 可执行规则 → 可回测比较”这条链路压缩得很短，适合快速 intake 和 first verdict。

## 3.5 策略拆解（必填）
- 方向属性：顺势延续（trend / momentum）
- 基础 alpha：过去 6h/12h 动量与趋势结构同向时，未来延续概率提升
- regime：中等以上波动、且非极端反转段时更友好
- filter / veto：BB 压缩（方向中性）、投票门槛、冷却窗口
- risk / sizing / execution overlay：ATR trailing、RSI 过热退出、统一仓位、fee+slippage+funding 成本记账

## 4. 与 `1m/3m/5m/15m` 的关系（实话版）
- 该仓库原始实验频率是 **1h**，不能直接当成 5m/15m 已验证。
- 但其规则结构是“可压缩周期”的：
  - `ret_6h/12h` 可改成 `ret_18bar/36bar@20m` 或 `ret_12bar/24bar@15m`
  - RSI/EMA/MACD/ATR 都是频率无关算子
- 因此它是 **可迁移的 raw alpha 骨架**，不是“现成可上 5m 的结论”。

## 5. 最小可复现实验口径（本轮）
### 5.1 数据源、公开性、更新频率
- 价格：CryptoCompare 小时 K 线（公开）
- funding：Hyperliquid `info` 接口（公开）
- 频率：仓库默认 `1h`；后续迁移可用 Binance/Hyperliquid 的 `1m/3m/5m/15m` 公开 K 线

### 5.2 本轮实验口径
- 代码：`autotrader/mar10c/strategy.py`
- 引擎：仓库 `prepare.py` 固定回测引擎
- 分段：`train / val / test`
- 标的：BTC/ETH/SOL
- 成本：引擎内置 `maker 2bps / taker 5bps / slippage 1bps`

## 6. 下一步怎么测（必须）
1. **周期压缩迁移测试（优先）**：把同一骨架下采到 `15m`，再到 `5m`，最后 `3m/1m`，每档都输出 `post-cost expectancy / trade count / turnover`，找生存频率带。  
2. **信号删减对照**：做 `6→4→2` 信号 ablation（保留同一出场），确认哪些信号是真 edge、哪些只是冗余。  
3. **执行诚实化**：把固定滑点替换为 `spread + participation cap`，测 `signal edge -> executable edge` 衰减。  
4. **统一口径复核**：用我们当前 desk 的 `next-bar open` 和交易成本参数重跑，避免“仓库引擎口径优势”误导。  
5. **不过拟合闸门**：要求 `val/test` 同时为正、且参数小扰动不过度崩塌，才进入 shadow 候选池。

## 7. 风险与保留意见
- 该仓库叙事里有“超高 Sharpe/低回撤”结果，必须持续防过拟合与口径偏差。  
- 当前证据是“框架和骨架值得复现”，不是“参数可直接照搬到 5m/15m 实盘”。  
- 高频下（1m/3m）交易成本与冲击可能让表现显著衰减，必须先过 friction ladder。

## 8. 来源
1. **Nunchi Trade. (2026). _auto-researchtrading_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/Nunchi-trade/auto-researchtrading  
   - Repo URL: https://github.com/Nunchi-trade/auto-researchtrading
2. **Nunchi Trade. (2026). _STRATEGIES.md (strategy evolution log)_.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/Nunchi-trade/auto-researchtrading/main/STRATEGIES.md  
   - Repo URL: https://github.com/Nunchi-trade/auto-researchtrading/blob/main/STRATEGIES.md
3. **Nunchi Trade. (2026). _autotrader/mar10c/strategy.py_.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/Nunchi-trade/auto-researchtrading/autotrader/mar10c/strategy.py  
   - Repo URL: https://github.com/Nunchi-trade/auto-researchtrading
4. **Hyperliquid Docs. _Info endpoint_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
5. **CryptoCompare API Docs. _Histohour endpoint_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://min-api.cryptocompare.com/documentation

## 9. 本地复现产物
- `reports/artifacts/quant_digests/nunchi_autoresearch_20260324/split_metrics.json`
- `reports/artifacts/quant_digests/nunchi_autoresearch_20260324/meta.json`