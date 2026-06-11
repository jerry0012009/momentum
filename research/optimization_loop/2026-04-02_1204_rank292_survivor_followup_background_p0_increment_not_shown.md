# Rank 292 survivor follow-up -> background/P0

- Time: `2026-04-02 12:04 UTC`
- Target: `Rank 292 / cross-asset integrated OFI × follower short-horizon continuation`
- Action: `survivor one-time existence follow-up`
- Verdict: `keep_P1后回background / P0`

## Why this was the next legal move
- Per current `BOT2_BOT3_STATE.md`, the first pending `cycle_plan` item is Rank 292's唯一一次 survivor follow-up.
- There is still no `Paper launch queue` target and no `Active P2`, so bot3 should only close this one front-slot item.
- Policy requires this follow-up to answer a decisive question, not to restate the story. Here the decisive blocker was explicit: under a minimal public-data / rough-cost lens, does `leader integrated OFI` add information beyond `leader return only`?

## What I checked
1. Re-read the intake digest `2026-04-02_0232_crossasset-integrated-ofi-leadlag-alpha.md`.
2. Re-read the first-verdict log `2026-04-02_1102_rank292_crossasset_integrated_ofi_keep_p1.md`.
3. Searched the repo for the specific blocker terms (`integrated OFI`, `lead-lag`, `leader return only`) and compared against older lead-lag family work already present in the workspace.
4. Spot-checked prior cross-market lead-lag code paths (`Rank 134`, `Rank 28`) to avoid misclassifying an old `leader move -> follower move` story as new evidence.

## What changed system cognition
`Rank 292` 目前仍然只是一个**定义清楚的 cross-asset microstructure 研究命题**，而不是已经完成存在性验证的 crypto raw alpha：现有材料能支持“值得被认真表述”，但还**不能证明**在最小 public-data / 粗成本口径下，`leader integrated OFI` 相对 `leader return only` 已经展示出足够独立、足够值得升到 `P2` 的新增信息量。

## Why this does NOT promote to P2
1. **关键 blocker 还停留在 paper/repo claim，而不是 desk-local existence check。**
   - intake digest 把问题定义得很清楚：`leader return only` vs `best-level OFI` vs `integrated OFI` vs `integrated OFI + microprice`。
   - 但当前 workspace 里并没有看到针对 `BTC/ETH/SOL/BNB` 的最小 ablation 结果，无法回答 integrated OFI 是否真的比 leader return only 多带来可交易增量。

2. **旧 lead-lag 家族已经存在，因此 distinctness 现在取决于“OFI 增量”而不是“有 lead-lag 故事”。**
   - workspace 里早就有 `Rank 134` / `Rank 28` 这类 lead-lag / follower 传导框架。
   - 所以 Rank 292 真正新、真正值钱的部分不是“leader 先动 follower 后动”，而是“leader 的 integrated OFI 比单纯 leader return 更早、更稳、更可交易”。
   - 这一步当前还没有被本地最小实验坐实。

3. **survivor 的唯一一次便宜 follow-up 已经用在最关键 blocker 上，但 blocker 仍未被消掉。**
   - 这次 follow-up 后，系统已经能更诚实地说清：问题不在“故事讲不讲得通”，而在“OFI 增量有没有被证明”。
   - 既然 decisive blocker 仍未过，就不该继续占前排资源。

## Why this is not a hard reject of the idea
- 这条线不是被证明为假；它仍然是一个定义清楚、可 clean-room 的研究对象。
- 但根据 policy，`Surviving candidate` 只有一次 cheap decisive follow-up。一次之后若没有升 `P2`，默认就应移回 `Background pool`。
- 因此更诚实的收口不是继续拖成第二次 survivor，也不是用空泛措辞保留前排，而是：**记录 blocker 已定位，然后回 background。**

## Honest takeaway
`Rank 292` 的真实地位是：
- **比泛 order-book imbalance 叙事更具体**，因为它有 leader/follower、integrated OFI、短时窗与最小实验壳；
- **但还没有具体到足以升 P2**，因为最关键的 incremental question —— `integrated OFI` 相对 `leader return only` 的独立信息量 —— 在当前 runtime 里仍未被最小 crypto existence check 证明。

所以这次 survivor follow-up 的诚实结论是：
**保留研究记录，但退出前排，回 `background/P0`。**

## Result line for runtime
`Rank 292`：survivor 唯一一次 follow-up 已把 decisive blocker 收口到“`leader integrated OFI` 在最小 public-data / 粗成本口径下尚未证明比 `leader return only` 有足够独立增量信息”，因此本轮不升 `P2`，结束前排占位并回 `background/P0`。
