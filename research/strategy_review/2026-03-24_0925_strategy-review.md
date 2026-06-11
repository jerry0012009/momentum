# Strategy Review (bot2)

Time: 2026-03-24 09:25 UTC

## 本轮一句话判断
本轮 `TRADING DESK BOARD` 必须从“fresh intake 先行”切到 **`ryanczm/Crypto-Stat-Arb` 的唯一 survivor follow-up 先行**：它已在 `2026-03-24 09:22 UTC` 完成 fresh intake 并进入 `keep_P1`，当前没有 `P2/P3`，所以 bot3 的下一轮主资源应先用来回答它是 `park` 还是 `promote_P2`。

## 1) 必检结果

### Repo 状态
- workspace 仍然很脏，但本轮 desk review 只做最小必要改动：
  - 刷新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 新增本轮 `strategy_review` 日志
- 最新改变 desk 认知的对象是：
  1. `research/optimization_loop/2026-03-24_0922_crypto-stat-arb-fresh-intake.md`
  2. 较近的前一条已闭环对象：`term-structure calendar-spread reversion raw alpha`（`keep_P1 -> park`）

### 最近 `research/optimization_loop/`
- `2026-03-24_0922_crypto-stat-arb-fresh-intake.md`
- `2026-03-24_0853_chanpy-framework-intake-park.md`
- `2026-03-24_0844_nfi-fresh-intake-park.md`
- `2026-03-24_0817_term-structure-calendar-spread-park.md`
- `2026-03-24_0745_term-structure-calendar-spread-keep-p1.md`
- `2026-03-24_0719_rank153-verdict-state-refresh.md`
- `2026-03-24_0713_rank153-first-verdict-minimal.md`
- `2026-03-24_0638_rank153-liquidation-consensus-cascade-intake.md`

结论：最新增量不是旧对象重开，而是新的 fresh intake `ryanczm/Crypto-Stat-Arb`。它已通过 intake 进入 `keep_P1`，因此按 policy 获得且只获得 **1 次** decisive follow-up 资格。

### 最近 `research/strategy_review/`
- `2026-03-24_0823_strategy-review.md`
- `2026-03-24_0740_strategy-review.md`
- `2026-03-24_0640_strategy-review.md`
- `2026-03-24_0600_strategy-review.md`

结论：`08:23` 那轮“fresh intake reopen”在当时是对的；但 `09:22` 新 intake 已产生并进入 `keep_P1`，所以本轮前排必须随之重排，不再是空开的 fresh slot。

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：running / 正常
- `bot3-momentum-auto-opt-13m`：running / enabled / 最近一次正常完成
- `momentum-narrow-paper-lanes-20m`：running / enabled
- `Rank32b live maintenance`：enabled / 正常
- `bot7-quant-digest-30m`：最近一次 timeout（与 desk 主路径无直接冲突，但说明旁路研究任务有单次超时）

结论：当前 cron 结构没有新的 paper launch 阻塞，也没有要求把资源拨回旧 background 对象；唯一该抢先执行的是 survivor 的一次性 follow-up。

## 2) authoritative board answers

### Paper / 待开启自动运行
- **none**

原因：
- 本轮没有任何 Scout 升到 `P3`
- 因此不新增 `runner / scheduler+status / verify+handoff` 的落地计划

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 151 / EWMAC breakout band-pass gate`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b / narrow paper lanes`
- `Rank 122 / paper sidecar`

判断：这些 lane 继续独立运行，但不改变当前 Scout 主排序。

### Scout 排序
1. `surviving candidate slot（当前前排）`
   - target: `ryanczm/Crypto-Stat-Arb`
   - budget: 仅剩 1 次最小 decisive follow-up
   - 目标：回答 `park / promote_P2`
2. `fresh intake slot（下一前排）`
   - status: open
   - 条件：若 `ryanczm/Crypto-Stat-Arb` 未升 `P2`，立即切回新 intake
3. `active P2 slot`
   - `none`
4. `Background pool（不自动回前排）`
   - `term-structure calendar-spread reversion raw alpha / Rank 153 / 152 / 145 / 111 / 140 / 14b / 147 / 146 / 150 / 125 / 112 / 139 / 149 / 144 / 143 / 142 / 141 / 更早 parked ranks`

### P0 ~ P4
- `P4`：当前不使用
- `P3`：none
- `P2`：none
- `P1`：`ryanczm/Crypto-Stat-Arb`（已完成 fresh intake，等待唯一一次 decisive follow-up）
- `P0`：背景池与 parked ranks（最新 parked：term-structure calendar-spread reversion raw alpha）

### Next 3 bot3 runs
1. **`ryanczm/Crypto-Stat-Arb` 唯一一次 decisive follow-up**
   - 只做 `carry / momentum / breakout / combined` 的最小分腿归因与成本敏感性检查
   - 明确回答：它只是“拼装看起来完整”，还是某一腿真在成本后提供可保留 edge
   - 目标：直接给出 `park / promote_P2`
2. **条件分流**
   - 若 Run 1 = `promote_P2`：立刻做 1 次最小 P2 admission follow-up，优先补最缺的一项（`cross-asset / time stability / parameter stability / honesty`）并回答 `keep_P2 / promote_P3 / drop_to_background`
   - 若 Run 1 = `park`：立即认领下一条 fresh raw alpha / repo，产出 intake card，并回答 `park / keep_P1`
3. **再下一步**
   - 若 Run 2 产生新的 `keep_P1`：给这条新 survivor 安排唯一一次最小 decisive follow-up，目标回答 `park / promote_P2`
   - 若 Run 2 已进入 `P2`：继续做最小 admission close-out，目标回答 `promote_P3 / drop_to_background`
   - 若 Run 2 直接 `park`：继续重开 fresh intake，不回旧 background 对象

## 3) 本轮是否有 Scout 升到 P3
- **没有**

所以：
- `Paper / 待开启自动运行 = none`
- 不触发 `runner / scheduler+status / verify+handoff` 三轮落地计划

## 4) Desk 判断
- `ryanczm/Crypto-Stat-Arb` 已完成 fresh intake，并成为当前唯一合法 `P1` survivor；如果此时直接跳过它再开新 intake，会违背 policy 对 survivor 的一次性 follow-up 约束。
- `term-structure calendar-spread reversion raw alpha`、`Rank 153`、`Rank 152` 等都没有被 reopen 的依据，继续留在 background pool。
- 当前合法主线已从上一轮的 `fresh intake open` 切换为：
  `survivor follow-up -> （若失败）fresh intake reopen / （若成功）P2 admission`

## 5) 当前 cron /执行面备注
- `bot2` 与 `bot3` 当前都处于 running 状态，说明 40m review 与 13m auto-opt 链路在继续工作。
- `bot7-quant-digest-30m` 存在最近 1 次 timeout，但这只影响旁路研究产能，不影响本轮 desk 排班判断。

## 6) 本轮实际改动
- 刷新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 新增本轮日志：
  - `research/strategy_review/2026-03-24_0925_strategy-review.md`

## 7) 一句话结论
**本轮桌面主线已切到 `ryanczm/Crypto-Stat-Arb` 的唯一一次 decisive follow-up：先回答它能否升 `P2`，若不能就立刻丢回背景池并重开 fresh intake。**
