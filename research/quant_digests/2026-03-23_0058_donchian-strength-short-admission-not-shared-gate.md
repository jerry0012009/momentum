# 别把 Donchian `penetration / ATR` 继续写成 shared conviction gate：它在 15m 更像 breakout-short 的 short-side admission score，对 Fib / EMA long 仍不诚实
- 时间：2026-03-23 00:58 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/v3/final-verdict/follow-up/donchian/breakout-strength/penetration/atr/asymmetry/admission/filter/repo/crypto/15m/fibonacci/ema/psar
- 证据类型：工程证据（仓库源码）+ 本地最小代理快检

## 1. 这次看了什么
这轮主看 **zekiayberk / Donchian-ML-Strategy (2026)**。仓库表面 headline 是“Donchian breakout + ATR trailing stop + ML filter”，但更值得 desk 偷的不是整套 ML，而是一个很便宜的旁支：作者把 `breakout_strength_threshold = (close - channel_edge) / ATR` 单独做成了可开关过滤层，且在 `config.yaml` 里直接写了 `0.0 # Base setup is more robust`。

我把这个想法翻成当前 desk 的问题：
> **Donchian 突破后，`penetration / ATR` 该不该被升成 15m 三条线共享 hard gate？**

## 2. 核心结论
- **一句话结论**：`penetration / ATR` 不适合当三条收口线共享确认；在 15m 上，它更像 **breakout-short 的 short-side admission / follow-up score**，不该镜像套到 Fib / EMA long。  
- **一句话证明方式**：先读 repo 里的信号与 ablation 骨架，再用 Binance Futures `BTC/ETH/SOL` 最近 `120d` 的 `15m` K 线做一个 next-bar-open + `+1.5ATR/-1ATR`（8 bars）代理判决，比较不同 `strength threshold` 的多空结果。

关键数据点（BTC/ETH/SOL 合并）：
1. **short 侧：阈值能把 pooled 结果从略负拉到转正**  
   - `th=0.0`: `n=1477`, `avg_pnl_r=-0.0173`  
   - `th=0.2`: `n=1100`, `avg_pnl_r=+0.0068`，保留率 `74.5%`  
   - `th=0.6`: `n=573`, `avg_pnl_r=+0.0489`，保留率 `38.8%`
2. **long 侧：即使阈值加严，pooled 结果仍没翻正**  
   - `th=0.0`: `avg_pnl_r=-0.1197`  
   - `th=0.6`: `avg_pnl_r=-0.0324`，但交易只剩 `33.9%`
3. **资产间还带明显非对称**  
   - `BTC short` 要到 `th=0.6` 才明显转正（`avg_pnl_r=+0.0980`）  
   - `ETH short` 在 base 已略正，最好点更像 `th=0.2`（`+0.0912`）  
   - `SOL short` 在 `th=0.4` 才刚翻正（`+0.0093`）

## 3. 为什么和当前项目有关
- **对 `V3 final-verdict / breakout-short follow-up`**：这条最直接。它说明“破得够不够深”可以是 short-side 的便宜 admission score，用来减少 weak break 追空。  
- **对 `Fibonacci confirmation / retest_hold`**：当前证据不支持把它镜像成 long-side shared hard gate；否则容易砍掉很多 long 候选，却没换来诚实正边际。  
- **对 `EMA / PSAR raw alpha focus`**：更像再次提醒“别把 breakout conviction 类特征误升级成 shared 通用过滤层”；它是 setup-specific，不是全 desk 公共真理。

## 3.5 策略拆解（必填）
- 方向属性：顺势 continuation，且当前明显偏 short-side 受益  
- 基础 alpha：Donchian breakout 后的延续 / follow-up  
- regime：默认只在已形成方向性挤压后的 breakout 事件里讨论，不是全天候 shared gate  
- filter / veto：`penetration / ATR` 强度阈值，当前更像 short-side admission score  
- risk / sizing / execution overlay：`signal on close -> next bar open`，`+1.5ATR/-1ATR`，8 bars first-hit

## 4. 可复刻的最小实验
下一步不要把它直接钉成一个全局 hard gate，而是先做 **breakout-short 专项 3 臂 A/B**：
1. `baseline_v3`（无 strength gate）
2. `baseline_v3 + short_only_threshold`（先测 `0.2 / 0.4 / 0.6`）
3. `baseline_v3 + short_strength_bucket_size`（不 veto，只按 strength 分层缩放仓位）

统一口径：
- 资产：BTC/ETH/SOL perp
- 周期：`15m signal`，补 `5m execution` 对照
- 判决：沿用当前 final-verdict / follow-up 框架，再补成本档位 `6/10/15 bps per side`
- 优先看：`post-cost avg_pnl_r`、`trade retention`、`continue vs fail spread`

如果结果只在 short 侧稳定抬升、且 long 侧持续无效，就把它正式写成 **`breakout-short specific admission score`**，不要再往 Fib / EMA shared gate 上推。

## 5. 风险与保留意见
- 这是 **proxy first-hit**，不是完整组合回测；
- 阈值最优点在不同币上不一致，说明它更像“打分项”而不是固定门槛；
- repo 原始主战场是 `1h`，这里是把想法压缩映射到 `15m`；
- 若后续加成本、滑点、funding 后只剩极窄优势，应该降级为 veto / sizing，而不是入场层。

## 6. 来源
1. **zekiayberk. (2026). _Donchian-ML-Strategy_. GitHub Repository.**  
   - Authors: zekiayberk  
   - Year: 2026  
   - Title: Donchian-ML-Strategy  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/zekiayberk/Donchian-ML-Strategy`  
   - Repo URL: `https://github.com/zekiayberk/Donchian-ML-Strategy`

2. **zekiayberk. (2026). _strategy/signals.py_ + _config.yaml_.**  
   - Authors: zekiayberk  
   - Year: 2026  
   - Title: strategy/signals.py; config.yaml  
   - Venue: GitHub raw source  
   - DOI: N/A  
   - Readable URL: `https://raw.githubusercontent.com/zekiayberk/Donchian-ML-Strategy/main/strategy/signals.py`  
   - Repo URL: `https://raw.githubusercontent.com/zekiayberk/Donchian-ML-Strategy/main/config.yaml`

3. **Binance. (2026). _USDⓈ-M Futures REST API – Kline/Candlestick Data_.**  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data  
   - Venue: Binance Developers Docs  
   - DOI: N/A  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`  
   - Repo URL: N/A

## 7. 本轮落地产物
- `scripts/run_quant_digest_donchian_strength_short_admission.py`
- `reports/artifacts/quant_digests/2026-03-23_donchian_strength_short_admission/events.csv`
- `reports/artifacts/quant_digests/2026-03-23_donchian_strength_short_admission/summary_by_symbol_side_threshold.csv`
- `reports/artifacts/quant_digests/2026-03-23_donchian_strength_short_admission/summary_pooled.csv`
- `reports/artifacts/quant_digests/2026-03-23_donchian_strength_short_admission/meta.json`
