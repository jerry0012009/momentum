# 项目级 paper→小资金实盘 promotion gate v1

- 时间：2026-03-15 08:46 UTC
- 主线：deployment-facing / admission
- 对应 TODO：`项目级：定义 paper trading -> 小资金实盘 promotion gate`

## 为什么这次选这个

先检查了 `git status --short`、最近几轮 optimization loop 记录、`docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md`。

当前 breakout 线虽然仍是高优先级，但最近几轮已经连续沿 `mixed-tail` 补了 forward / walk-forward / conditional honesty；这几轮都在同一 admission gap 附近继续压实证据。按当前 steering，这一轮更值得补的是**更接近 deployment 的剩余硬门槛**，避免继续在同一 breakout 子枝上堆近义表达。

`docs/TODO.md` 里当前最直接、且确实还没落地的 deployment-facing 小任务，就是：

- **项目级：定义 `paper trading -> 小资金实盘` promotion gate**

这件事的价值不在于“让项目显得更像要上实盘”，而在于把当前 closure / admission 结论真正接成**统一的 forward 守门规则**：
- paper 至少要跑多久；
- 回撤多大就不能谈 live；
- 哪些情况要停机；
- small-live 资金上限是多少；
- 触发什么条件必须 rollback。

## 本轮完成内容

1. 扩展 `scripts/build_alpha_closure_board_report.py`
   - 新增项目级 `promotion gate v1` 数据结构；
   - 新增 artifact 导出：
     - `reports/artifacts/alpha_closure_board/paper_live_promotion_gate_v1.csv`
   - 在 `alpha_closure_board` 页面新增一整块 `Paper trading → 小资金实盘 promotion gate（v1）` 表。

2. 刷新 closure board 页面
   - 更新：`reports/site/factors/alpha_closure_board/report.html`
   - 把原先“离小资金实盘还很远”的泛泛表述，改成有明确硬门槛的 deployment-facing 口径。

3. 更新 `docs/TODO.md`
   - 将 `项目级：定义 paper trading -> 小资金实盘 promotion gate` 标记为已完成；
   - 补入当前固定口径与对应 artifact 路径。

4. 重建 plans 镜像
   - 执行 `python3 scripts/build_plans_site.py`，让 `plans/momentum_todo.html` 同步反映这条完成项。

## 结果摘要

### 当前固定下来的项目级 promotion gate v1

#### 1) 进入 paper / shadow 的前置条件
- 只适用于已经过 `Step 2`、且已有 `candidate spec + operating spec + monitoring board / runbook` 的对象；
- 当前更像先给 `EMA` 用；`breakout` 仍需先清掉 `one_more_gate`；
- 启动时真实资金必须为 `0`，先跑 paper / shadow 并行记账。

#### 2) 从 paper 进入 small-live review 的最小要求
- 至少满足：`30` 个自然日 + `>=20` 个 closed decision cycles / trades；
- 若是更慢的策略，则至少：`60` 个自然日 + `>=8 trades`；
- `paper max drawdown` 不得突破研究基线的 `max(1.25x, +3pp)` 容忍带；
- 不能连续两次 review 都落在 monitoring board 的 `red` 区；
- 若 paper 累计回撤跌破 `-5%`，或触发 drawdown guardrail，就冻结 promotion review。

#### 3) small-live pilot 的资金与 kill switch
- 单候选 live pilot 先限制在：
  - `<= 总可部署资金 1%`
  - 且 `<= 该策略 sleeve 10%`
- 单 symbol / pair 不得超过 pilot capital 的 `50%`；
- 任一 kill switch 触发即停：
  - `drawdown breach`
  - `live vs paper mismatch > 5pp`
  - `连续两次 red review`
  - `数据 / 执行异常`

#### 4) rollback 规则
- 任一 kill switch 触发，立即退回 `paper only`；
- rollback 后至少再观察 `10` 个交易日或 `5` 个 closed trades，才可重新申请 live review；
- 同一 candidate 若 `90` 天内两次触发 kill switch，自动降回 `Step 3`，等待人工重新立项。

## 这意味着什么

这轮最重要的推进，不是新增一页“看起来更完整”的说明文，而是把当前项目从：
- 只会说 `closest to paper / one_more_gate / park`

推进到：
- **即使未来真的开始 paper / shadow，也必须按哪一套最小前瞻守门规则走**。

更具体地说：
- `EMA` 现在不再只是“最接近 paper”这句抽象判断，而是已经知道：**先补 runbook，然后按 promotion gate v1 跑真实 paper**；
- `breakout` 也不再只是“以后也许可以 paper”，而是明确知道：**在没清掉 `one_more_gate` 前，连 paper/shadow start 都不该启动**；
- `small live` 也不再是空泛的未来词，而是被压成了 `0 -> paper -> review -> tiny live -> rollback` 这条保守路径。

因此这轮属于真正的 deployment-facing 收口，而不是 closure wording。

## 本轮验证

已执行：
- `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

结果：成功。

抽样核对：
- `reports/artifacts/alpha_closure_board/paper_live_promotion_gate_v1.csv` 已生成；
- `reports/site/factors/alpha_closure_board/report.html` 已出现 `Paper trading → 小资金实盘 promotion gate（v1）` 表；
- `docs/TODO.md` 对应任务已改为 `[x]`。

## 风险 / 边界

- 这是一版**项目级保守 gate v1**，不是“任何策略都适用”的数学真理；后续若真实 paper 运行暴露出频率差异或执行细节问题，可以再校准。
- 本轮没有新增任何策略收益证据，也没有改变 breakout / EMA 的 admission verdict；改变的是**它们之后若真往前走，必须遵守的统一 forward 守门规则**。
- 当前 worktree 里仍有大量与本轮无关的历史脏改动 / 未跟踪文件；这轮只围绕 closure board / TODO / plans 镜像推进，没有把无关内容混提。

## 下一步建议

- 若下一轮继续 `EMA`，更合理的是把现有 `candidate spec / operating spec / monitoring board` 真正接成 `paper-trading runbook`，然后才能按这版 promotion gate 开始真实 paper。
- 若下一轮继续 `breakout`，仍应回到默认主候选的最后一道 gate：`raw + avoid_fluctuating + ETH+SOL pair halfsize`，而不是再扩新的近义 gate 分支。

## Commit hash

本轮未提交。

## 未提交原因

当前 git 工作区存在大量与本轮无关的脏改动和未跟踪文件；为了避免误把其他线上的文件一起带入，本轮只完成文件落地与最小验证，不做 selective commit。
