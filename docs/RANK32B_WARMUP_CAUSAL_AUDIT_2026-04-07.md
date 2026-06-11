# Rank32B warmup / causal audit (2026-04-07)

## 这次审计在看什么

目标不是重新评价 32b 有没有 alpha，而是先把 **哪些页面 / 产物能继续信，哪些应该先撤下** 讲清楚。

重点排查两类问题：

1. **warmup 口径错误**
   - 本来只是想给指标一个有限 warmup
   - 结果实现里把 `horizon` 又额外吃进去一次
   - 让回测实际覆盖窗口比名字写的更长
2. **future / hindsight 混淆风险**
   - 尤其是 preview-family 页面
   - 即便它们不一定是严格意义上的 future leak，也容易和官方 `official-close` 主口径混在一起，被误读成同一层级证据

---

## 发现 1：`backtest_rank32b_global_shadow_live_like.py` 存在 warmup 窗口放大错误

受影响脚本：

- `scripts/backtest_rank32b_global_shadow_live_like.py`

旧实现里：

- `signal_fetch_days = horizon_days + lookback_days`
- 然后又做：`warmup_start = cutoff - signal_fetch_days`

这会把实际抓数窗口放大成接近：

- `2 * horizon + lookback`

而不是更自然的：

- `horizon + lookback`

### 直接后果

以 720d 为例，脚本名义上是“720d live-like”，但实际会把分钟级历史往前再拖很大一截，导致：

- 运行时间异常拉长
- 结果的时间范围不再等于页面文案说的那个范围
- `180d / 365d / 720d` 这些 long-window live-like 产物不适合继续当 canonical 结果展示

### 已采取动作

- 已修正该脚本 warmup 计算
- 新版会把 warmup 限制在 `lookback_days / refresh_tail_days` 这一层，而不是把 `horizon` 再重复吃一遍

---

## 发现 2：preview-family 页面不该继续挂在 32b 主路径里

这批页面更适合被视为：

- 历史研究页
- preview / parity / reconciliation 研究材料
- 非当前 `official-close only` 主口径

它们的问题不一定都是“严格的 future leak”，但它们会制造一种更糟的风险：

> **把 preview 研究、clean replication、recent reconciliation 和 current official-close 主页面混成一套证据。**

因此这次把它们统一从主路径里移出，按 **archive / research-only** 处理。

### 已移出主路径的页面 / 产物家族

页面：

- `reports/site/factors/rank32b_unclosed15m_preview_backtest/`
- `reports/site/factors/rank32b_corrected_preview_extended_validation/`
- `reports/site/factors/rank32b_recent90_corrected_preview/`
- `reports/site/factors/rank32b_recent90_reconciliation/`
- `reports/site/factors/rank32b_preview_delay1m_study/`

对应研究产物：

- `reports/artifacts/rank32b_preview_delay1m_study/`
- `reports/artifacts/rank32b_corrected_preview_extended_validation/`
- `reports/artifacts/rank32b_preview_signal_parity/`
- `reports/artifacts/rank32b_recent90_corrected_preview/`
- `reports/artifacts/rank32b_recent90_reconciliation/`

---

## 发现 3：`rank32b global live-like stability` 页需要降级成 short-window only

保留：

- short-window official-close 稳定性
- recent-180d 稳定性可视化
- 当前 official live 状态

撤下：

- 旧 `180d / 365d / 720d` live-like long-window 数值
- 基于旧 long-window ledger 的月度拆解表

原因很简单：

> 这些 long-window 数值来自 warmup 审计前的 backtest 产物，不应继续摆在主页面上让人误以为它们仍然有效。

---

## 现在的主路径应该怎么读

### 继续保留为主路径

- `reports/site/factors/rank32b/report.html`
  - 32b 统一入口页
- `reports/site/factors/rank32b_canary/report.html`
  - current live / canary 运行页
- `reports/site/factors/rank32b/transparency.html`
  - 交易逻辑透明页
- `reports/site/factors/rank32b/decomposition.html`
  - baseline / components / ablation 结构拆解
- `reports/site/factors/rank32b/global_live_like_stability.html`
  - **仅 short-window only** 的稳定性页

### 归档 / research-only

- 所有 preview-family 页面
- 所有基于旧 warmup 口径的 long-window live-like artifacts

---

## 这次收口后的原则

以后 32b 页面分三层：

1. **official / canonical**
   - live
   - official-close backtest
   - current stability
2. **audit / honesty**
   - warmup 修正
   - causal / timing / signal-definition 说明
3. **archive / research-only**
   - preview-family
   - parity / reconciliation 历史页
   - 已被新口径替代的旧产物

这样以后用户打开页面时，不会再碰到：

- 页面还在，但其实口径已经失效
- preview 研究页看起来像 current official page
- long-window 数字其实基于旧 warmup 代码，却没人提醒

---

## 下一步建议

1. 用修正后的 backtest 脚本重新跑：
   - 180d
   - 365d
   - 720d
2. 产出新的 canonical ledger：
   - `paper_trades_180d/365d/720d`
   - `monthly_summary_180d/365d/720d`
3. 再恢复 long-window 稳定性页里的长期卡片

在这之前：

> **主路径只讲 short-window official-close + current official live。**
