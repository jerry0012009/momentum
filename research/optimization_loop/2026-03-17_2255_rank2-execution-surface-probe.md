# Rank 2 execution surface probe

## 为什么这次选这个
- 先按 `TRADING DESK BOARD` 顶板顺序重读：`Run 1 / EMA` 当前仍是 `running paper / waiting_not_due`，不该空转。
- `Run 2 / Scout Fast Lane` 当前 authoritative 读法仍是 `exhaustion state`，而且本轮没有新的合格 `paper / repo based 5m / 15m crypto` source 可认领。
- 因此按板上顺序回退到 `Run 3 / tiny-live plumbing`。
- `Run 3` 当前唯一真的会改状态的动作，仍是 `Rank 2` 那 1 次 whitelist-bound `test/no-fill replay`；但 22:40 顶板已提示 blocker 不是逻辑 ready gate，而是 `execution surface` 可能不在场。这轮要做的不是继续补 packet，而是把这个 blocker 做成可复核的硬检查。

## 做了什么改动
1. 重新核对执行面是否存在：
   - `openclaw` 浏览器 profile 当前只有研究/搜索页，没有交易 venue / operator tab；
   - `chrome` relay profile 当前 `tabs=[]`，说明没有已附着 tab；
   - repo 内 grep 只找到 `small_live_*` 的 packet / checklist / ledger / ready-gate 产物，没有找到本地可直接发起 whitelist-bound replay 的执行脚本/API 入口。
2. 新增 reader-facing artifact：
   - `reports/artifacts/alpha_closure_board/small_live_rank2_execution_surface_probe_v1.csv`
   - `reports/site/factors/alpha_closure_board/rank2_execution_surface_probe.html`
3. 同步把 `small_live_rank2_closeout_snapshot_v1.csv` 的 authoritative blocker 改写成更诚实版本：
   - 不再只写泛化的 `route_receipt_chain_missing`；
   - 明确写成 `execution_surface_absent; chrome_relay_tab_missing; local_replay_entrypoint_not_found; route_receipt_chain_missing`；
   - 把 `next_allowed_action` 收紧成：先 attach/login 一个 execution surface，再做唯一允许的那 1 次 replay。

## 验证 / 证据
### 执行面 probe 结果
- `openclaw browser`：存在 headless browser，但当前 tab 只看到 research/search 页（GitHub 搜索、论文页、about:blank），没有 exchange/operator 执行面。
- `chrome relay`：profile 未运行，`tabs=[]`，所以当前没有 Browser Relay 附着 tab 可用于回填 `intent + ack + cancel(close)` refs。
- `local repo entrypoint`：grep 仅找到 `small_live_*` 的 packet/checklist/ledger/ready-gate 类 artifact，没有找到可直接发起 whitelist-bound `test/no-fill replay` 的本地执行入口。

### 本轮硬结论
- `Rank 2` 当前并不是逻辑上还没 `ready_for_one_test_no_fill_replay`；
- 更诚实的 blocker 是：**执行面不存在**，所以当前仍必须停在 `paper_candidate_only / blocked`；
- 在某个已登录、已附着的 venue execution surface 出现之前，继续补 ready-gate / packet / writeback 都不算真实进展。

## 风险 / 边界
- 这轮没有真的触发 replay，也没有变更任何 `Rank 2` 策略 scope / capital / venue whitelist。
- 这轮只是把 blocker 从“泛阻塞”收紧成“execution surface absent”的可复核状态。
- 由于 repo 当前存在大量与本轮无关的脏文件，本轮不做 commit，避免混提。

## 下一步建议
- 只有当 operator 提供一个**已登录 + 已附着**的 venue execution surface（本地执行入口或 Browser Relay attached tab）后，才继续那 1 次 `SOLUSDT` 优先的 whitelist-bound `test/no-fill replay`。
- 若下一轮仍没有 execution surface，则应继续维持 `paper_candidate_only / blocked`，不要再把相邻 closeout 文案当成进展。

## 相关产物
- `reports/artifacts/alpha_closure_board/small_live_rank2_execution_surface_probe_v1.csv`
- `reports/site/factors/alpha_closure_board/rank2_execution_surface_probe.html`
- `reports/artifacts/alpha_closure_board/small_live_rank2_closeout_snapshot_v1.csv`

## Commit hash
- 未提交。本轮只做了与 Run 3 blocker 相关的最小 artifact/snapshot 更新，但工作区已有大量无关脏文件，安全 selective commit 成本过高。