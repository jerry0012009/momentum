# 2026-03-15 18:25 UTC｜EMA+PSAR overlay deployment matrix

## 为什么这次选这个
- 先检查了 repo 状态、`docs/TODO.md`、以及最近几轮 auto log。最近两轮 EMA 已经把 `A股 daily overlay audit` 和 `closure board sync` 做出来了；继续补近义 wording 价值很低。
- breakout 线这边，同一样本内的 retrospective admission slicing 已基本冻结，当前 steering 也明确说：如果没有新的 `pure-test / down-tail` forward honesty，就不要继续切更细 micro-slices。
- 因此这轮选一个更 deployment-facing 的小收口：把已经存在的 `Crypto 60m overlay` 结果和刚做完的 `A股 daily overlay` 审计压成同一张 `EMA + PSAR` deployment matrix，直接回答 **哪些 pocket 还能继续 shadow、哪些必须拒绝默认接线**。

## 本轮主点 / 子点
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`EMA + PSAR` 最小组合研究收口成 deployment matrix

## 做了什么改动
1. 修改 `scripts/build_ema_psar_raw_alpha_report.py`
   - 新增 `build_ema_psar_overlay_deployment_matrix(...)`，把已有两类证据合并成一张 project-facing matrix：
     - `Crypto 60m` rolling overlay slice
     - `A股 daily` strict-holdout overlay audit
   - 生成新工件：
     - `reports/artifacts/ema_psar_raw_alpha/ema_psar_overlay_deployment_matrix.csv`
2. 更新 `EMA / PSAR Raw Alpha Focus Report`
   - 新增 `Q35f`，把 `EMA + PSAR` 当前最诚实的 deployment 读法压成一张矩阵，而不是继续分散在多个局部段落里。
3. 更新 `docs/TODO.md`
   - 将 `做一版 EMA + PSAR 的最小组合研究` 标记为 `[x]`。
   - 补上本轮固定下来的项目级口径，避免它继续停留在“协议已写好，但还没形成 first-pass 结论”的状态。
4. 重新生成相关页面
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/plans/momentum_todo.html`
   - `reports/site/plans/index.html`
   - `reports/site/plans/report.html`

## 验证 / 证据
最小必要验证：
- `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py`
- `python3 scripts/build_ema_psar_raw_alpha_report.py`
- `python3 scripts/build_plans_site.py`

结果：均成功。

本轮固定下来的关键证据：
- `Crypto 60m`：overlay 约仅 `4/30` 窗口改善，median net20 delta 约 `-6.26pp`，median trade delta 约 `+46`，因此只能继续视为 `reject_rescue_overlay`，不得拿来 reopen `60m fail pocket`。
- `创业板ETF 1d`：约 `75%` strict holdout 改善，median net20 delta 约 `+2.00pp`，median trade delta 约 `+13`，可以保留为 `primary lane` 的 `shadow protective` 候选，但不改写默认 `EMA` 持有规则。
- `沪深300ETF 1d`：约 `25%` holdout 改善，median net20 delta 约 `-1.51pp`，因此 `PSAR` 不能当 shadow promotion patch。
- `A股 daily overall`：约 `50%` holdout 改善，median net20 delta 约 `-0.38pp`，所以项目级默认规则仍应保持：`EMA` 负责方向与默认持有，`PSAR` 不升格成 family-wide default overlay。

## 为什么这轮算有效推进
- 这轮不是再补近义 board，而是把已经分散在 `Q14/Q15/Q35e` 的组合证据压成一张 deployment matrix。
- 这样 Jerry 现在可以更直接判断：
  - `PSAR` 哪里还能继续 shadow；
  - 哪里必须明确拒绝默认接线；
  - `EMA + PSAR` 这条线目前是否已经足够诚实到可以当默认组合（答案：还不行）。
- 这也把一个长期挂着的 TODO（最小组合研究）正式收口成 first-pass verdict，而不是继续停在“协议存在、局部切片很多、但项目级结论没钉死”的状态。

## 风险 / 边界
- 这仍是 `first-pass deployment matrix`，不是完整的参数化 `EMA + PSAR` 组合研究，更不是实盘级 execution proof。
- 当前结论只够支持：
  - `创业板ETF 1d` 保留 `PSAR` 为 `shadow protective watch`；
  - 其余 pocket 继续拒绝默认 overlay 接线。
- 这并不证明 `PSAR` 在所有 non60m 场景都无用，只是说明它当前还不配升格成项目级默认 protective layer。
- 构图阶段仍有中文字体 warning，但不影响 CSV / HTML 结果。

## 下一步建议
- `EMA` 下一刀默认继续等真实 `market-close refresh / week-1 review`，不要再回头补近义 overlay wording。
- 如果后续还继续 `PSAR overlay`，默认只沿 `创业板ETF 1d` 这条 primary shadow protective 观察位推进；不要拿它去 reopen `Crypto 60m`，也不要把它偷渡成 `沪深300ETF 1d` 的 promotion patch。
- breakout 线若没有新的 `pure-test / down-tail` forward evidence，默认继续保持 freeze，不要回到同样本 micro-slicing。

## 提交情况
- 本轮未提交。
- 原因：当前 repo 存在大量与本轮无关的既有脏改 / 未跟踪文件；为了避免把历史改动一起打包，本轮只落地产物与日志，不做 selective commit。
