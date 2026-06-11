# 新上币 early-short 更宽 shell distinctness first verdict -> background/P0

- 时间：2026-04-22 16:48 UTC
- 对象：`research/quant_digests/2026-04-22_1115_newlisting-early-short-bubblefade-shell.md`
- 本轮动作：fresh intake first verdict
- 结论：`background/P0`
- 对应 cycle_plan 小点：2

## 这轮只回答的唯一 blocker

按 cycle_plan，本轮只补 1 个最小 decisive blocker：这条更宽的 `3d listing-age + funding-positive high-window short fade` shell，是否相对已 live 的 `Rank 434 / newlisting early-short bubble fade` 仍保留 **未被当前 runner 吸收的独立新增 after-cost pocket**。

## 最小 distinctness 检查

只做最小上下文对比，不重开第二轮 admission：

1. 读取原始 digest `research/quant_digests/2026-04-22_1115_newlisting-early-short-bubblefade-shell.md`；
2. 对照 `Rank 434` 的 fresh intake / survivor / P3 launch wiring 记录；
3. 对照已落库的 live runner `scripts/run_rank434_newlisting_earlyshort_paper_runner.py` 的冻结 launch spec。

## 对比结果

### 1) 基础 alpha 完全同源

当前 shell 的核心定义就是：
- `listing age >= 3d`
- `close` 仍处最近 `3d` 高位附近
- `funding > 0`
- 做空新上币早期泡沫并吃回落

而这正是 `Rank 434` 已经完成 `keep_P1 -> promote_P2 -> promote_P3 -> connected_runner_live` 的同一条 raw alpha 主线，不是新的对象族。

### 2) Rank 434 已吸收 shell 中真正有价值的 desk 化收口

`Rank 434` 不是只保留原 repo 的 `30%TP/15%SL/30d` 慢版本；它已经把这条 shell 中对 short-cycle desk 真正重要的部分冻结进 live runner：

- `3d listing-age gate`
- `funding-positive`
- `3d high-window` 的高位 short fade 定义
- `8% TP / 5% SL / 3d timeout` 的 short-cycle 退出口径
- 每 symbol/listing window `1~3` 笔 cap
- `+100bps` early-listing execution buffer
- paper runner 中显式记录 `short availability / child fill realism / listing-age gate`

换句话说，这条“更宽 shell”的新增内容并没有停留在 queue 外；它已经被 `Rank 434` 的 runner / scheduler / first verified run 吸收并上线。

### 3) 当前 shell 没有指出新的独立 pocket，只是更宽措辞

本轮没有发现任何能把它与 `Rank 434` 区分开的新增对象级内容，例如：
- 不同交易所 / 不同市场结构；
- 新的 listing-age 子窗口；
- 与 `Rank 434` 不同的 entry/exit 逻辑；
- 新的 liquidity tier / borrow / short-availability 过滤后产生的独立 after-cost pocket；
- 一条不能由当前 `Rank 434` runner 覆盖的新增 sleeve。

因此它在 runtime 中更像 `Rank 434` 的上游 digest / 宽口径描述，而不是值得再占一个 fresh intake / survivor / P2 / P3 槽位的独立新候选。

## 本轮 verdict

`research/quant_digests/2026-04-22_1115_newlisting-early-short-bubblefade-shell.md` 诚实收口 `background/P0`：其核心 raw alpha、desk 化约束与 execution realism 已被已 live 的 `Rank 434` 完整吸收，本轮未发现额外独立 after-cost pocket，因此不再作为新的 front-slot 候选保留。

## 对 runtime 的直接影响

- `Fresh intake slot.latest_result` 更新为：这条更宽 shell 已被 `Rank 434` live runner 吸收，收口 `background/P0`
- `Fresh intake slot.latest_result_record` 指向本日志
- `cycle_plan` 第 2 项写回 `done`
- `cycle_plan` 第 2 项 `result` 写为：`新上币 early-short 更宽 shell` 未留下相对 `Rank 434` 的独立新增 pocket，收口 `background/P0`
- `Background pool.latest_parked_record` 追加本日志

## 一句话结果

这条更宽的 `newlisting early-short` shell 没有留下相对已 live `Rank 434` 的独立新增 pocket；新增价值已被当前 runner 吸收，因此本轮直接收口 `background/P0`。
