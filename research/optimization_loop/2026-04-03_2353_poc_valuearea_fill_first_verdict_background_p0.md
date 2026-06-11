# Rankless fresh intake first verdict：POC / value-area fill sanity 直接收口到 background/P0

- 时间：2026-04-03 23:53 UTC
- 对象：`research/quant_digests/2026-04-03_2224_poc-valuearea-fill-sanity-alpha.md`
- 轮次角色：bot3 auto execution
- 对应动作：`cycle_plan` 第 3 项（conditional fresh intake）
- 结论：`background/P0`

## 这轮只回答一个问题
这条 `POC / value-area displacement -> fill/return` 题，是否已经足够构成一个可继续前排推进的独立 raw alpha 主语，而不是停留在 volume-profile 术语包装和乐观成交假设上。

## 读完 source 后的关键事实
根据 intake digest 里的最小复核，这个 repo 的 base alpha 主语本身是清楚的：

- 用 rolling volume-profile proxy 算 `POC`
- 观察价格相对 `POC` 的偏离
- 下注价格向 `POC / value area` 回摆，或把同一偏离当 continuation shell

但真正决定 verdict 的不是“主语清不清楚”，而是它在 honest execution 下是否还保留足够厚的边。

本轮直接采用 digest 中已经给出的最小诚实复核结果：

- 把乐观的 stale fill 改成 `signal bar close -> next bar open` 后
- `fade + EMA200 + next-open` 只剩约 `1.53 bps` 的可承受 round-trip 成本阈值
- `follow + EMA200 + next-open` 也只剩约 `2.24 bps`
- digest 已明确指出：一旦脱离 repo 里的理想化成交口径，fade / follow 都只剩很薄的 gross edge，真实 crypto 执行里基本一加成本就死

## 为什么这轮不留在 P1
按当前 policy，这一轮要的是 fresh intake 的 first verdict，不是给术语好听的对象发一张继续观察券。

这条对象的问题不是“还差一点点补测”，而是：

1. **当前正边主要依赖 fill 假设，而不是策略本体厚度**
   - digest 已经说明，同样数据下，只要保留过期理想价成交，连信号方向都可能被 fill 假设盖过去。
   - 这说明当前 repo 更像 execution illusion，而不是已诚实站住的 standalone alpha。

2. **honest shell 下边太薄，不足以支撑前排继续推进**
   - 对 desk 而言，`1.5~2.2 bps` 量级的成本容忍度不够当作可 paper 化的独立候选。
   - 这不是“再多跑一轮就会突然变厚”的问题，而是第一性结论已经很清楚：当前 standalone 壳不够强。

3. **真正值得保留的是 feature，不是当前 standalone strategy shell**
   - digest 里最有价值的部分其实是：
     - `distance_to_POC`
     - `POC_drift`
     - `value-area excursion`
   - 它们适合以后作为共享特征/状态变量复用，但这不等于当前这条 fresh intake 应该继续占用前排槽位。

## verdict
本轮 fresh intake first verdict 直接收口：

> `POC / value-area fill sanity` 虽有清楚的 rolling POC displacement 主语，但在把成交口径改成诚实的 next-open / 非 stale fill 后，只剩约 `1.5~2.2 bps` 量级的毛边；当前优势主要来自乐观 fill，而不是足够厚的独立 alpha，因此不保留为前排 `keep_P1`，直接落回 `background/P0`。

## 对 runtime 的直接影响
- `Fresh intake slot` 的当前对象完成 first verdict，收口到 `background/P0`
- 下一条 fresh intake 头顺延到：`research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
- `cycle_plan` 第 3 项状态改为 `done`
- 本轮不分配新 `Rank`，因为 verdict 未达到 `keep_P1` 或更高

## 最短版
这条题不是完全没信息，但目前更像“可拆成 feature 的价量锚点素材”，不是值得继续前排推进的独立 raw alpha；因此 bot3 本轮直接把它收口到 `background/P0`。