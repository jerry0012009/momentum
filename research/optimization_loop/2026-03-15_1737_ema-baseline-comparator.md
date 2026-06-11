# 2026-03-15 17:37 UTC — 把 EMA 正式钉成结构层默认 baseline 比较尺

## 为什么这次选这个
- 先做了环境观测：`git status --short`、最近 optimization loop 记录、`docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md`。
- 当前 steering 仍要求默认优先最接近 paper 的对象；但 EMA live-ledger 的下一笔真实推进还在等下一根 completed bar，上一轮也已把这一点压成 `refresh_clock_audit`。
- 在不伪造不存在的新 refresh / week-1 review 的前提下，本轮优先从 `docs/TODO.md` 里挑一个仍直接服务 deployment / admission 的小任务：**把 `EMA` 正式钉成后续 breakout / retest / confirmation 的默认 baseline，比的是“谁能更诚实地拿到 paper admission / deployment seat”，不是再比一句泛泛 alpha 叙事。**

## 本轮主点 / 子点
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`support_breakout_v0 / Fibonacci` 相对 EMA 的 deployment-facing 排位澄清

## 做了什么改动

### 1) 在 closure board 新增一张显式 `structure vs EMA baseline` 对照表
- 修改：`scripts/build_alpha_closure_board_report.py`
- 新增 artifact：`reports/artifacts/alpha_closure_board/structure_vs_ema_baseline_v1.csv`
- 新增网页区块：`reports/site/factors/alpha_closure_board/report.html`

这张表现在直接回答 6 件事：
1. 每条线相对 EMA 的当前排位；
2. EMA 在这张比较里的角色；
3. 当前是否已经证明“结构层增量价值”；
4. 为什么还不能高于 EMA；
5. 下一刀什么才算有效比较；
6. 哪些线已经退出 baseline seat 竞争。

### 2) 把 `docs/TODO.md` 的 baseline 任务正式勾掉
- 修改：`docs/TODO.md`
- 已把：
  - `把 EMA 作为后续 breakout / retest / confirmation 研究的默认 baseline，对比“结构层有没有带来增量价值”`
  - 标记为 `[x]`
- 并补上当前固定口径：
  - `EMA baseline family` = 默认 baseline / deployment reference seat
  - `support_breakout_v0` = 仍是 `conditional alpha / one_more_gate`
  - `Fibonacci` = `archive / optional filter`

### 3) 把“比较标准”从泛泛叙事收紧到 deployment-facing 问题
本轮不是再补一页近义 closure-copy，而是把后续结构层默认比较问题写死成：
- 它有没有比 EMA **更早、更诚实**地拿到 `paper admission`？
- 如果没有，它至少有没有清楚到值得和 EMA **并列保留**？
- 如果两者都没有，就不该继续占主资源。

## 验证 / 证据
最小必要验证：
1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_alpha_closure_board_report.py`
3. `python3 scripts/build_plans_site.py`

关键结果：
- `reports/artifacts/alpha_closure_board/structure_vs_ema_baseline_v1.csv` 已生成。
- `alpha_closure_board` 现在不只回答“谁最接近 paper”，还直接回答“结构层现在有没有资格挑战 EMA baseline seat”。
- `TODO` 镜像页会同步反映该任务已完成，不再把它留成口头要求。

## 当前更清楚的项目级结论
- `EMA baseline family` 继续占据默认 baseline / deployment reference seat；短期内谁想继续吃主资源，先回答能不能比它更诚实地进 paper。
- `support_breakout_v0` 现在仍不能高于 EMA：不是因为它没 alpha 感，而是因为它还卡在 `one_more_gate`，且 `pure down coverage = 0/100`、`pre-down bridge = 0`、pure-test 前半段仍只有 very thin edge。
- `Fibonacci` 当前更不该继续拿来挑战 baseline：它连 structure 主线内部都不是胜出者，当前更诚实的位置仍是 `archive / optional filter`。

## 风险 / 边界
- 本轮没有制造新的 forward alpha 证据，也没有伪造 EMA 的下一笔 live refresh。
- 这轮完成的是**比较尺固定**，不是“结构层已证明优于 EMA”。
- 后续如果 breakout / retest 还要继续推进，默认必须用这张 baseline 尺回答更硬的问题，而不是继续补近义 wording。

## 执行层 hygiene
- `git status --short` 只作为环境观测使用；当前 worktree 仍存在大量与本轮无关的历史脏改 / 未跟踪文件。
- 本轮没有去碰 `pytrendline_event_validation_v3` reopen，也没有回到 breakout 同一样本的 retrospective micro-slicing。

## 下一步建议
1. EMA 线：继续等下一根真实 completed bar，沿同一张 live ledger 落下下一笔 `market-close refresh`。
2. breakout 线：只有拿到新的 `pure-test / down-tail` shadow/holdout honesty，才配继续争取与 EMA 并列；否则默认维持 `one_more_gate`。
3. Fibonacci 线：继续停在 archived / optional filter，不再抢主资源。

## Commit hash
- 本轮未提交。
- 原因：当前仓库存在大量与本轮无关的脏改 / 未跟踪文件，而且本轮涉及的目标文件本身也处在持续演化区；为避免把历史未清改动一起打包，本轮保持不提交。