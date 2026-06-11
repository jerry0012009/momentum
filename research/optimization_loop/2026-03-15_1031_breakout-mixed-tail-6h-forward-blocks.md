# Breakout mixed-tail 6h forward blocks

- 时间：2026-03-15 10:31 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 本轮目标：沿 `down+flat mixed-tail` 再补一层更前瞻的 shadow honesty，直接回答它能否升格成更诚实的 conditional policy。

## 本轮完成（小而完整）

### 1) 新增 mixed-tail strict pure-test tail 的 non-overlap 6h forward blocks

在 `scripts/build_support_breakout_v0_reports.py` 新增并接线：

- `summarize_hourly_pair_forward_blocks_hours(...)`
- 对象：`pair halfsize`（基线） vs `pair + down+flat mixed-tail overlay`
- 口径：strict pure-test tail 内 non-overlap `6h` blocks
- 输出 artifact：
  - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_forward_blocks_6h_20bps.csv`

### 2) 将结果落到 breakout 主报告

在 `reports/site/factors/support_breakout_v0_h24/report.html` 新增一节：

- “如果把这段 strict pure-test mixed tail 压成更前瞻的 non-overlap 6h blocks，结论还会一致吗？”

用途：避免只看 cumulative checkpoints，改成更前瞻、不可重叠的小窗 forward 读法。

### 3) 同步 TODO

在 `docs/TODO.md` breakout 主线下新增一条 `[x]`（10:31 UTC），把这轮结论写进 deployment-facing 连续记录。

---

## 关键结果

本轮新增的 `6h` non-overlap blocks（strict pure-test mixed tail）结果为：

- 正向：`2/4`
- 负向：`2/4`

分块 delta（相对默认 `pair halfsize`）：

1. block#1：约 `+0.41pp`
2. block#2：约 `-0.29pp`
3. block#3：约 `+0.11pp`
4. block#4：约 `-0.14pp`

对应的 deployment-facing 读法：

- mixed-tail overlay **不是**“只有一格 lucky pocket”；
- 但它也**不是**“每个前瞻小段都稳定更优”的 conditional policy；
- 因此当前仍应维持：`shadow-only mixed gate`，不能改写 breakout 总 verdict（`one_more_gate`）。

---

## 对主问题的推进价值

这轮不是继续堆 wording，而是把 mixed-tail 在 strict pure-test tail 的证据从“累计仍为正”进一步压到“更前瞻 non-overlap 小窗”。

得到的新增信息是：

- cumulative 口径看起来能站住；
- 但 non-overlap 前瞻口径下仍出现阶段性回吐（`2/4` 负）；
- 所以它目前更像“方向没死但稳定性不足”的候选 gate，而非可直接放行的 policy patch。

---

## 修改文件

- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_forward_blocks_6h_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

## 最小验证

已执行：

```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py
python3 scripts/build_support_breakout_v0_reports.py
python3 -m py_compile scripts/build_plans_site.py
python3 scripts/build_plans_site.py
```

结果：通过。

## Git / hygiene 备注

- 当前工作区存在大量与本轮无关的既有脏改动与未跟踪文件；已按要求继续推进本轮任务，但不混提无关改动。
- 本轮未提交：当前仓内跨主题脏文件过多，不适合直接安全 selective commit；后续若提交应先隔离仅本轮 breakout 相关文件。
