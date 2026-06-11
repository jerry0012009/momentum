# Strategy Review (bot2)

Time: 2026-03-22 23:14 UTC

## 本轮一句话判断
Desk 主线仍不换：**Paper Seat 继续是 EMA / 创业板ETF 1d，Live Seat 继续暂空**；但 Scout 不该再被写成“默认继续磨 Rank140”。最新两轮 bot3 已先给出 `Rank137` 的 decisive positive honesty evidence，又在 23:01 合规切到 fresh intake 并把 `Rank141` 直接压回 `P0`。因此当前更诚实的 desk 口径是：**Scout Seat 进入“Rank140 family-board pending + fresh intake reserve”模式，而不是把某个单一 P1 候选长期写死为 primary。**

## 1) 必检：Repo 状态
- 分支：`master`
- 工作区：**dirty（大量 modified + untracked 产物/脚本/页面）**
- 结论：当前 repo 噪声仍高；本轮不清理，但继续视作误混产物/误 commit 风险。

## 2) 必检：最近 optimization_loop / strategy_review
### 最近 `research/optimization_loop/`
- `2026-03-22_2301_rank141-bounce-polarity-source-intake.md`
- `2026-03-22_2248_rank140-rank137-confirm-window12.md`
- `2026-03-22_2236_rank140-rank137-confirm12-entry24.md`
- `2026-03-22_2214_rank140-rank128-max-high-only.md`
- `2026-03-22_2206_rank140-rank127-shared-three-arm.md`

### 最近 `research/strategy_review/`
- `2026-03-22_2206_strategy-review.md`
- `2026-03-22_2037_strategy-review.md`
- `2026-03-22_1950_strategy-review.md`
- `2026-03-22_1910_strategy-review.md`
- `2026-03-22_1831_strategy-review.md`

## 3) 必检：当前 cron 列表（desk 相关）
- `bot2-strategy-review-40m`：enabled，当前这轮运行中。
- `bot3-momentum-auto-opt-13m`：enabled，最近 `ok`，排班仍与 desk 主线一致。
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`。
- `bot7-quant-digest-30m`：enabled，但最近一轮 `error`（`python: command not found`）；这是辅助研究链路问题，不改变当前交易 desk 主排班。
- `bot6-park-reframe-2h`：enabled，最近 `ok`。

结论：当前 cron 主干仍正常；无需改频率。唯一值得记一笔的是 bot7 又踩了 `python`/环境假设问题，但不影响 bot2/bot3 主线。

## 4) Desk 核心回答（authoritative）
### 4.1 Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **当前状态**：`running paper pilot / waiting_not_due`
- **hosted lanes / family lanes**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- **当前最缺的 gate**：不是继续讲 alpha，而是 `refresh continuity / week-1 review continuity / active-shadow demotion discipline`。

### 4.2 Live Seat 是否空
- **Live Seat：空（暂空）**
- 理由：目前没有任何 Scout 候选已经诚实通过到 `paper candidate / tiny-live review` 的门槛，没必要为了“桌上有 live challenger”而硬塞。

### 4.3 Scout 复刻对象
- **当前 Scout 主口径**：`dynamic active Scout / fresh intake reserve`，本轮不把单一 P1 候选写死为长期 primary。
- **刚刚完成的复刻对象**：
  1. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
     - 最新 family-board 新增 decisive evidence：
       - `Rank137 / confirm12_entry24` → `PBO=0.0000 / guard_passed`
       - `Rank137 / confirm_window_12` → `PBO=0.0000 / guard_passed`
     - 同时 `Rank127`、`Rank128` 继续给出 `guard_failed` 或 `veto 优于 kept` 的反证。
  2. `Rank 141 / bounce polarity not-shared gate`
     - 最新 fresh intake 已直接给出 `not_shared / park`，不进入 clean replication 主队列。

### 4.4 候选 P0~P4 分档（本轮）
- **P1 / keep_P1（仍 relevant，但不再默认长期占 primary）**
  - `Rank 140 / pbo-cscv deflated sharpe honesty gate`
    - `recommended_action = keep_P1`
    - `why_now = family-board 终于拿到 Rank137 两条 guard_passed 正例，说明它还没到该 park 的阶段`
    - `main_weakness = 通过的是 honesty-layer family，不等于已产出可直接升到 paper 的独立策略；且多数其它 family 仍 guard_failed`
- **P1 / evidence-input only（不抢主资源位）**
  - `Rank 125 / range location veto gate`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
  - 这些都更像 Rank140 的 family 输入，而不是当前 desk 要单独追升格的主点。
- **P0 / park / evidence pool**
  - `Rank 141 / bounce polarity not-shared gate`：fresh intake 已给出 direct park
  - `Rank 137`：作为独立 scout 候选仍维持 `park / evidence only`；本轮 positive evidence 只支持它在 **Rank140 family-board** 里当 honesty 正例，不足以直接把原始 Rank137 独立升格回 active scout
  - `Rank 138 / Rank 127` 及其余已 park ranks：维持 park
- **P3 / hosted narrow paper continuity**
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - `Rank 139`（独立 runner）
  - `Rank 122`（sidecar monitoring）
- **P2 / P4**
  - 本轮仍无新增可升格对象

## 5) strongest evidence / weakest lines
### strongest evidence
1. **EMA 仍是唯一真实 Paper primary anchor**：Run1 继续合规返回 `waiting_not_due`，说明现在是 market clock 在等，不是执行飘移。
2. **Rank140 family-board 出现了真正的 decisive evidence**：
   - `Rank137 / confirm12_entry24`：`478:340`，`PBO=0.0000`，`guard_passed`
   - `Rank137 / confirm_window_12`：`545:273`，`PBO=0.0000`，`guard_passed`
   这意味着 Rank140 不再只是“全是 guard_failed 的失败板”，而是终于拿到两条可读且过关的 honesty 正例。
3. **Rank141 已被快速、低成本地诚实淘汰**：
   - `same_body=True` 相比 `False` 在 long/short 两侧都没有 shared uplift，long 侧更明显变差；
   - 因此它更像 repo 审美/追单偏好，不值得继续浪费 clean replication 预算。

### weakest / should-park lines
1. **最该收口的是继续把 Rank141 当 active scout**：已经直接 `park`，不要再回头磨。
2. **不该误读的是把 Rank137 立刻当独立新主点**：当前 positive evidence 的语义是“它在 Rank140 honesty-layer 里是强正例”，而不是“原始 Rank137 独立策略已经恢复成 desk 主候选”。
3. **Hosted P3 continuity 仍不该回潮成主资源**：没有 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 时，只维持事件驱动。

## 6) Next 3 bot3 runs（本轮排班）
1. **Run 1 = EMA due-check first**
   - 若真实 `due-now / overdue`，先做 paper refresh；
   - 若仍 `waiting_not_due`，立刻切 Run 2。
2. **Run 2 = Hosted P3 continuity（低频、事件驱动）**
   - 只在 `closed-trade append / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 时认领；
   - 若无事件，跳过，不做近义健康检查。
3. **Run 3 = Scout 动态择一，但不要把单一 P1 写死**
   - 优先级：
     - **先**看 `Rank140` 是否还需要 **1 条最小 family 定锚/总结**（例如把 Rank137 两条 pass 压成更清楚的“核心贡献来自 confirm window 还是 entry latency”结论）；
     - **否则**直接切新的 active Scout / fresh intake reserve；
   - **不要**继续 Rank141；
   - **不要**把 Rank140 又写成“默认长期 primary”。

## 7) TODO / Board 是否要改
- **本轮做最小必要更新：建议更新 `docs/TODO.md` 顶部两处。**
  1. 在 `Active Scout 排序` 中补入 `Rank 141 / P0 / park / not_shared`；
  2. 在 `Next 3 bot3 runs` 中把 Run 3 的描述再收紧一层：明确“可先做 1 次 Rank140 family-board 定锚，否则切 fresh intake；不得把单一 P1 长期锁成主点”。

## 8) 网页 / cron / 自动化建议
### 网页 / 表达
- 本轮只需常规 publish 首页 index；不需要额外重写 reader-facing closure 页。
- 等 Rank140 对 Rank137 的 family 结论再压成一句话后，再考虑把“honesty-layer 已出现 guard-passed 正例”外显到 reader-facing 页面。

### cron / 节奏
- bot2 / bot3 / narrow-paper 频率不改。
- `bot7` 的环境假设（`python` vs `python3`）值得后续单独修，但不抢当前 desk 主线。

## 9) Top 1~3
1. **把 Rank140 对 Rank137 的 family-board 结论压成一句更硬的 desk 读法**：核心贡献到底来自 `confirm_window_12` 还是 `entry latency`，做 1 次最小定锚就够。
2. **若 EMA 仍 waiting_not_due，Scout 下一轮优先 fresh intake / next active scout**，不要又回到 Rank141，也不要把 Rank140 默认写死。
3. **继续保持 Hosted P3 事件驱动纪律**，避免 continuity 回潮侵占主资源。

## 10) 风险与不确定性
- 当前最容易犯的错，是把 Rank140 的最新 positive family evidence 误读成“整个候选已接近 paper candidate”。现在只能说：**honesty-layer 终于有了正例**，还不是独立策略升格。
- repo 工作区仍然很脏；任何真实代码/文档改动都需要继续只做局部、最小编辑。

## 11) 本轮我改了什么
- 生成本轮 `strategy_review` 记录
- 下一步将对 `docs/TODO.md` 顶部做最小必要更新（Rank141 + Run3 收紧）
- 将执行常规首页刷新 + 邮件发送
