# 2026-03-30 20:23 UTC — Rank 63 park reframe review

## 为什么这轮看 Rank 63
- 继续遵循 `bot6` 轮转：当前默认优先 `Rank 50+`。
- 最近 `7` 天内已被 `bot6` 复盘的 `50+` 号段主要集中在 `50/51/52/54/55/56/57/58/59/60/61/62/67/76/83/86/87/92/96/97/101/104/105/106/110`，`Rank 63` 尚未进入 `park_reframe` 复盘队列。
- 因此本轮选 `Rank 63 / Fib 0.618 hold + 0.5 failure gate`，只做一次低频复盘，不改主 TODO 排班。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_1854_rank63-source-intake-guard-passed.md`
- `research/quant_digests/2026-03-18_1810_fib-0618-hold-05-failure-gate.md`
- `reports/artifacts/scout_rank63_fib0618_hold05_fail_15m/overall_summary.csv`
- `reports/artifacts/scout_rank63_fib0618_hold05_fail_15m/asset_summary.csv`
- `reports/artifacts/scout_rank63_fib0618_hold05_fail_15m/time_stability.csv`
- `reports/artifacts/scout_rank63_fib0618_hold05_fail_15m/cost_trade_stability.csv`
- `research/quant_digests/2026-03-19_2009_abnormal-volume-drydown-long-bias-gate.md`
- `research/quant_digests/2026-03-20_1557_deepest-retracement-hold-quality-gate.md`
- `research/quant_digests/2026-03-22_2228_ordered-fib-touch-chain-not-shared-gate.md`

## 1) 原 Rank 为什么 park？
原 Rank 63 想表达的是：
- 一段向上冲击之后，若后续回踩仍能守住 `Fib 0.618`，同时不出现对 `Fib 0.5` 的失败性跌破，就把它当成一个 shared continuation / retest quality gate；
- 希望它能同时服务 `Fib retest_hold`、`EMA continuation`，甚至给其他 lane 提供更“诚实”的 pullback 定义。

原始直觉并不奇怪：
- `0.618 hold` 像“深但没坏”；
- `0.5 fail` 像“中位支撑也丢了，别再硬讲 continuation”。

但 clean replication 的审计结果非常直白：
1. **原始 `fib618_reclaim_raw` 全资产、全成本都明显负。**
   - 6bps 档 mean total return 约 `-30.32%`
   - 10/15/20bps 继续线性变差
2. **把它收窄成 `volume_gate` / `fib50_fail` 也没有真正救回来。**
   - 6bps 档 mean total return 仍约 `-18.29%`
   - 更关键的是 `volume_gate` 与 `volume_gate_fib50_fail` 几乎一模一样，说明 **“0.5 failure” 这条号称独特的语义，在最小实现里几乎没贡献独立增量**。
3. **再叠 `sma200` 趋势过滤，亏损虽然缩小，但仍没过线。**
   - `volume_gate_fib50_fail_sma200` 在 6bps 档 mean total return 约 `-7.24%`
   - 三个资产仍然全部为负：BTC `-9.37%`、ETH `-7.09%`、SOL `-5.26%`
4. **时间稳定性没有给出“只是某一段失真”的借口。**
   - 三个 bucket 仍全负，只是 bucket_2 少亏一些
5. **它留下的主要改善，来自 generic long-side trend / hold-quality 过滤，不是来自 Rank 63 自己那组二元 Fib 叙事。**

所以它被 park 的核心原因不是“Fib 语义完全没信息”，而是：
**`0.618 hold + 0.5 fail` 这组二元 gate 没能证明自己提供独立、可迁移、跨资产稳定的 shared 增量；稍微少亏的部分也更像 generic long-side hold-quality / trend filter，而不是 Rank 63 这条原命题本身。**

## 2) 它更像 hard park 还是 soft park？
我会把它定为：**soft park，但已经很偏 hard。**

原因：
- 它不是 classic hard park，因为 `0.618 / 0.5` 这组 level 语言至少清楚、可实现、也能审计；
- 但 clean replication 已经把最自然的几刀基本都试过：
  - raw fib reclaim
  - volume gate
  - fib50 fail
  - 再叠 SMA200
- 结果显示：**最像 Rank 63 自己的那部分语义并没站住，真正有点帮助的是 generic long-side trend / dry-down / hold-quality 近邻。**

所以它还没到“完全无定义、完全不可救”的 hard park；但离“值得继续围着原命题迭代”也已经很远了。

## 3) 现有证据里有没有“可救信号”？
有，但很薄，而且方向已经偏离原命题。

### 可救信号 1：long side 确实存在“少一点坏单”的 residual
- `volume_gate_fib50_fail_sma200` 相比 raw 版本明显少亏；
- `failure_before_target_rate` 下降、`target_hit_within_12bars` 仍不差；
- 这说明 **深回踩后的 long-side hold quality** 不是完全没信息。

### 可救信号 2：最近一周的新证据，反复支持“Fib 更像路径质量 / hold-quality 分层”，不是二元 hard gate
- `2026-03-19 abnormal volume dry-down`：说明缩量回踩更像 long-side absorption / hold-quality；
- `2026-03-20 deepest retracement`：说明真正该盯的是路径里最差那一脚，而不是当前收盘还在不在 `0.618` 上方；
- `2026-03-22 ordered Fib touch chain`：说明 Fib 主题留下的残余更像 long-side maturity / path-quality score，而不是三线 shared hard gate。

### 但它不可救的地方也很明确
- Rank 63 自己最想强调的 **`0.618 hold + 0.5 failure` 二元口径**，并没有证明自己比这些新近的 path-quality / hold-quality 表述更独立、更强；
- 尤其 `fib50_fail` 与 `volume_gate` 基本同值，这一点很伤：
  - **说明“0.5 fail”这刀没有形成单独存在的必要。**

## 4) 最值得改的唯一一刀是什么？
如果硬要保留唯一主修改轴，最自然的一刀只剩：

**把 `0.618 hold + 0.5 fail` 从二元 shared gate，降级成 long-side Fib path-quality / hold-quality score。**

也就是：
- 不再问“这根到底有没有守住 `0.618`、有没有跌破 `0.5`”；
- 改成把它写成一个 long-side 质量刻度：
  - deepest retracement 多深；
  - 回踩阶段是否 dry-down；
  - pre-break ladder / maturity 如何；
  - 再把这些东西用于 long-side admission / veto。

但问题也正出在这里：
**这刀并不是 Rank 63 独有的新发现，而是最近已经被 Rank 64b / Rank 101 / Rank 12b 一类 long-side hold-quality 提案基本吸收。**

换句话说：
- 唯一还能切的一刀，不是没有；
- 但它已经不再诚实地属于“Rank 63b”，而更像别的近邻血缘正在表达的内容。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

本轮结论：`keep_park`

原因：
1. 原 `park` verdict 的审计意义很强，应该保留；
2. Rank 63 自己最独特的 `0.618 hold + 0.5 failure` 二元叙事，没有证明出独立增量；
3. 唯一可救残余已经明显漂向更上位的 long-side hold-quality / path-quality family：
   - `Rank 64b`：long-side hold-quality / admission score
   - `Rank 101`：volume dry-down long-side residual note
   - `Rank 12b`：zone persistence / quality gate
4. 如果现在再写一个 `Rank 63b`，大概率只是在重复说：
   - “别把 Fib 写成二元线；把它改成 long-side quality score”
   这件事本身已经被现有 queue 里的近邻提案表达得更诚实。

所以这轮更诚实的选择，不是硬凑一个 `Rank 63b`，而是：
**承认 Rank 63 的 residual value 已经被邻近 hold-quality / path-quality 血缘吸收，保留 park。**

## 6) trade on / trade off（若硬派生会是什么）
本轮不 draft 新假设，因此这里只记录为什么不写：
- **trade on**：若继续写，会落成“long-side Fib path-quality / hold-quality score”，服务 Fib retest_long / EMA continuation 的 long lane；
- **trade off**：但这样会彻底放弃 Rank 63 原本最独特的二元 `0.618/0.5` 叙事，而且与 `Rank 64b / Rank 101 / Rank 12b` 严重重叠，缺少独立存在的必要。

所以本轮选择不派生，比再写一个重复提案更诚实。

## 最终结论
- `Rank 63` 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 63 不是完全没信息，但它留下的 residual 已经不再属于“0.618 hold + 0.5 fail”这条二元 gate 本身；真正活下来的只是 generic long-side hold-quality / path-quality 语义，而这部分已被 Rank 64b / 101 / 12b 一类近邻提案基本吸收，当前不诚实再派生 Rank 63b。**

## 队列写回
建议在 `docs/PARK_REFRAME_QUEUE.md` / `research/park_reframe/INDEX.md` 中登记为：
- `2026-03-30 20:23 UTC | Rank 63 | verdict=keep_park | original verdict kept=park | note=soft park，但已很偏 hard；原 Rank 63 的 0.618 hold + 0.5 failure 二元 Fib gate 没证明出独立增量，唯一残余已漂向 long-side hold-quality / path-quality 语义，并被 Rank 64b / 101 / 12b 一类近邻提案基本吸收，当前不诚实再派生 Rank 63b`

## Git / 风险备注
- 本轮只做最小必要文件改动。
- 当前工作区长期存在大量与本轮无关的脏文件；为避免混提，本轮不做 commit。
