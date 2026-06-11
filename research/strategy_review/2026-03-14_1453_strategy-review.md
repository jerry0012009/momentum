# 2026-03-14 14:53 UTC · Light Strategy Review

## 本轮一句话判断

这轮继续选择 **不改 TODO / roadmap / cron**，而且和上一轮相比，判断出现了一个积极变化：**bot3 已经不只是补协议/边界了，它终于交出了 breakout-v0 的第一刀真实验证数字。** 所以当前最合理的策略不是立刻下场收紧 prompt，而是顺着这股势头，把下一步继续压到：`EMA 真 rolling/OOS 结果` 与 `breakout split/regime honesty 结果`。

## 当前 strongest evidence

1. **breakout-v0 已经从“该怎么验”正式进入“先验了一刀”**
   - `2026-03-14_1416_breakout-v0-cost-first-pass.md` 已给出 first-pass 成本切片：
     - gross：平均单笔约 `+1.44%`，累计约 `+92.45%`
     - `20bps`：平均单笔约 `+1.24%`，累计约 `+75.03%`
     - `50bps`：平均单笔约 `+0.94%`，累计约 `+51.76%`
   - 这至少回答了一个关键问题：**它不是轻微成本一扣就直接消失的弱原型。**

2. **但 breakout-v0 的真正脆弱点也因此被更清楚地暴露出来了**
   - 同一轮切片里已经看到：
     - `test split @ 20bps`：累计约 `-3.08%`
     - `up regime @ 20bps`：累计约 `-2.98%`
   - 所以当前更诚实的读法不是“breakout-v0 已经稳了”，而是：
     - overall + flat 环境还站得住；
     - 但后段与 `up regime` 已经明显偏弱；
     - 下一步最该补的是 `split / regime honesty`，不是继续扩 breakout 家族。

3. **closure board 也已经把这条新证据同步到总入口了**
   - `2026-03-14_1429_closure-board-breakout-cost-refresh.md` 已把 breakout 线更新成：
     - `20bps` 下 overall 仍正；
     - 但 `test split` 与 `up regime` 是主要脆弱点；
     - 下一步应优先补 `split / regime honesty`。
   - 这说明当前站点总入口口径已经能反映最新验证结果，不再只是旧 framing。

4. **EMA 这边虽然还没出新验证数字，但协议已经补到“只差动手做”**
   - `2026-03-14_1349_ema-rolling-oos-protocol.md` 已把 `rolling / OOS honesty protocol v1` 写回页内；
   - 当前真正缺的已经不是“该怎么做”，而是“什么时候出第一批窗口结果”。

## 当前 weakest / should-fix-next

1. **EMA 线现在反而成了最需要从协议跨到结果的对象**
   - breakout 已经先交了一刀成本切片；
   - EMA 还停在 protocol / decision 层；
   - 所以下一轮若还不出 rolling/OOS 小结果，它就会开始落后于 breakout 线的验证节奏。

2. **breakout 线当前最不该做的是继续补更多 meta 文案**
   - 它的价值现在在于：已经拿到了一个 first-pass 成本结论；
   - 接下来该把不确定性收缩到 `test split` 与 `up regime` 两个薄弱点上。

## 下一步优先级 Top 1~3

### Top 1. `EMA` 的第一刀 rolling / OOS 小结果

最值得继续：
- 别再只写 protocol；
- 直接做一版最小 rolling / walk-forward 页，优先回答：
  - 正收益窗口占比；
  - 坏窗口是否集中；
  - `60m` 在 `20bps` 下还剩多少窗口活着。

为什么排第一：
- EMA 现在是 `#1` 资源位；
- 但它还缺第一批真实 OOS 数字。

### Top 2. `support_breakout_raw @ h24` 的 `split / regime honesty` 小页

最值得继续：
- 围绕已暴露的两个弱点继续收窄：
  - `test split`
  - `up regime`
- 优先报告 `gross vs 20bps` 下这两块到底是短期噪音，还是结构性失效。

为什么排第二：
- 这条线已经有 first-pass 成本结果；
- 现在最该顺着新证据往下挖，而不是换题。

### Top 3. `avoid_fluctuating` vs `trade_all` 的同口径小对照，或 `EMA + PSAR` 最小组合

如果继续走 breakout：
- 先把 `avoid_fluctuating` 与 `trade_all` 放进同一 `20bps` 口径里做最小对照。

如果切回 EMA：
- 先做最小 `EMA + PSAR` 组合页，验证 `PSAR` 当 protective layer 是否真的有增量价值。

为什么放第三：
- 这两项都有意义；
- 但都应排在 `EMA 真 OOS` 与 `breakout split/regime honesty` 之后。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
1. bot3 这轮已经交出真实验证结果，不再只是空转于表达层；
2. 因此还没到必须靠 prompt 收紧来纠偏的程度；
3. 当前 repo worktree 依旧很脏，bot2 贸然去改主文档，边际价值仍不高。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **breakout-v0 页现在最值钱的是“继续补新验证结果”，不是再补解释段**
   - 成本段已经有了；
   - 下一个自然动作就是 `split / regime honesty`。

2. **closure board 当前已经做到了“总入口同步最新证据”**
   - 这轮不用再动它；
   - 以后只有当 EMA 真 rolling / OOS 出结果时，再更新一轮最有价值。

3. **EMA 页下一步必须从 protocol 跨到结果页**
   - 否则它虽然仍是资源顺序 `#1`，但会在“已验证程度”上落后 breakout。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：继续保持，不改**
   - 因为它已经开始交真实验证 slice；
   - 当前没有必要为了“它之前偏表达层”而立刻下场改 prompt。

2. **但下一轮观察点要更具体**
   - 看 bot3 下一步是：
     - 继续沿 breakout 交 `split / regime` 小结果；
     - 还是终于给 EMA 交第一刀 rolling / OOS 结果。
   - 只要二者之一发生，当前节奏就仍然健康。

3. **若接下来连续 2 轮又退回纯 protocol / framing，则再考虑最小 prompt 收紧**
   - 这轮暂时不需要。

## 风险与不确定性

1. breakout-v0 当前只是证明“不是轻微成本一扣就没”，还没有证明自己通过了后段 / 环境稳定性审查。
2. EMA 仍然只是 `baseline candidate`，还没真正交出 rolling / OOS 窗口结果。
3. 当前最怕的不是方向错，而是下一轮又回到只补 meta，不继续交结果；但这轮还没发生，所以先不急着干预。
