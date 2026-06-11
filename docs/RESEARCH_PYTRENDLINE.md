# RESEARCH_PYTRENDLINE

## 目标
把外部成熟实现的趋势线 / breakout 研究能力接进 `momentum`，但保持来源和边界清晰。

---

## 为什么这次选 `pytrendline`

- 仓库：<https://github.com/ednunezg/pytrendline>
- License：MIT
- 核心能力：
  - pivot points
  - support / resistance trendlines
  - breakout lines
  - duplicate grouping / scoring

这比我们自己从零开始猜“通道/趋势线如何画”更合适。

---

## 为什么不直接搬 `PyIndicators` 的 breakout navigator

不是因为它技术不行，而是因为**代码来源边界不够干净**。

我们审计到：
- `PyIndicators` 仓库整体可用；
- 但 `trendline_breakout_navigator.py` 文件头注明它是从 **LuxAlgo** 移植；
- 且带有 **CC BY-NC-SA 4.0 / analytical use only** 之类限制语义。

所以：
- **NWE / swing_structure** 可以继续参考；
- **trendline_breakout_navigator.py** 不建议直接搬到正式项目里。

为了避免来源争议，这次改用 MIT 的 `pytrendline`。

---

## 当前落地方式

### 1. `src/momentum/factors/pytrendline_bridge.py`
这是一个很薄的 adapter：
- 负责接 `pytrendline`
- 补 pandas 3 的兼容层（`DataFrame.append`）
- 限制扫描窗口，避免对超长 5m 样本做 O(N^3) 穷举

### 2. 当前定位
这是**研究功能**，不是正式交易信号。

它回答的问题是：
- 在最近一个分析窗口里，`pytrendline` 找到了哪些 support / resistance lines？
- 哪些线被它判成 breakout？
- 这些线的 points / score / breakout 属性是什么？

---

## 运行边界

`pytrendline` 本身是穷举扫描，复杂度较高。

所以当前约束为：
- 仅在最近窗口运行（例如 `48 / 96 / 144` 根 5m bars）
- 更适合：
  - offline analysis
  - report / chart inspection
- 不适合：
  - 大样本全量增量扫描
  - 高频实时信号引擎

---

## 下一步

1. 先做网页 report，把 support / resistance / breakout 结果画出来
2. 再决定要不要把“趋势线突破”往正式 signal 层推进
3. 推进前，先补：
   - 来源审计
   - 参数稳定性
   - bar-by-bar 可用性检查
