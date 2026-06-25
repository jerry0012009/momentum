# PM-59A-UI-FIX2：Factor Evaluation 页面真实阅读顺序修复指令

> 用途：把本文件链接发给服务器 AI，让它按 PM 指令修复 `factor-evaluation.html` 的真实 DOM 顺序、HTML 结构和 page QA。
>
> 注意：本任务只修页面信息架构和 QA，不重算任何后端数据。

---

## 0. 执行要求

执行 **PM-59A-UI-FIX2**。

不要重算任何后端数据，不要修改 PM-59A 计算逻辑。请根据本文件，以及用户随后提供的 MB 文档网页链接，对照当前 GitHub 代码和生成后的 `factor-evaluation.html` 页面，修复真实页面阅读顺序、HTML 结构和 page QA。

### 输入材料

用户会另外提供一个 MB 文档网页链接。你需要：

1. 打开该网页，作为 PM 对页面阅读顺序和信息架构的设计说明。
2. 对照当前仓库中的：
   - `scripts/_build_factor_eval_html.py`
   - `reports/site/factor-library/factor-evaluation.html`
   - `scripts/check_factor_evaluation_page_completeness.py`
   - `scripts/factor_metric_glossary.json`
3. 不要只改静态 HTML，必须改 builder，使页面可以再生。
4. 修改后重新生成 HTML 和 QA 报告。

---

## 1. 当前问题

PM-59A-UI-READING-ORDER 已经完成一部分，但仍有结构性问题：

1. Evidence Reading Order 文案存在，但真实 DOM 顺序没有完全按文案排列。
2. Block 3 — Shape & Stability 没有真正作为独立 section 出现，QA 可能只是匹配到了导览文字。
3. Block 4 — Strategy Path Diagnostics 实际出现在 Block 5 Robustness & Regime 后面，顺序错误。
4. Scorecard / Redundancy 仍然插在 Block 2 后面，没有放入 Block 6 Constraints & Novelty。
5. PM-59A 从 details 提升为主 block 后，疑似残留多余 `</details>`。
6. Page QA 目前显示 PASS，但它没有检测真实 block 顺序，因此存在假阳性。

---

## 2. 目标真实页面顺序

请在 `scripts/_build_factor_eval_html.py` 的 `renderDetail(fid)` 中，把 factor detail 实际 DOM 顺序调整为：

```text
Header
Evidence Reading Order
Factor Definition
Block 1 — Predictive Ranking Evidence
Block 2 — Monthly Edge Extraction
Block 3 — Shape & Stability
Block 4 — Strategy Path Diagnostics
Block 5 — Robustness & Regime
Block 6 — Constraints & Novelty
Optional Deep-dive Evidence
```

注意：不是只改导览文字，而是实际 HTML section 顺序必须如此。

---

## 3. Block 3 必须真实存在

新增或移动现有 Quantile Shape / Rolling Stability / Decile Shape section，使其前面有明确标题：

```html
<div class="section-divider"></div>
<div class="evidence-label">📊 Block 3 — Shape & Stability / 分层形状与稳定性</div>
<p style="font-size:10px;color:#94a3b8;margin:2px 0">
Is the edge structurally distributed across ranks, or driven by tail/noise?<br>
收益是否沿分位组稳定分布，还是来自尾部、单月或偶然噪声？
</p>
```

Block 3 下放：

- Quantile Shape
- Decile Shape
- Rolling Stability
- Q Spread
- Dir-aware Spearman
- Monotonicity
- Tail Concentration
- Recent ΔIC / Recent ΔLS

不要只让 “Shape & Stability” 出现在 Evidence Reading Order 里。

---

## 4. Block 4 必须移到 Block 5 前面

当前 PM-59A Strategy Path Diagnostics 不能放在 Robustness & Regime 后面。

正确顺序必须是：

```text
Block 3 — Shape & Stability
Block 4 — Strategy Path Diagnostics / 策略路径诊断
Block 5 — Robustness & Regime / 稳健性与条件性
```

PM-59A block 保留以下 badges：

```text
GROSS ONLY
RESEARCH DIAGNOSTIC
NOT LIVE
NOT TRADING
HOURLY PATH
```

conditional 因子保留：

```text
EMPIRICAL DIRECTION
```

if derived/default horizon factor, 保留：

```text
DERIVED HORIZON
```

---

## 5. Block 6 必须承接 Scorecard / Redundancy / Capacity

当前 `scorecardHtml` 和 `Redundancy & Novelty` 不能继续插在 Block 2 后面。必须移动到 Block 6。

Block 6 标题：

```html
<div class="section-divider"></div>
<div class="evidence-label">📊 Block 6 — Constraints & Novelty / 约束与独立性</div>
<p style="font-size:10px;color:#94a3b8;margin:2px 0">
Even if the factor has evidence, is it liquid, non-redundant, and worth further research?<br>
即使因子有证据，它是否具备容量、流动性、独立信息和继续研究价值？
</p>
```

Block 6 下放：

- Capacity / Liquidity
- Redundancy & Novelty
- Marginal Information
- Factor Quality Scorecard

Scorecard 是综合判定，必须放在 Block 6，不要放在 Block 2 后面。

---

## 6. Monthly charts 归属

当前 Monthly RankIC / Monthly LS / Cumulative LS charts 不能漂浮在 Block 2 和 Block 5 之间。

优先方案：

- Monthly RankIC chart 放入 Block 1 的 collapsible subsection
- Monthly LS / Cumulative LS chart 放入 Block 2 的 collapsible subsection

备选方案：

- 三个 raw charts 全部移入 Optional Deep-dive Evidence

任选其一，但必须有清楚归属。

---

## 7. HTML tag 结构检查

检查 `renderDetail(fid)` 中所有 `<details>` / `</details>` 是否配对。

要求：

- PM-59A 主 block 如果不是 `<details>`，就不能有残留 `</details>`
- Optional Deep-dive 的 `<details>` 必须自己闭合
- Period-Level Window Diagnostics 的 `<details>` 必须自己闭合
- Factor Definition 的 `<details>` 必须自己闭合

新增 QA：

```text
count("<details") == count("</details>")
```

如果不相等，FAIL。

---

## 8. PM-59A tooltip 补齐

当前 PM-59A 已有部分 tooltip，但还缺：

- PM-59A Annualized Vol
- Active Sleeves Max
- Return Convention

请在 `scripts/factor_metric_glossary.json` 增加对应 key，或在 HTML builder 中补 `renderTooltip()` 支持。

### 8.1 PM-59A Annualized Vol

中文 tooltip：

```text
基于 PM-59A hourly strategy return path 的标准差 × sqrt(8760)。未扣费，且 sleeve 重叠会影响解释。不是实盘组合波动率。
```

英文 tooltip：

```text
Annualized volatility computed from the PM-59A hourly strategy return path: std(hourly_return) × sqrt(8760). Gross of costs; overlapping sleeves affect interpretation. Not live portfolio volatility.
```

### 8.2 Active Sleeves Max

中文 tooltip：

```text
同一小时内同时处于持有期的最大 sleeve 数。1h/4h/24h/72h 的理论上限分别约为 1/4/24/72。它不是持仓币种数量。
```

英文 tooltip：

```text
Maximum number of active sleeves at the same hour. Expected upper bounds are about 1/4/24/72 for 1h/4h/24h/72h horizons. This is not the number of held symbols.
```

### 8.3 Return Convention

中文 tooltip：

```text
PM-59A 使用 long_mean − short_mean spread。先计算每个 sleeve 的 long basket 均值和 short basket 均值，再对 active sleeves 求均值；不是 symbol-level contribution 的简单平均。
```

英文 tooltip：

```text
PM-59A uses long_mean − short_mean spread. It first computes each sleeve’s long basket mean and short basket mean, then averages active sleeves. It is not a simple symbol-level contribution mean.
```

---

## 9. Page QA 必须加强

修改：

```text
scripts/check_factor_evaluation_page_completeness.py
```

新增真实顺序检查。

从 HTML 中找到以下 marker 的 index：

```text
Evidence Reading Order
Factor Definition
Block 1 — Predictive Ranking Evidence
Block 2 — Monthly Edge Extraction
Block 3 — Shape & Stability
Block 4 — Strategy Path Diagnostics
Block 5 — Robustness & Regime
Block 6 — Constraints & Novelty
Optional Deep-dive Evidence
```

检查实际顺序：

```python
idx_reading_order < idx_definition < idx_block1 < idx_block2 < idx_block3 < idx_block4 < idx_block5 < idx_block6 < idx_optional
```

如果任何 marker 缺失或顺序错误，FAIL。

另外新增检查：

1. `Block 3 — Shape & Stability` 必须出现在 actual section，不只是 Evidence Reading Order 文案。
2. `Block 4 — Strategy Path Diagnostics` 必须早于 `Block 5 — Robustness & Regime`。
3. `Factor Quality Scorecard` 必须在 `Block 6 — Constraints & Novelty` 之后。
4. `Redundancy & Novelty` 必须在 `Block 6 — Constraints & Novelty` 之后。
5. `<details` 数量必须等于 `</details>` 数量。
6. Page QA 最终必须 0 FAIL。

---

## 10. 不要修改

不要改：

- factor formulas
- factor values
- expected_direction registry
- PM-59A computation
- PM-59A summary CSV/JSON
- RankIC / LS / robust diagnostics 数值
- scorecard scoring
- backend workflow

只允许改：

- `scripts/_build_factor_eval_html.py`
- `scripts/factor_metric_glossary.json`
- `scripts/check_factor_evaluation_page_completeness.py`
- generated `reports/site/factor-library/factor-evaluation.html`
- generated page QA report

---

## 11. 执行命令

运行：

```bash
python scripts/_build_factor_eval_html.py
python scripts/check_factor_evaluation_page_completeness.py
```

必须得到：

```text
0 FAIL
```

---

## 12. 最终返回内容

完成后返回：

1. commit hash
2. changed files
3. actual block order
4. `<details>` count 与 `</details>` count
5. PM-59A block index 是否早于 Robustness block index
6. Scorecard block index 是否晚于 Constraints block index
7. Block 3 actual section 是否存在
8. Page QA PASS/FAIL 统计
9. 说明没有重算后端 PM-59A 数据

---

## 13. 关键提醒

请严格以这份 PM 指令和用户附上的 MB 网页为准，不要自己重新设计页面结构。

这不是“把 PM-59A 再新增一个大块”，而是“把现有页面重排成证据链”。
