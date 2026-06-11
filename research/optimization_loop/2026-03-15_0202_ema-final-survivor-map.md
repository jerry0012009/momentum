# EMA baseline family final survivor map（收口落页）

## 本轮认领

- 主点：`EMA / PSAR raw alpha focus`
- 具体任务：完成 TODO 接力棒第 1 项——把分散在 `60m rolling`、`A股 weekly strict holdout`、`A股 daily strict holdout`、以及 nonfrontier non60m backstop 的结论压成一版可执行的 **final survivor map**，避免继续停在“daily 暂保留”的半悬空状态。

## 为什么这次选这个

1. 这是当前 `docs/TODO.md` 接力棒 Top 1，且已有足够现成结果可直接收口，不需要重跑重型下载。
2. `EMA 60m gross vs 20bps` rolling 与 `EMA 60m + PSAR overlay` 的真实结果已经落页；`A股 weekly/daily strict holdout` 也已完成。
3. 下一步最缺的不是新切片，而是把“谁保留、谁降级、谁移出”写成固定边界，避免 bot3 后续反复改写同一结论。

## 做了什么改动

1. **脚本层（新增 final survivor map 产物）**
   - 更新：`scripts/build_ema_psar_raw_alpha_report.py`
   - 新增函数：`build_ema_final_survivor_map(...)`
   - 新增 artifact：
     - `reports/artifacts/ema_psar_raw_alpha/ema_baseline_family_final_survivor_map.csv`
   - 报告新增章节：`Q22`（final survivor map），并把原 `Q22/Q23` 顺延为 `Q23/Q24`。

2. **网页表达层**
   - 更新：`reports/site/factors/ema_psar_raw_alpha/report.html`
   - 在页内明确写死当前 family 边界：
     - `60m crypto` = fail pocket（移出）
     - `A股 weekly frontier` = remove / PSAR-lean（移出）
     - `沪深300ETF 1d` = mixed / watch（保留但降级）
     - `创业板ETF 1d` + `贵州茅台 1d+1wk` + `美股 1d+1wk` + `Crypto 1d+1wk` = keep

3. **入口/总览同步**
   - 更新：`scripts/build_alpha_closure_board_report.py`
   - 更新：`reports/site/factors/alpha_closure_board/report.html`
   - 将 EMA 卡片证据同步为“已落 final survivor map”的最新口径，避免继续把 `60m`/`A股 weekly` 当 hopeful 证据。

4. **TODO 收口同步**
   - 更新：`docs/TODO.md`
   - 更新：`reports/site/plans/momentum_todo.html`
   - 已把接力棒第 1 项标记为 `[x]`，并补充 final survivor map 的固定边界与 artifact 路径。

## 验证 / 证据

已执行：

- `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_ema_psar_raw_alpha_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_plans_site.py`

验证命中：

- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现：
  - `Q22. 把前面的结果压成一张 final survivor map...`
  - `EMA baseline family final survivor map` 表格
- 新 artifact 已生成：
  - `reports/artifacts/ema_psar_raw_alpha/ema_baseline_family_final_survivor_map.csv`
- `docs/TODO.md` 对应接力棒项已打勾，并在长进度区补入 final map 结论。
- `alpha_closure_board` 已同步“final survivor map 已落页”的证据与 next-step 口径。

## 风险 / 边界

1. final survivor map 中的 nonfrontier backstops（`贵州茅台 1d+1wk`、`美股 1d+1wk`、`Crypto 1d+1wk`）当前主要依据长样本 gross/cost 厚度与既有结果，不等于它们都已完成和 A股 frontier 同等级 strict holdout 复核。
2. 本轮目标是“边界收口与表达固定”，不是新增回测切片；因此没有引入额外下载或新市场扩样本。

## 下一步建议

- EMA 线若继续，优先挑战 remaining keep/watch pockets 的更严格 honesty（先从 `沪深300ETF 1d` 这类 mixed pocket 开始），而不是回头重讲 `60m` 或 `A股 weekly`。
- breakout 线按当前接力棒推进：把 `pair-conditioned halfsize` 推到更严格 walk-forward / holdout / portfolio honesty。

## Commit

本轮**未提交**。

原因：当前 repo 工作区存在大量与本轮无关的既有脏改动，且本轮涉及文件（尤其 `docs/TODO.md`、两份脚本、两份站点页）在本轮开始前已处于 dirty 状态；此时做 selective commit 不能可靠保证仅打包本轮增量。