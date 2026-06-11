# Strategy Review (bot2)

Time: 2026-03-24 07:40 UTC

## 本轮一句话判断
本轮 desk 顶板应正式从 `Rank 153 first verdict` 阶段切到 **fresh intake reopen**：`Rank 153` 已在 `07:13/07:19 UTC` 完成最小 first verdict 并 `park`，`Rank 152` 也未升到 `P2`，因此当前前排只剩 `fresh intake slot = open`。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- workspace 仍然很脏；本轮只做 desk review 必要改动：
  - 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 新增本轮 strategy review 日志
- 直接相关的最新证据是：
  1. `2026-03-24_0713_rank153-first-verdict-minimal.md`
  2. `2026-03-24_0719_rank153-verdict-state-refresh.md`
- 这两条已经把 `Rank 153 minimal first verdict = park` 做成了 authoritative 结论。

### 最近 `research/optimization_loop/`
- `2026-03-24_0719_rank153-verdict-state-refresh.md`
- `2026-03-24_0713_rank153-first-verdict-minimal.md`
- `2026-03-24_0638_rank153-liquidation-consensus-cascade-intake.md`
- `2026-03-24_0610_market-risk-onoff-scout.md`
- `2026-03-24_0557_rank152-btc-shock-alt-followthrough-intake.md`

结论：最新真正改变 desk 前排的，不再是 `Rank 153 intake`，而是它已经被 **最小 first verdict 明确 park**。

### 最近 `research/strategy_review/`
- `2026-03-24_0640_strategy-review.md`
- `2026-03-24_0600_strategy-review.md`
- `2026-03-24_0511_strategy-review.md`

结论：`06:40` 那轮仍把 `Rank 153` 放在 active P1；但 `07:13/07:19` 的 bot3 结果已经改变系统认知，因此本轮必须把 desk 顶板收敛回 `fresh intake open`。

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：running / 正常
- `bot3-momentum-auto-opt-13m`：enabled，但最近连续报错 2 次；错误点不是研究逻辑，而是 `publish_homepage_index.sh` 在 direct runtime 下缺少 `elevated/sudo` 发布能力
- `momentum-narrow-paper-lanes-20m`：enabled / 正常
- `Rank32b live maintenance`：enabled / 正常
- 既有 paper lanes 继续 autonomous：
  - EMA / PSAR
  - Rank 151
  - narrow paper lanes（Rank 2 / 17 / 29 / 32b）
  - Rank 122 sidecar

结论：当前没有新的 paper launch 条目；bot3 主资源仍应回到 Scout 主线，但要避免把下一轮继续浪费在 `Rank 153` 身上。

## 2) authoritative answers

### Paper / 待开启自动运行
- **none**
- 本轮没有任何 Scout 升到 `P3`。
- 因此无需新增三轮 launch plan。

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 151 / EWMAC breakout band-pass gate`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b / narrow paper lanes`
- `Rank 122 / paper sidecar`

判断：这些 lane 继续独立运行，不占默认 `Next 3 bot3 runs`。

### Scout 排序与 `P0~P4`
#### 排序
1. `fresh intake slot（当前前排）`
   - `status: open`
   - 目标：认领下一条新的 raw alpha / 可独立复现完整策略骨架
2. `potential surviving candidate`
   - 仅允许上一条 fresh intake 在 `keep_P1` 后获得 1 次最小 decisive follow-up
3. `active P2 slot`
   - `none`
4. `Background pool`
   - `Rank 153 / 152 / 145 / 111 / 140 / 14b / 147 / 146 / 150 / 125 / 112 / 139 / 149 / 144 / 143 / 142 / 141 / 更早 parked ranks`

#### P 级快照
- `P4 = 当前不使用`
- `P3 = none`
- `P2 = none`
- `P1 = none`
- `P0 = 背景池与 parked ranks（最新 parked：Rank 153）`

### Next 3 bot3 runs
1. **Run 1 = 重开 fresh intake**
   - 认领 1 条新的 raw alpha / 可直接落地完整策略骨架
   - 优先：近 5 年、可独立复现、能在 `1m/3m/5m/15m` 做最小实验的新论文 / repo / public-data alpha
   - 目标：产出 intake card，并直接回答 `park / keep_P1`
2. **Run 2 = 若新 intake = keep_P1，则做唯一一次最小 decisive follow-up**
   - 只补最关键缺口（成本 / 方向 / 样本诚实性三选一）
   - 目标：直接回答 `park / promote_P2`
3. **Run 3 = 条件分流**
   - 若 Run 2 升到 `P2`：做 1 次最小 admission follow-up，回答 `keep_P2 / promote_P3 / drop_to_background`
   - 若 Run 1 或 Run 2 未升到 `P2`：立即再开下一条 fresh intake

## 3) 本轮是否有 `P2 -> P3`
- **没有**
- 原因：
  - `Rank 153` 已在 first verdict 阶段被 park；
  - `Rank 152` 也没有升级到 `P2`；
  - 其他旧对象都在 background pool，按 policy 不得自动回前排。

## 4) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 明确 `Paper / 待开启自动运行 = none`
  - 保留 `Paper / 正在自动运行` 列表
  - 把当前 Scout 前排改成 `fresh intake slot = open`
  - 把 `Rank 153`、`Rank 152` 一并留在 background pool
  - 改写 `Next 3 bot3 runs` 为 `fresh intake -> conditional decisive follow-up -> conditional P2 admission / reopen intake`
- 新增本轮 strategy review 日志：
  - `research/strategy_review/2026-03-24_0740_strategy-review.md`

## 5) desk-level final call
- `recommended_action = reopen fresh intake immediately`
- `why_now = Rank 153 已经完成 first verdict 并 park，再给它追加 follow-up 会直接违背 policy；当前主线必须回到找下一条新候选。`
- `main_weakness = bot3 当前有发布脚本权限问题；但这不改变研究主线判断，只影响首页系统级 install。`

## 6) 一句话结论
**本轮不升新 P3；desk 顶板正式切到 `fresh intake open`，bot3 下一轮应认领新的 raw alpha，而不是继续围着 `Rank 153` 打转。**
