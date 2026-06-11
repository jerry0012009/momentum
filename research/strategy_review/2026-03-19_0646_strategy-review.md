# 2026-03-19 06:46 UTC bot2 strategy review

## 本轮先检查了什么
- repo 状态：`git status --short` 显示 `jerry/momentum` 仍有大量既存脏文件；本轮只做 `docs/TODO.md` 顶部 desk-board 最小必要写回、strategy review 记录、首页 index 刷新与邮件，不混改无关文件。
- 最近 optimization logs（本轮重点核对）：
  - `2026-03-19_0528_rank80-first30m-impulse-intake.md`
  - `2026-03-19_0547_rank80-clean-replication-keep-p1.md`
  - `2026-03-19_0610_rank81-rs-asymmetry-intake.md`
  - `2026-03-19_0640_rank81-clean-replication-keep-p1.md`
- 最近 strategy review：
  - `2026-03-19_0504_strategy-review.md`
  - `2026-03-19_0604_strategy-review.md`
- 当前 cron：
  - `bot2-strategy-review-40m` enabled / 本轮正在运行
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
  - 本轮不需要改 cron
- `Paper Seat` guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue`；最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，当前仍是真 `waiting_not_due`，但已经进入临近窗口。
- `P3 narrow paper` 托管状态：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T06:18:05Z` 显示 `new_closed_trades_appended=1`。进一步看 `manual_narrow_paper_status.csv / manual_narrow_paper_closed_trades.csv`，对应的是 `Rank 32b` 新增 closed-trade append；当前专属 narrow-paper cron 已把状态与 ledger 写回，尚未看到需要 bot3 抢主资源补救的异常。

## 这轮 desk judgment 为什么要比 06:40 再收紧一步
`06:40 UTC` 顶板已经把 `Rank 81` 压回 `keep_P1 / evidence_pool`，意味着当前 fast lane 上 **没有值得继续默认续命的 active P1/P2 replication 候选**。与此同时，`06:18 UTC` 的 narrow-paper sidecar 虽出现了 `Rank 32b` closed-trade append，但它已经被专属 refresh cron 正常托管；这不是一个足以把 bot3 主资源从 fresh intake 抢回 P3 continuity 的异常。

因此当前更诚实的读法不是“继续围着 Rank 80 / 81 打磨”，也不是“因为 P3 有 closed trade 就回头做 continuity”，而是：
- `Paper Seat` 继续守 `EMA / waiting_not_due -> 07:00 UTC due window`；
- `Live Seat` 继续允许为空；
- `Scout Seat` 明确切回 **fresh paper/repo intake**，并按 `ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source` 排队。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA / PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 说明：A 股 `07:00 UTC` 的 due window 已很近，但此刻仍未进入 `due-now / overdue`；因此 `Paper Seat` 仍应保持 `EMA`，只是下一个 bot3 run 必须先做 due-check。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 80` 在 `05:47 UTC` 已给出 **`keep_P1 / evidence_pool`**；
  2. `Rank 81` 在 `06:40 UTC` 也已给出 **`keep_P1 / evidence_pool`**；
  3. 这两条线都已经用掉了各自那 1 次便宜诚实检查，却仍未升到 `P2`；按 desk 纪律，现在应切资源，而不是硬把它们包装成 live challenger；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 narrow paper` 托管层，也不是新的 live promotion 候选。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：**
  - `ETF lead regime gate`
- **当前紧邻后备：**
  - `Fib trend-strength admission layer`
  - `其他 fresh paper / repo based 5m / 15m crypto source`
- **当前只保留在证据池、但不再默认占主资源：**
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS+/RS- realized-semivariance asymmetry gate`
- **明确不应误写成新 seat 的托管位：**
  - `Rank 78 / 17 / 2 / 29 / 32b`（均属 `P3`）
  - 其中 `Rank 32b` 这轮虽有 closed-trade append，但当前仍只算 **托管层真实状态更新**，不是新的 Scout 主线。

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`ETF lead regime gate = P0`**（`source intake next / 当前默认主资源位`）
- **`Fib trend-strength admission layer = P0`**（`fresh intake pool / 邻近后备`）
- **`其他 fresh paper/repo source = P0`**（`source intake pool`）
- **`Rank 80 / first-30m impulse quality gate = P1`**（`cheap honest check 已用 / keep_P1 / evidence_pool`）
- **`Rank 81 / RS+/RS- asymmetry gate = P1`**（`minimal clean replication 已用 / keep_P1 / evidence_pool`）
- **`Rank 78 / adaptive no-trade band = P3`**（`narrow paper pilot approved / EMA-only suppression overlay`）
- **`Rank 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / 低频托管位`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 重点盯 `A股 07:00 UTC` 窗口；若此时仍 `waiting_not_due`，必须立即切到 `Run 2`，不得空转。
2. **`Run 2 = ETF lead regime gate source intake + 两条轻量诚实守门`**
   - 只做 `trade on / trade off` 与 `no-lookahead / no-repaint / no-leakage` 两条最小守门，不要同时打开其他 fresh 候选。
3. **`Run 3 = 若 ETF lead guard-passed，则只给它 1 次最小 clean replication；若 ETF 在守门阶段硬 fail，则改做 Fib trend-strength admission layer source intake`**
   - 继续保持 `1 个主点 + 1 个紧邻子点`；
   - `P3 continuity` 仍只作为 sidecar，不得默认重回主资源位。

## Active Scout 边际价值比较（本轮显式重排）
1. **`ETF lead regime gate`**
   - 当前排第一，不是因为证据最厚，而是因为 `Rank 80 / 81` 两条 `P1` 候选都已经用掉便宜检查却没有升级；按 desk 纪律，当前最诚实的动作就是切回新的 fresh source。
2. **`Fib trend-strength admission layer`**
   - 仍是 paper/repo based 的 `5m/15m crypto` 邻近 fresh intake；比继续磨 `Rank 80 / 81` 或挤占 `P3 continuity` 更符合当前 board 顺序。
3. **`其他 fresh paper/repo source`**
   - 保持在第 3 顺位，只有 ETF / Fib 这一层都拿不到合格对象，才继续往后扩。
4. **`Rank 80 / Rank 81`**
   - 当前都只应保留在 `P1 evidence_pool`；继续认领它们大概率只会增加近义说明，而不会减少真实 gate。
5. **`Rank 32b` 与其他 P3 托管位**
   - 这轮的确出现了 `Rank 32b` closed-trade append，但当前专属 cron 已把 ledger/status 续写完成；它现在更像低频健康检查触发器，不是新的 fast-lane 主线。

## 对 TODO 顶板的动作
- **本轮已做最小必要写回。**
- 在 `docs/TODO.md` 顶部新增了 `2026-03-19 06:46 UTC（bot2 desk review）` 补充，明确：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat` 已明确切回 fresh paper/repo intake，当前顺位为 `ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source`
  - `Rank 80 / Rank 81 = P1 evidence_pool`，不再默认续命
  - `Rank 32b` 的 `closed-trade append` 继续按 narrow-paper sidecar 托管，不改默认 seat
  - `Next 3 bot3 runs` 已改写为更具体的 `EMA due-check -> ETF intake -> ETF clean replication / Fib intake`
- 本轮不改 cron，不改其他 brief/prompt。

## 结论
- **Paper Seat：EMA，keep**
- **Live Seat：继续暂空**
- **Scout Seat：fresh paper/repo intake，当前由 `ETF lead regime gate` 领跑，`Fib trend-strength admission layer` 为紧邻后备**
- **P2：空；P4：空**
- **Rank 80 / 81：都留在 `P1 keep / evidence_pool`，不再默认抢主资源**
- **Rank 32b：出现真实 closed-trade append，但当前只算 `P3 continuity sidecar`，不改默认排兵布阵**
