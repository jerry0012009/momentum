# Rank 297 / same-underlier multiquote bucket RV — survivor follow-up 收口，回 background/P0

- 时间：2026-04-02 21:48 UTC
- 对象：`Rank 297 / same-underlier multiquote bucket RV`
- 本轮角色：bot3 执行器
- 动作：按 `cycle_plan` 执行唯一一次 survivor follow-up，直接回答 `bucket allocator` 相对 `independent pairs` 的 after-cost 增益是否已经真实存在，从而决定是否从 `P1` 升到 `P2`
- 结论：**不升 `P2`；survivor budget exhausted，回 `background/P0`。**

## 本轮只回答一个问题
在同一套 same-underlier multiquote relative-value 设定下，`bucket allocator` 是否已经被证明确实能比 `independent pairs` baseline 更诚实地改善成本后净收益、冲突敞口治理或回撤控制，以至于值得把 `Rank 297` 升到 `P2`。

## 结论
当前证据还不够支持这个升级，因此最诚实的收口是：**`Rank 297` 不升 `P2`，其唯一一次 survivor follow-up 用尽后回 `background/P0`。**

## 为什么这轮不能升 P2
### 1) 现有可迁移证据主要仍停在 pair-level gross reversion
`2026-04-02_2018_multiquote-bucket-rv-alpha.md` 已经证明：
- 同一底层、多 stable-quote 腿（`BTC/ETH × USDT/USDC/FDUSD`）确实存在可重复的短时 relative-value 偏离；
- `1m/3m/5m/15m` 上都能看到 pair-level 回归形状；
- 多条 spread 同时亮灯并非稀有，因此“统一 allocator 解决冲突”这个工程问题是真实的。

但这些证据回答的是“这条家族有 raw-alpha 痕迹”，**不是**“allocator 已经在 admission 层面创造了比 independent-pairs 更好的 after-cost 结果”。

### 2) 当前可用 proxy 里，成本后并没有出现足以改级别的净边
现有最接近 allocator / multiquote 的公共 artifact 仍然显示：
- `multiquote_ott_probe_20260324/summary.csv` 中，`BTC/ETH` stable-quote pair 的 **gross bps/trade 大多只有约 `0.23 ~ 0.77 bps`**；
- 在统一的 `4/8/12 bps` round-trip 成本口径下，`net4_bps_per_trade` 已普遍转负，`net8_bps_per_trade` 与 `net12_bps_per_trade` 更是全部明显为负；
- `multiquote_ott_proxy_20260324/grid_summary.csv` 里，即便在论文 proxy 的较优参数行上，**8 bps 成本后 net_mean_bps 仍系统性为负**。

这说明当前最扎实的公共证据仍然是：
**same-underlier multiquote RV 有 gross shape，但成本后 edge 还没被 allocator 诚实救活。**

### 3) 我们还没有拿到这次 follow-up success criterion 真正要求的那组 ablation
本轮应回答的是：
- 同 residual / entry / exit / max-hold / cost 设定下；
- `independent pairs` 各自开仓；
- vs `bucket allocator` 统一分配；
- after-cost 到底谁更好。

目前 runtime 可用材料最多只够支持：
- allocator 是合理的实现方向；
- conflict routing 的确值得未来 replication 时补；
- 但**尚未给出一个 clean ablation 证明 allocator 本身改变了成本后 verdict。**

在这种情况下，按 policy 不能把它硬写成 `promote_P2`。

## 为什么也不继续拖在 survivor
policy 已经规定 survivor 只有这一次便宜 follow-up 预算；而这次 follow-up 后，系统认知已经足够清楚：
- 对象主语成立；
- 工程层问题成立；
- 但 admission 所需的决定性证据（allocator 相对 baseline 的成本后净增益）仍未成立。

因此本轮不能再把它拖成长尾开放式“再看看 allocator / 再补一点成本细节”的前排对象；**最诚实的动作就是预算用尽后回 background/P0。**

## 本轮对系统认知的改变
`Rank 297` 不是空洞换壳：same-underlier multiquote bucket RV 的对象主语与 allocator 命题都成立；但当前公开/已有 proxy 证据仍只支持 pair-level gross reversion，尚未证明 `bucket allocator` 能把该家族在诚实成本后稳定抬升到优于 `independent pairs` baseline 的 admission 级结果，因此本轮不升 `P2`，而是在 survivor 唯一一次 follow-up 用尽后回 `background/P0`。

## 写回 runtime 的一句话
`Rank 297` 的 survivor follow-up 已收口：现有证据只证明 same-underlier multiquote RV 存在 pair-level gross 回归与真实 conflict-routing 需求，但尚未证明 `bucket allocator` 相对 `independent pairs` baseline 在成本后有决定性净增益，因此不升 `P2`，survivor budget exhausted 后回 `background/P0`。
