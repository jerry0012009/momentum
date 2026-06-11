# 2026-03-16 03:38 UTC · Desk Board Review

## 本轮一句话判断

**席位仍不换，但当前 blocked 窗口已经往前推进了一格：`Scout Seat` 不再是“还没有 shortlist”，而是已经有了 `fast-cycle crypto shortlist v1`；`tiny-live plumbing` 也不再只是抽象 board，而是已经多出 `live-ledger template v1`。因此这轮最该改的是 desk board 顶部两处状态同步，而不是再重复上一轮的排班。**

## 当前 strongest evidence

1. **Paper Seat 仍是 EMA**
   - 当前仍在 `waiting_not_due`；
   - 没有新的 `due-now / overdue` lane；
   - 所以 `Paper Seat` 继续不变，最缺的仍是 **连续 market-close refresh / week-1 review 的 forward honesty**。

2. **Live Seat 仍是 breakout，但仍只能按 `keep but narrower-scope` 读**
   - 最新 cron / run history 里，breakout 这条线并没有出现新的 `pure-test / down-tail` blocker reduction；
   - 当前也仍落在 `rerun cooldown / no fresh overturn evidence`；
   - 所以没有理由把它升回宽口径主线，也没有足够证据现在就 bench / replace。

3. **Scout Seat 已经从“抽象方向”推进到“有 shortlist”**
   - 新增日志：`2026-03-16_0323_scout-seat-shortlist-card.md`
   - 当前已明确 `Rank 1 -> Rank 3`：
     1. `τ-band / no-trade breakout filter`
     2. `volume + support-flip + higher-low`
     3. `third-touch + EMA/MACD confluence`
   - 这说明 Scout Seat 现在已经有可直接认领的下一刀，不再只是口号。

4. **tiny-live plumbing 已经从 board 进到 schema**
   - 新增日志：`2026-03-16_0336_small-live-ledger-template.md`
   - 当前已落下 `small_live_ledger_template_v1.csv`；
   - 这意味着 Run 3 这条线现在已从“抽象 gate”推进到可审计字段层。

## 当前 weakest / should-park lines

- **Fibonacci**：继续 `park / archive`，没有任何理由回升。
- **breakout 的同样本 rerun 冲动**：当前仍应压住。现在更需要的是 cooldown-aware hard verdict，而不是再撞一轮同类重跑。

## 建议优先级 Top 1~3

1. **先把 desk board 顶部状态同步到最新现实**
   - `Scout Seat` 不能再写成“还没有 shortlist”；
   - `Next 3 bot3 runs` 也不能继续把已完成的 shortlist card / live-ledger template 当未来动作重复排。

2. **Live Seat 继续 `keep but narrower-scope`，但优先交 blocker sync / hard verdict**
   - 若 breakout 仍在 cooldown，就别 rerun；
   - 优先把 `one_more_gate` 的当前 deployment-facing 口径说死。

3. **Run 3 从“搭底板”转向“沿已落底板开始最小实验/最小检查”**
   - Scout 侧：从 `Rank 1 τ-band` 开始最小 `15m crypto` 对照实验；
   - tiny-live 侧：从 `routing dry-run checklist` 或 `paper-live shadow parity checklist` 开始，而不是继续写抽象规则页。

## TODO / web / cron 本轮改动

### 已改：`docs/TODO.md` 顶部两处

1. **Scout Seat 状态同步**
   - 从“还没有 shortlist candidate”改成：
   - **已有 `Run 3 fallback shortlist`，但还没有被本地最小实验推成 replace-ready candidate**。

2. **Next 3 bot3 runs 当前窗口排班**
   - 从：`shortlist card -> small_live plumbing 一小步`
   - 改成：
     1. breakout cooldown-aware hard verdict / blocker sync
     2. 从 `Scout shortlist Rank 1 τ-band` 开始最小 `15m crypto` 对照实验
     3. 补 `routing dry-run checklist` 或 `paper-live shadow parity checklist`

### 这轮不改

- 不改 `Paper Seat` 归属
- 不改 `Live Seat` 归属
- 不改 `Live Seat = keep but narrower-scope` 的 desk call
- 不改 cron 频率

原因：当前席位判断本身没变，变的是 **blocked 窗口里已经新落下的 Run 3 资产，需要同步到作战板**。

## 风险与不确定性

1. 这轮改的是作战板同步与排班前移，不是新增 alpha 证据本身。
2. bot3 当前列表仍显示 `error`，主因是 exact-text edit mismatch；若后续继续反复出现，下一轮应考虑再收紧 prompt，减少对同一脚本的大段精确 edit。
3. `Scout shortlist v1` 仍只是候选排序，不是 replace Live Seat 的本地证据；真正能不能升格，还要看 Rank 1/2 的 first verdict。

## 本轮一句话结论（给 Jerry）

**这轮我没换席位，但把 desk board 同步到了最新现实：Scout Seat 现在已经有 shortlist，tiny-live 也已经有 live-ledger template，所以接下来 bot3 不该再重复做“先列 shortlist / 先搭 ledger”，而要开始做 `τ-band` 最小实验和 `routing/parity` 最小检查。**
