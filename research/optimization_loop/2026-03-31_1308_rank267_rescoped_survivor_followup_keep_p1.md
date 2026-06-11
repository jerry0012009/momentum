# Rank 267 / ex-majors high-liquidity alt basket factor momentum × size/vol rotation re-scoped survivor follow-up

- 时间：2026-03-31 13:08 UTC
- 轮次来源：bot3 13 分钟自动执行轮次
- 依据文件：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 执行动作：执行 `cycle_plan` 最前项 pending 小点，即 `Rank 267` 在一次性 `P2->P1 re-scope` 后的唯一 survivor follow-up
- 正式结论：`keep_P1`

## 本轮只回答的唯一问题
> 当对象被诚实收窄为 `ex-majors high-liquidity alt basket`、并只保留 `72h~7d` 排序、`12h~24h` 持有、`1d~5d` sleeve rotation` 这片慢频有效参数面后，它是否已经形成一个可独立审计的窄版 raw alpha 主语？

## 允许使用的现成证据
本轮不重开 broad-crypto/P2 admission，也不再把 `majors` 拉回主语；只用已有 runtime 证据回答窄版对象是否站得住：

1. `rank267_minimal_replication_summary.json`
   - 在当前高流动 perp 样本上，rotation 最优区明确落在 `72h~7d rank × 24h hold × 1d~5d rotation`，其中
     - `7d × 24h × 1d` 约 `+174.82 bps/period`
     - `72h × 24h × 1d` 约 `+164.21 bps/period`
     - `7d × 24h × 3d/5d` 约 `+147.04 / +145.44 bps/period`
   - `12h hold` 也仍保留连续正区间，快到 `4h hold` 后才明显被摩擦压薄。
2. `rank267_cross_asset_summary.json`
   - `majors` 单独拆开后 rotation 仅约 `+11.17 bps/period`，几乎落到手续费边缘；
   - `alts` 子集 rotation 约 `+117.44 bps/period`，且 leave-one-out 全部仍为正，说明窄版对象并不是单一币 pocket 幻觉。
3. `rank267_time_stability_summary.json`
   - 在统一的 `7d rank × 24h hold × 1d rotation` 骨架下，三段时间切分均为正：
     - early ≈ `+78.13 bps/period`
     - mid ≈ `+224.24 bps/period`
     - recent ≈ `+187.82 bps/period`
   - 这说明窄版主语不是只靠最近一小段行情幸存。

## 为什么本轮结论是 keep_P1，而不是直接回 background
窄版对象已经具备独立可审计的 raw alpha 骨架：
- **scope** 明确：只针对 `ex-majors high-liquidity alt basket`；
- **signal** 明确：`size / low-vol / momentum sleeves` + `winner sleeve rotation`；
- **tempo** 明确：只保留慢频 `72h~7d` 排序、`12h~24h` 持有、`1d~5d` rotation；
- **honesty** 明确：不再把 `majors` 或 broad-crypto 普适性写进主语。

如果这一步仍判回 background，等于把“broad-crypto 叙事不诚实”误写成“窄版 alt-basket alpha 不存在”。现有证据并不支持这么重的否决。

## 为什么本轮也不直接升下一层
虽然窄版对象已站成一个可独立审计的 P1 主语，但这一步按 policy 只是 re-scoped survivor 的唯一 follow-up；本轮不重开新的 admission 轴，也不把旧 P2 结果机械平移成“窄版对象已经完成新一轮 P2 准入”。

更诚实的落点是：
- **承认窄版对象已经成形，保留前排 P1 身份；**
- **把 broad-crypto 旧主语彻底关掉；**
- 等 bot2 后续若要继续推进，必须以这个收窄后的主语重新排一个具体、单一、会改变层级的下一步，而不是偷回 broad-crypto/P2 旧轨道。

## 正式 verdict
`Rank 267 / ex-majors high-liquidity alt basket factor momentum × size/vol rotation`：`re-scoped survivor follow-up passed，keep_P1`

一句话收口：

> `Rank 267` 在收窄到 `ex-majors high-liquidity alt basket` 后，已有连续正的慢频参数面、alts 子集显著强于 majors、且 leave-one-out 与分段时间结果都未显示单一币或单一区间幻觉，因此这条 re-scoped 对象已经形成可独立审计的窄版 raw alpha 主语；本轮诚实结论是保留前排 `P1`，而不是回 background，也不重开 broad-crypto/P2 旧叙事。

## 对 runtime 的写回语义
- `Surviving candidate slot` 继续保留 `Rank 267`，但其 re-scoped survivor follow-up 已用尽；
- `followup_budget_remaining` 应写为 `0`；
- `cycle_plan[1]` 应写为 `done`，result 写成一条会改变系统认知的句子；
- `Active P2 slot` 保持 `none`，不得因为这一步又把 broad-crypto 旧 P2 轨道偷偷复活。

## 一句话 result（用于 state / cycle_plan）
`Rank 267：re-scoped survivor follow-up passed；在只看 ex-majors 高流动 alt basket、并只保留 72h~7d 排序 + 12h~24h 持有 + 1d~5d rotation 的窄版主语下，alts 子集仍有连续正的可审计净边且非单一币幻觉，因此保留前排 P1，不回 background，也不重开 broad-crypto/P2。`
