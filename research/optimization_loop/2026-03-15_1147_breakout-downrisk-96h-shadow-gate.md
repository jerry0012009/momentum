# Breakout：down-risk zone 放宽到 96h 后仍只是远距离 bridge shadow gate

- 时间：2026-03-15 11:47 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 本轮目标：继续只沿 breakout admission 主线补最后一道 gate；不重开 EMA / Fib，不扩新变体，只回答一个更接近 deployment 的小问题：
  - 如果把当前 blocker 的 `down-risk zone`（pure `down` + 会在未来滑进 pure `down` 的 bridge）继续放宽到更长窗口，`mixed-tail overlay` 能不能更诚实地写成 near-down protective policy？

## 先检查了什么

- 已检查 `git status --short`：worktree 很脏，但按要求继续推进，不把无关改动当失败条件。
- 已对照：
  - `docs/AUTO_OPTIMIZATION_LOOP.md`
  - `docs/TODO.md`
  - 最近 breakout 连续记录，确认当前 blocker 仍是 `pure-test / down-tail honesty`，而不是再堆 wording。

## 本轮完成（小而完整）

### 1) 把 down-risk zone 审计从 `6/12/24h` 扩到 `48/72/96h`

在 `scripts/build_support_breakout_v0_reports.py` 中，继续沿已有 `summarize_pair_downrisk_zone_audit(...)` 扩展：

- 默认主候选：`avoid_fluctuating_eth_sol_pair_halfsize`
- shadow 观察项：`avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay`
- lead hours：从原先的 `[6, 12, 24]` 扩到 `[6, 12, 24, 48, 72, 96]`

输出 artifacts：

- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downrisk_zone_audit_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_downrisk_zone_audit_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_downrisk_zone_audit_compare_20bps.csv`

### 2) 把结果落回 breakout 主报告

更新：

- `reports/site/factors/support_breakout_v0_h24/report.html`

新增/改写的 deployment-facing 读法：

- default pair candidate 在 `12/24/48h` 的 risk-zone 里仍是 `0 coverage`；
- 到 `72/96h` 才开始擦到少量 bridge；
- mixed-tail 也是同样模式，而且 pure `down` 命中仍是 `0/63`；
- 因此 mixed-tail 现在最多只能算 `远距离 bridge shadow gate`，不是 near-down protective gate。

### 3) 同步 TODO / plans 入口

已更新：

- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

对应条目已标记为 `[x]`，时间戳为 `2026-03-15 11:47 UTC`。

## 关键结果

### 默认 `pair halfsize`（相对 gate-only）

- `12h`：`0/74`
- `24h`：`0/86`
- `48h`：`0/109`
- `72h`：`13/164`（但全是 bridge，pure `down` 仍 `0/63`）
- `96h`：`14/177`（仍全是 bridge，pure `down` 仍 `0/63`）

### `down+flat mixed-tail overlay`（相对 default pair）

- `12h`：`0/74`
- `24h`：`0/86`
- `48h`：`0/109`
- `72h`：`5/164`（bridge `5/101`，pure `down` `0/63`）
- `96h`：`12/177`（bridge `12/114`，pure `down` `0/63`）

## 这轮新增了什么判断

这轮把 mixed-tail 的诚实边界又收紧了一格：

- 它不是完全“碰不到 down-risk”；
- 但要把窗口放宽到 **3~4 天**，才开始擦到一点 bridge；
- 而且就算这样，pure `down` 覆盖仍然是 `0/63`；
- 所以它还不能诚实写成 near-down protective policy，只能继续算 `shadow-only` 观察项。

一句话：

> mixed-tail 现在最多只是“远距离 bridge shadow gate”，不是能补掉 breakout admission hard gap 的 protective clearance。

## 对 breakout 主 verdict 的影响

**不改写主 verdict。**

- `default pair halfsize`：继续保留为 breakout 默认 admission 候选
- `mixed-tail overlay`：继续只配 `shadow-only`
- `breakout` 总 verdict：继续维持 `shadow-admission queue / one_more_gate`
- 当前最硬 blocker：仍是 `pure-test / down-tail honesty`，尤其是 `pure down coverage` 还停在 `0/63`

## 修改文件

- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downrisk_zone_audit_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_downrisk_zone_audit_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_downrisk_zone_audit_compare_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

## 最小验证

已执行：

```bash
python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py /root/clawd/jerry/momentum/scripts/build_plans_site.py
python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py
python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py
```

结果：通过。

## Git / hygiene 备注

- 当前仓内存在大量与本轮无关的既有脏改动与未跟踪文件；这轮按要求继续推进，但没有把无关改动混入本轮判断。
- 本轮**未提交**：当前 worktree 跨主题脏文件过多，且全量重建会刷新很多无关页面，不适合安全做 selective commit。若后续要提交，应先隔离只包含本轮 breakout admission 相关文件的最小提交。
