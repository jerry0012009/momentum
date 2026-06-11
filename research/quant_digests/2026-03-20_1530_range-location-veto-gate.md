# 别把 15m 的 breakout verdict 只写成“破位/回踩”：`range location（收盘在近期高低区间的位置）`更像三条收口线共用的快速 veto gate
- 时间：2026-03-20 15:30 UTC
- 类型：论文 + GitHub 复现仓库
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/range-location/confirmation/veto/filter/repo/paper/crypto/15m
- 证据类型：论文证据（JOF）+ 工程证据（公开复现仓库）

## 1) 这次看了什么
这轮主看 **Jiang, Kelly, Xiu (2023)** 的 JOF 论文《(Re-)Imag(in)ing Price Trends》，并补看其公开复现实现仓库。没复刻它“CNN 全流程主叙事”，只抽一个对我们 5m/15m 更快落地的旁支：**收盘在近期高低区间中的位置（range location）**。

## 2) 核心结论（先说人话）
- **一句话核心结论：** 在短周期里，先问“这根收盘是贴近近期区间下沿还是上沿”，往往比只看“是否刚突破/刚回踩”更诚实；它可以直接做 `final-verdict` 的 veto/confirm 层。  
- **一句话证明方式：** 论文把 OHLCV 图像化后做 CNN，并用 logistic 近似解释模型；文中明确给出一个可解释近似：**当收盘更靠近近期 high-low 区间低端时，后续收益更高**（偏反抽/均值回归方向）。

## 3) 为什么这轮比“另开新题”更值得做
它不是游离题，直接服务三条收口线：
1. **V3 breakout-short follow-up**：可直接当“别追空过度延伸”的 veto；
2. **Fib retest_hold**：可直接当“回踩后是否真的被接住”的确认层；
3. **EMA/PSAR raw alpha**：可作为外置 gate，帮助判断 EMA/PSAR 此刻更像趋势延续键，还是容易被反抽打脸。

## 4) 对三条收口线的落地映射
先定义（15m）：
- `RL_n = (close - rolling_low_n) / (rolling_high_n - rolling_low_n + 1e-9)`，取值约在 `[0,1]`。
- `RL` 越低 = 收盘越贴近近期区间下沿；`RL` 越高 = 越贴近上沿。

映射建议：
- **breakout-short follow-up（空头续跌）**：
  - 若入场时 `RL_20 <= 0.15`（已经贴下沿），默认 **veto add-short** 或 `size-down`；
  - 只在 `RL_20` 从中位回落（如 `0.45 -> 0.25`）且结构未被破坏时考虑 continuation。
- **Fib retest_hold（多头回踩确认）**：
  - 回踩后若 `RL_20` 从 `<=0.2` 重新回到 `>=0.4`，可视作“被接住”加分；
  - 若始终贴近下沿（`RL_20 < 0.2`），即使到达 Fib 位也先降级为 weak hold。
- **EMA/PSAR raw alpha**：
  - 把 RL 当作角色判定器：
  - `RL` 低位时，EMA/PSAR 的顺势信号更容易遇到反抽噪声；
  - `RL` 中高位且价在 EMA 之上时，顺势信号可信度更高。

## 5) 最小可复现实验（只用公开 OHLCV）
**数据源**：Binance USDT perpetual 15m K 线（公开可得，分钟级更新）。

### 实验 A（先做）
- 对象：现有三条 baseline（breakout-short / fib-retest / ema-psar）。
- 做法：每条 baseline 各做两组：`without RL gate` vs `with RL gate`。
- RL gate 初版：
  - short：拒绝 `RL_20 <= 0.15` 的新追空；
  - long（retest hold）：只保留 `RL_20` 在确认窗内上穿 `0.4` 的信号。
- 先看指标：`post-cost expectancy`、`failure-before-target`、`trade count retention`。

### 实验 B（稳健性）
- 把 `n` 做成 `{8, 20, 32}` 三档；
- 阈值做小网格：`0.1/0.15/0.2` 与 `0.35/0.4/0.45`；
- 看是否出现“参数平原”（避免只在单点有效）。

### 实验 C（角色判断）
- 仅在 EMA/PSAR 方向一致时，比较 `RL` 低位 vs 中高位分层收益；
- 若低位分层持续更差，则把 RL 固化为默认 risk overlay。

## 6) 风险与保留
- 论文主样本是股票日频，不是 crypto 15m；我们现在借的是**可解释旁支**，不是直接搬运主结论收益数字。  
- RL 过于简单，可能和“超跌反弹”混在一起；所以必须与结构条件（break/retest/EMA 方向）联用。  
- 若 gate 只提升胜率但显著压缩交易数，可能是“挑样本幻觉”，需同时盯 `trade count retention`。

## 7) 来源
1. **Jiang, J., Kelly, B., & Xiu, D. (2023). _ (Re-)Imag(in)ing Price Trends_. Journal of Finance.**  
   - Authors: Jingwen Jiang; Bryan Kelly; Dacheng Xiu  
   - Year: 2023  
   - Title: (Re-)Imag(in)ing Price Trends  
   - Venue: The Journal of Finance  
   - DOI: <https://doi.org/10.1111/jofi.13268>  
   - Readable URL: <https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268>  
   - PDF URL: <https://economics.yale.edu/sites/default/files/2023-11/The%20Journal%20of%20Finance%20-%202023%20-%20JIANG%20-%20Re%25E2%2580%2590%20Imag%20in%20ing%20Price%20Trends_0.pdf>  
   - Repo URL: N/A（论文官方未附本文使用的官方代码链接）
2. **gaoym4321. (2023). _ReImagining_Price_Trends_. GitHub Repository.**  
   - Authors: GitHub user `gaoym4321`  
   - Year: 2023（仓库命名对应论文复现）  
   - Title: ReImagining_Price_Trends  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/gaoym4321/ReImagining_Price_Trends>  
   - Repo URL: <https://github.com/gaoym4321/ReImagining_Price_Trends>  
   - 代码示例（窗口/标签设置）：<https://raw.githubusercontent.com/gaoym4321/ReImagining_Price_Trends/main/sample_codes.py>
3. **Binance Developers. USDⓈ-M Futures Kline/Candlestick Data（公开市场数据）**  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>

## 8) 下一步怎么测（一句话）
先在三条 baseline 上做一个 2×3 的小网格（有/无 RL gate × `n={8,20,32}`），只看成本后收益、失败率、交易保留率；若三条线至少两条同时改善且不严重掉交易数，就把 RL gate 升级为默认 shared veto layer。