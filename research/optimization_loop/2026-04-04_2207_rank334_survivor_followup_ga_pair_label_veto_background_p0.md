# Rank 334 — survivor follow-up：GA triple-barrier pair-label veto 收口到 background / P0

- 时间：2026-04-04 22:07 UTC
- 对象：`Rank 334 / GA-optimized triple-barrier pair-label veto`
- 本轮角色：survivor 唯一一次 follow-up
- 结论：`drop_to_background / P0`

## 本轮要回答的问题
不是再问这条对象是否 distinct；那件事在 first verdict 已经回答过了。

这轮唯一该回答的是：

> 在同一 pair admission / triple-barrier / cost 口径下，`baseline all-take` vs `GA take/skip veto selected subset`，是否至少留下一个可辩护的 **post-cost positive pocket**；以及 `HRHP / LRLP` 是否真形成可部署双档，而不只是同一 veto 的换阈值重述。

按 policy，这一问回答完，survivor 预算就必须收口，不能再拖。

## 直接证据
证据来自现有 artifact：
- `reports/artifacts/quant_digest_2026-04-04_pair_label_gate/pair_label_gate_summary.csv`
- `reports/artifacts/quant_digest_2026-04-04_pair_label_gate/pair_label_gate_test_trades.csv`

### 1) 聚合层：只证明“少亏一点”，没证明“转正”
`ALL` 行结果：
- baseline net sum = `-151.31`
- take-only net sum = `-43.45`
- baseline avg net = `-0.548`
- selected avg net = `-0.391`
- baseline win rate = `11.96%`
- selected win rate = `13.51%`
- baseline MDD proxy = `-150.59`
- take MDD proxy = `-43.45`

这说明 veto 层**确实能减伤**，但还停留在“把负期望变成少亏一点”。
系统当前需要的不是这个层面的改善，而是至少找到一个成本后仍可辩护的正净边 pocket。这里没有。

### 2) 单 pair 层：没有任何一对转成正净边
三组 pair 里没有一组在 selected subset 上转成正：

- `BTCUSDT-ETHUSDT`
  - baseline avg net = `-0.629`
  - selected avg net = `-0.347`
  - take rate = `17.0%`
  - AUC = `0.679`
- `ETHUSDT-SOLUSDT`
  - baseline avg net = `-0.657`
  - selected avg net = `-0.494`
  - take rate = `55.1%`
  - AUC = `0.471`
- `BTCUSDT-SOLUSDT`
  - baseline avg net = `-0.362`
  - selected avg net = `-0.298`
  - take rate = `49.5%`
  - AUC = `0.539`

其中最像样的是 `BTC-ETH`：
- 它的 AUC 的确最好；
- take rate 压到只剩 `17%`；
- 但留下来的交易单笔仍是 **`-0.347`**，并没有形成正净边 lane。

这已经足够回答 survivor 问题：
**当前 `selected subset` 还不是“挑出好单”，只是“删掉一部分更差的单”。**

### 3) `HRHP / LRLP` 没有形成真正 deployment 分层
当前 digest 里 `HRHP / LRLP` 的意义主要来自 paper 叙事，但这轮 artifact 没有给出一个可以落到 desk deployment 的双档结果，例如：
- `profit-first` 档位留下清晰正期望、但波动更高；
- `drawdown-first` 档位收益略低、但显著更稳。

目前看到的只是统一 take/skip veto 对负收益的缩窄，没有证明可以拆成两个各自自洽的 live 档位。

所以 `HRHP / LRLP` 在当前 runtime 里仍更像研究假设，不是已经站得住的部署分层。

## 为什么这轮不能升 P2
P2 admission 的门槛不是“看起来像有用 filter”，而是要更接近：
- 至少一个 pocket 有成本后正净边，或者
- 已经非常接近 paper trade / paper launch 的最低可信状态。

`Rank 334` 现在还没到这一步。

它满足的是：
- 主题 distinct；
- veto 方向研究上有价值；
- 适合作为 pairs alpha admission-layer 素材。

但它**不满足**：
- 任何单 pair selected subset 已成本后转正；
- 或 `HRHP / LRLP` 已形成可部署分层。

按 policy，这种情形不能继续把 survivor 拖成开放式 `keep_P1`。

## 为什么也不该再继续给第二次 survivor 机会
survivor 规则写得很清楚：
- survivor 只能是上一条 fresh intake；
- 最多只允许 **1 次** 最小 decisive follow-up；
- 这 1 次后若仍未升级到 `P2`，默认移入 `Background pool`。

本轮已经完成这唯一一次 decisive follow-up，而且答案是否定的。
因此最诚实的收口不是“再补一下 barrier grid / 再分一下 regime / 再看看 HRHP/LRLP”，而是直接把对象放回 background。

## 对 runtime 的影响
- `Surviving candidate slot` 清空
- `followup_budget_remaining` 归零
- `Rank 334` 写入 `Background pool`
- 本轮 cycle item 1 标记为 `done`

## 一句话结果
`Rank 334` 的 GA triple-barrier pair-label veto 证明了“筛单能显著减伤”，但没证明任何 pair 会在成本后转成正净边，`HRHP / LRLP` 也没形成可部署双档；因此 survivor 唯一 follow-up 到此收口，对象直接 `drop_to_background / P0`。