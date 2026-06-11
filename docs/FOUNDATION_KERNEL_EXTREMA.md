# FOUNDATION_KERNEL_EXTREMA

当前保留的成熟底层，只做两层：

1. **endpoint / non-repainting Nadaraya-Watson smoothing**
2. **confirmed extrema with raw-price anchoring**

暂时**不**把通道、突破、形态业务逻辑写死到正式模块里。

---

## 为什么收缩到这两层

因为这两层更容易直接对齐外部成熟实现：

- `PyIndicators` 的 `nadaraya_watson_envelope.py`
- `PyIndicators` 的 `swing_structure.py` / pivot confirmation 逻辑

而“如何从 extrema 继续做 channel / breakout / pattern”是下一阶段的研究课题，
不应该在当前阶段拍脑袋扩展成正式策略模块。

---

## 代码来源审计

### A. 已对齐外部成熟逻辑的部分

#### 1. `src/momentum/factors/endpoint_nadaraya_watson.py`
- 性质：本仓库自写的轻量实现
- 参考来源：`PyIndicators / nadaraya_watson_envelope.py`
- 当前只保留：
  - endpoint / past-only kernel smoothing
  - middle line（平滑主线）
- 当前不保留：
  - envelope upper / lower

#### 2. `src/momentum/factors/confirmed_extrema.py`
- 性质：本仓库自写的轻量实现
- 参考来源：`PyIndicators / swing_structure.py` 与 pivot confirmation 思路
- 当前保留：
  - extrema 必须延迟确认
  - 结构标签：`HH / LH / HL / LL`
  - extrema 的价格锚点使用原始 `high / low`
- 当前口径：
  - **平滑线决定“何时确认”**
  - **原始价格决定“锚点值是多少”**

### B. 已明确降级 / 暂缓的部分

以下内容不再视为当前正式成果：

- `channel_lines.py`
- `kernel_channel_breakout.py`
- 基于 extrema 直接推导 channel / breakout / failed-breakout 的业务层

原因不是“永远不做”，而是：
- 这部分需要单独查文献 / 查成熟仓库
- 需要更清晰的几何定义与验证方法
- 不适合在当前阶段硬塞进正式策略层

---

## 当前网页报告应该展示什么

报告只展示这两层：

1. 原始价格 close
2. endpoint NWE 平滑线
3. confirmed highs / confirmed lows
4. 最近若干 extrema 的来源表格

并且明确说明：

- 图上的 extrema 锚点值来自原始 `high / low`
- 不是平滑线上的值
- 但这些 extrema 只能在确认 bar 之后才可用

---

## 下一步建议

如果后面要继续研究：

### 方向 1：先查外部现成实现
- `PyIndicators` 还有哪些与 pivot / trendline / pattern 相关模块
- 其他库如何从 extrema 做 trendline / channel / pattern

### 方向 2：再查文献
- Lo, Mamaysky, Wang (2000) 这种“平滑 + 极值 + 形态识别”主线
- 更具体的“trendline / channel / breakout”文献与实现

### 方向 3：最后再写业务层
- 只有在外部逻辑和定义都更清楚后，才写正式策略模块

---

## 一句话总结

当前正式保留的是：

**NWE 平滑 + confirmed extrema（raw high/low 锚点）**

当前正式暂缓的是：

**channel / breakout / pattern 业务层**
