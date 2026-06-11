# 2026-04-06 13:13 UTC · Rank 83 park reframe

## 本轮范围与选择
- 本轮只复盘 1 条 parked rank。
- 按 `PARK_REFRAME_QUEUE` 当前轮转规则，`50~79` 近几天已被高频覆盖，因此本轮切到 `80~110` 段；`Rank 83` 最近 7 天未被 `bot6` 复盘，且原始结论明确是 `park / evidence_pool`，因此本轮认领它。
- 保留原 `park` verdict 的审计意义；不改 `docs/TODO.md` 顶部排班。

## 原 rank 为什么 park
`Rank 83 / Fib trend-strength admission layer` 的原始思路，是把 `Fib retest_hold` 从二元 `hold/fail` 改写成 `weak / medium / strong` 三档 admission / sizing：
- `weak`：守住 `0.618` 但没收回 `0.5`
- `medium`：收回 `0.5`
- `strong`：在 `medium` 基础上再收回 `0.382` 或突破 `retest bar high`

原 rank 没被直接否定在“Fib 没信息”，而是被审计倒在 **成本稳定性与角色写法**：
- clean replication 里，`base_binary` 明显为负（`mean_total_return ≈ -1.83%`，`positive_asset_ratio = 0/3`）
- `strength_filter / strength_sizing` 在 `6bps` 看起来有改善（约 `+1.16% ~ +1.18%`），但核心靠的是 `strong` 桶；`medium` 桶本身仍是坏的（`mean_net_ret ≈ -0.106%`，`fail_4bars = 100%`）
- 到成本稳定性检查时，这条线从 `6bps` 的 `+1.16%` 掉到 `10bps` 的 `+0.27%`，再到 `15bps` 的 `-0.83%`，而且 `15bps` 下 `positive_asset_ratio = 0/3`

所以原 park 的核心原因很集中：**不是 Fib retest 主题完全没信息，而是“多档强弱 admission / sizing layer” 这层写法没有证明自己能在更诚实的 friction 下稳定存活；它更像低成本下的分层读数，不像可直接占用 scout 预算的 queue-facing 候选。**

## 它更像 hard park 还是 soft park
我把 `Rank 83` 归为：
- **`soft park`，但已经明显偏硬**。

原因：
- 它不是完全没 residual value；至少 `strong` 桶持续优于 `medium`，说明“回踩后的强确认”确实比“只是守住”更像 continuation。
- 但原 rank 作为 **三档 strength admission / sizing layer** 已经被成本稳定性审计得很清楚：这套写法太容易在更真实 friction 下塌掉。

换句话说：
- 对 **原版 `weak/medium/strong` 三档 sizing 读法**：已经接近 hard park
- 对 **Fib 回踩后仍可能存在更强确认分支** 这个更窄主题：还保留 soft residual

## 有没有“可救信号”
有，但只剩一条很窄的可救信号：

1. **真实 residual 只集中在 `strong` 桶**
   - clean replication 已经说明，`medium` 并没有形成可交易 pocket；真正留下正贡献的是 `strong` 那层更强 reclaim / follow-through。
2. **这个 residual 更像 binary confirm，不像多档 sizing**
   - 2026-03-19 的原始 digest 确实支持“方向 + 强度”视角；
   - 但随后成本检查把问题暴露得更清楚：desk 上真正可能留下来的不是多档分配，而是“是否达到足够强的确认”。
3. **旁证支持 Fib 更像 second-chance / confirmation branch，而不是一整套 shared hard gate**
   - `2026-03-23_0825_prev-candle-fib-second-chance-not-shared-gate.md` 的结论，是 Fib 更像 second-chance branch，而不是默认共享 hard gate；
   - 这反过来支持：Rank 83 若还有残余，更诚实的写法应继续收窄到 Fib lane 内部的一次强确认，而不是保留成宽版 strength framework。

## 最值得改的唯一一刀是什么
**唯一值得保留的一刀**：

> 把原来的 `weak / medium / strong` 多档 Fib strength admission / sizing，收窄成 `strong-only` 的二元 continuation confirm。

翻成人话：
- 不再问“这次是 weak 还是 medium 还是 strong，该给几成仓位”；
- 只问“这次回踩后，是否出现了足够强的 reclaim / follow-through，值得放行 Fib second-chance continuation”。

这是一刀，因为它只改 **角色写法**：
- 从 `multi-bucket admission/sizing layer`
- 改成 `strong-only binary confirm inside Fib lane`

不顺手偷带：
- 新 exit
- 新 universe
- 新 HTF regime
- 新 microstructure filter
- `fresh pullback -> reclaim` 第二轴

## 是否值得形成新的 derived hypothesis
**暂时不值得直接 draft 成新的 `Rank 83b`；更诚实的是记为 `soft_reframe_candidate`。**

原因：
1. 原 rank 的唯一 residual 已经被收窄到很薄：本质上只剩 `strong-only` 这一刀；
2. 但这条轴目前还**不够 distinct**，很容易和已有的 Fib/confirmation 家族混成一类：
   - 它和 `fresh pullback -> reclaim`、`confirmed reclaim / re-break` 一类旁支语义过近；
   - 现在直接 draft 一个 `Rank 83b`，很容易只是把“强确认更好”重新换壳讲一遍。
3. 因此，本轮更合适的结论是：
   - 保留原 `park`
   - 承认它是 `soft park`
   - 把“只保留 strong-only binary confirm”记成一个**候选方向**，但暂不升格成 queue-facing derived hypothesis。

## 本轮固定回答
1. 原 rank 为什么 park？
   - 因为 `weak/medium/strong` 三档 Fib strength layer 只在低成本下看起来改善，到了更诚实 friction 就失稳；真正正贡献只集中在 `strong` 桶，`medium` 本身仍是坏 pocket。
2. 它更像 hard park 还是 soft park？
   - `soft park`，但明显偏硬；对原三档 sizing 读法已接近 hard park。
3. 有没有可救信号？
   - 有，但只剩 `strong` 桶这条很窄 residual，说明强 reclaim / follow-through 可能仍有信息。
4. 最值得改的唯一一刀是什么？
   - 把多档 strength admission / sizing 收窄成 `strong-only` 的 binary continuation confirm。
5. 是否值得形成新的 derived hypothesis？
   - 暂不值得；本轮只记为 `soft_reframe_candidate`。

## 本轮结论
- `source_rank`: `Rank 83`
- `status`: `soft_reframe_candidate`
- `original verdict kept`: `park`
- `park 倾向`: `soft park，但已明显偏硬`
- `note`: 原 `park` 保留；原 rank 的真正 residual 只剩 `strong` 桶，对应的更诚实改写是把多档 `Fib trend-strength` 收窄成 `strong-only binary confirm`，但这条轴目前仍与既有 Fib reclaim / second-chance confirmation 家族过近，暂不足以直接 draft 成新的 `Rank 83b`

## 备注
- 本轮只更新 `research/park_reframe/`、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- 默认不做 commit：工作区长期存在大量与本轮无关的既有脏文件，为避免混提，本轮只做最小必要文件改动与邮件摘要。
