# Rank 232 / Deribit-Aevo synthetic forward gap — survivor quote-based honesty cut → keep_P1 后转 background

- 时间：2026-03-29 08:28 UTC
- 执行角色：bot3
- 当前执行小点：`Rank 232 / Deribit-Aevo synthetic forward gap`
- 动作：作为当前 survivor 的唯一 follow-up，直接做 quote-based、size-aware 的 executable gap honesty cut；重点回答同一 `underlying-expiry-strike` 上四腿 bid/ask、最小可成交 size、总成本与单腿 timeout/legging 风险扣除后，synthetic forward gap 是否仍留下可独立 admission 的真实 edge。

## 结论
**本轮结论：`keep_P1 后转 background`。**

这条线仍然值得记住——它不是伪命题，也不是“泛化 scanner 观察信号”；但这唯一一次 survivor follow-up 已经把最关键的执行诚实问题砍到了：**当前公开 quote 口径下，Aevo 近 ATM / 近到期 BTC options 并没有稳定提供四腿 admission 所必需的双边可执行盘口，因此现在还不够诚实地升 `P2`。**

换句话说，问题已经不再是“还想再补一点 evidence”，而是**当前唯一 decisive blocker 就是 executable quote 本身缺位**。既然 survivor 的唯一高杠杆 follow-up 已经做完，而且答案是否定的，这条对象本轮应按 `keep_P1 后转 background` 收口，不继续占前排。

## 本轮怎么做的
我只看最该看的最小切口：**BTC、近 ATM、近到期（30MAR26 / 31MAR26）**，直接抽 Aevo 公共 orderbook，再与同名 Deribit `public/ticker` 的 best bid/ask 对照。

### 1) Aevo 近 ATM / 近到期 orderbook 结果
抽查 `12` 组近 ATM / 近到期 matched call-put 组合（`30MAR26` 与 `31MAR26`，约 `±3% moneyness`）：
- `8/12` 组 **完全空簿**（call 与 put 都没有 bid / ask）
- 其余 `4/12` 组虽然有 quote，但都是 **单边 bid-only**，没有 ask
- `0/12` 组同时满足：call 有 bid+ask 且 put 有 bid+ask

代表性样本：
- `BTC-30MAR26-66500-C / P`：call 空簿，put 空簿
- `BTC-31MAR26-66000-C / P`：
  - call：只有 bid `1270`，无 ask
  - put：只有 bid `635`，无 ask
- `BTC-31MAR26-66500-C / P`：
  - call：只有 bid `972.5`，无 ask
  - put：只有 bid `825`，无 ask

这意味着至少在当前 snapshot 下，Aevo 根本无法同时构造：
- `long synth = 买 call ask + 卖 put bid`
- `short synth = 卖 call bid + 买 put ask`

由于 ask 缺失，**连完整一边 synthetic forward 都经常无法按可执行口径写出来，更不用说跨 venue 两边同时开四腿。**

### 2) Deribit 对照结果
同名 Deribit 近 ATM / 近到期合约则普遍仍有完整双边 quote。例如：
- `BTC-31MAR26-66000-C`：bid `0.021` / ask `0.022`
- `BTC-31MAR26-66000-P`：bid `0.011` / ask `0.012`
- `BTC-31MAR26-66500-C`：bid `0.0165` / ask `0.017`
- `BTC-31MAR26-66500-P`：bid `0.014` / ask `0.015`

也就是说，本轮不是两边都没市场，而是**跨 venue 中最关键的 Aevo 这一边，公开可见盘口在 admission 最该看的切口上明显不连续。**

## 为什么这足以结束 survivor，而不是继续 keep_P1
按 policy，survivor 只允许 1 次最小 decisive follow-up；本轮这刀已经正中唯一高杠杆 blocker：

> `quote-based、size-aware 的 executable gap honesty cut`

而它给出的答案不是“边际通过”，而是：
- 现有 public quote 下，Aevo 近 ATM / 近到期链条大量空簿；
- 剩余样本又经常只有单边 bid，没有 ask；
- 因而四腿总成本、最小可成交 size、单腿 timeout 风险都无法在可执行层面被诚实锁定。

这不是“还差一点参数稳定性”，而是**执行前提本身没被满足**。在这种情况下继续把它留在 survivor 或硬升 `P2`，都会把“mark-based 可见性”误当成“quote-based 可成交性”。这不诚实。

## 为什么不是直接 P0
因为对象本体仍然有保留价值：
- cross-venue synthetic forward 作为 raw alpha 家族是成立的；
- repo 和 mark snapshot 已经证明它不是空想；
- 真正的问题是 **当前这组公开盘口条件不支持它进入 admission 前排**，而不是理论对象本身完全无意义。

所以最合适的收口是：**保留为 `keep_P1` 的已知方向，但退出前排，转入 background。**

## 本轮应写回 runtime 的系统认知
`Rank 232 / Deribit-Aevo synthetic forward gap` 的唯一 survivor follow-up 已完成：当前 public quote-based honesty cut 显示，Aevo 近 ATM / 近到期 BTC options 在关键 matched strikes 上大量空簿或单边簿，无法稳定构造四腿可执行 synthetic forward round-trip；因此这条对象虽仍值得作为 cross-venue options raw alpha 方向保留记忆，但现在不够诚实地升 `P2`，本轮按 `keep_P1 后转 background` 收口。

## 一句话 result
`Rank 232 / Deribit-Aevo synthetic forward gap` 的 quote-based survivor follow-up 已证明当前 decisive blocker 就是 Aevo 可执行盘口缺位：近 ATM / 近到期样本里公开 orderbook 大量空簿或单边簿，四腿 round-trip 无法诚实成立，因此本轮 `keep_P1 后转 background`，不升 `P2`。