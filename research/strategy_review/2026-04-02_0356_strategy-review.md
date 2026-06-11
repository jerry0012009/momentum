# Strategy Review — 2026-04-02 03:56 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并已复核当前 repo/runtime 与最近证据：
- `git status --short --branch`
- `research/optimization_loop/2026-04-02_0344_rank288_us_etf_midday_keep_p1.md`
- `research/optimization_loop/2026-04-02_0326_rank287_survivor_followup_background_p0_postcost_fee_shell.md`
- `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md`
- `research/strategy_review/2026-04-02_0316_strategy-review.md`

## 本轮只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- 否，当前为空。
- `current_target = none`。
- 已完成接线并处于 `connected_runner_live` 的仍是：`Rank 200 / 201 / 213 / 229`。
- 最近证据里没有任何仍停留在 `Active P2` 且已经明显达到 `P3 / paper launch` 门槛、却还没被升级的对象；因此本轮不存在 bot2 需要兜底直推 `P3` 的情形。

### 2) 本轮 `fresh intake` 是什么？
- 当前 runtime 里最近完成首判的 fresh intake 是：
  - `Rank 288 / research/quant_digests/2026-04-02_0158_us-etf-midday-momentum-pocket-alpha.md`
- 它的首判已完成并写回 state：
  - `US crypto ETF midday 30m momentum pocket` 已具备可独立审计的 intraday raw alpha skeleton；
  - 拥有清晰 universe（`IBIT / FBTC / ETHA / FETH`）、固定 pocket（`11:00–11:30 ET` signal，`11:30–12:00 ET` hold）、明确 entry/exit 与公开取数的最小 transfer path；
  - 但当前证据仍主要停留在 notebook/source audit 与作者给出的输出，尚未完成我们自己的 clean-room ETF 复现与 `BTC-vs-ETH perp` 映射下的 post-cost honesty，因此本轮只记为 `keep_P1`，不直升 `P2`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，而且它现在就是前排第一优先级。
- `Surviving candidate slot` 当前是 `Rank 288`，`followup_budget_remaining = 1`。
- 按 policy，它享有 survivor 锁定权；在这一次诚实收口完成前，不能让别的 `keep_P1` 覆盖它的前排槽位。
- 这唯一一次 follow-up 必须直接回答：
  1. 我们自己的 ETF clean-room 复现里，这条 midday pocket 是否仍保留净 alpha；
  2. 映射到 `BTCUSDT vs ETHUSDT perp` 后，在 `post-cost / delay / sizing` 下是否仍留下可执行净 pocket。
- 如果这一步过不了，就应直接 `follow-up exhausted -> background/P0`；不能继续把它拖成长尾 `keep_P1`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- `Rank 285` 已在 `2026-04-02 01:59 UTC` 完成 `P2 exit decision`，不再属于 active P2：
  - 结论不是 `P3`，也不是 fatal `P0`；
  - 而是一次性的 `P2 -> P1 re-scope`，收窄为只面向 `mature liquid tail / high-RV` 条件化子桶、并只保留 `1h~4h` 慢节奏持有的窄版 reversal pocket。
- 因此当前没有任何对象处于“离 `P3 / P1 / P0` 出口最近但尚未收口”的 active P2 状态。

## Rank 完整性检查
- `Paper launch queue`: `none`，无 rank 缺口。
- `Surviving candidate slot`: `Rank 288`，已有正式 rank。
- `Active P2 slot`: `none`。
- 当前前排对象不存在“已达 keep_P1/P2/P3 但无正式 rank”的问题，因此本轮无需补 rank。

## 本轮排班重写
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0 归档`。

当前真实前排链条为：
1. 没有 `P3` queue 头需要接线；
2. 没有 `Active P2`；
3. 有一个必须优先收口的 survivor：`Rank 288`；
4. 因此前两项里，第一项必须是 `Rank 288` 的唯一 follow-up，后续才能切回具体 fresh intake；
5. 本轮补入的 fresh intake 必须是具体对象，不能写空泛模板句子。

### 已写回 `BOT2_BOT3_STATE.md` 的新 `cycle_plan`
1. `Rank 288 / US crypto ETF midday 30m momentum pocket`
   - action: 执行 survivor 的唯一一次高杠杆 follow-up，直接回答 clean-room ETF 复现与 `BTC-vs-ETH perp` 映射后的 `post-cost / delay / sizing` 诚实性
   - success_criterion: 明确写成 `promote_P2` 或 `follow-up exhausted，退回 background/P0`
   - result: `none`
   - status: `pending`
2. `research/quant_digests/2026-04-02_0344_volnorm-rocshock-ema-volume-alpha.md`
   - action: 作为当前 survivor 已诚实排入后的第一条 fresh intake，判断 `volnorm roc-shock EMA volume` 是否真有可独立审计的 crypto signal skeleton，而不是常见 ROC+volume breakout 改名
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`
3. `research/quant_digests/2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`
   - action: 判断 `cross-asset integrated OFI lead/lag` 是否具备独立可复核的 feature、传导主语、交易时钟与执行边界
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`
4. `research/quant_digests/2026-04-02_0306_dynamic-coint-percentile-pairs-alpha.md`
   - action: 判断 `dynamic coint percentile pairs` 是否真是 distinct 的新主语，而不是旧 pairs family 改名后重回前排
   - success_criterion: 明确给出 `keep_P1 / P2 / P0`
   - result: `none`
   - status: `pending`

## 结论
- `Paper launch queue`：空
- 本轮 `fresh intake`：`Rank 288`
- 上一条 fresh intake 是否值得唯一 follow-up：值得，而且必须优先收口
- 当前明确 `Active P2`：无
- 因此本轮最诚实的排班是：先收口 `Rank 288`，再继续具体 fresh intake，而不是跳过 survivor 或虚构 P2/P3 主线。
