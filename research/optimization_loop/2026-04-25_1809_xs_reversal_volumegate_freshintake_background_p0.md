# 2026-04-25 18:09 UTC｜bot3｜fresh intake｜cross-sectional loser→winner fade × volume gate reality check -> background/P0

- Target: `research/quant_digests/2026-04-25_1630_xs-reversal-volumegate-realitycheck.md`
- Action: fresh intake first verdict；只用 1 个最小 decisive blocker 回答：当前 liquid-major `15m` transfer 下，这条 `cross-sectional loser→winner fade × volume gate` 是否至少还保留一个可诚实留在前排的 after-cost pocket，或一个足够清楚的 `15m signal -> 5m execution` survivor 主语。
- Success criterion: 必须直接输出 `keep_P1` 或 `background/P0`；只有当至少一个清楚 universe / gate / execution scope 在成本后仍有诚实可保留边际，且不是靠口径漂移硬留前排，才 `keep_P1`。

## 本轮读取与使用的证据
1. digest：`research/quant_digests/2026-04-25_1630_xs-reversal-volumegate-realitycheck.md`
2. probe summary：`reports/artifacts/quant_digests/2026-04-25_xs-lowvol-reversal_probe_summary.csv`
3. probe script：`reports/artifacts/quant_digests/2026-04-25_xs-lowvol-reversal_probe.py`

## 最小 decisive blocker
要让这条线保留到 `keep_P1`，至少要满足以下二选一中的一个：
- 已有某个明确 pocket 在当前 `15m` liquid-major 映射下 **成本后仍非负/接近可留**；或
- 已有足够具体、由现有证据直接支持的 survivor 主语，能诚实收束成 `15m signal -> 5m execution`，而不是只剩“也许换执行会更好”的泛想法。

本轮结论：**两项都不满足。**

## 为什么不满足
### 1) raw alpha 只有很薄 gross，当前 after-cost 不成立
按现有 probe：
- `unconditional`：gross `+0.2155 bps/bar`，net `-0.4626 bps/bar`，平均 turnover `16.95%`
- `lowvol_z_lt_0`：gross `+0.0896 bps/bar`，net `-0.4090 bps/bar`
- `lowvol_z_lt_-0.5`：gross `+0.0799 bps/bar`，net `-0.3899 bps/bar`
- `highvol_z_gt_0`：gross `+0.1959 bps/bar`，net `-0.1404 bps/bar`，平均 turnover `8.41%`

这说明：
- repo headline 里的 `low-volume reversal` 在当前 liquid-major `15m` transfer 上并没有成立；
- 相对最像 pocket 的 `high-volume` 子样本，虽然 turnover 更低、gross 也不差，但 **在已给定的 taker-ish 4bps one-way 粗成本下仍为负**；
- 因此当前并没有现成的 after-cost 可保留 pocket。

### 2) 还不足以诚实收束成 survivor 主语
现有 digest 的“下一步”里确实提到 `15m signal -> 5m entry`、maker-first、breadth gate 等方向，但这些都还是**后续实验假设**，不是本轮已被证据支持到可直接保留前排的 survivor 主语。

尤其本轮要避免的就是：
- 因为 repo 有完整策略壳，就默认认为执行优化后一定能救活；
- 因为 `highvol_z_gt_0` 比 `lowvol` 好，就把“high-volume router 也许能救”直接包装成 `keep_P1`。

在当前证据里，`high-volume` 只能说明 **作者的 low-volume 叙事不成立，且 volume gate 方向需要重估**；它还不能说明这条 `xs loser→winner fade` 已经有足够 queue-facing 的 short-cycle pocket。

## Verdict
`background/P0`

## 会改变系统认知的话
这条 fresh intake 已诚实收口为 `background/P0`：当前 liquid-major `15m` transfer 下，repo 的 `low-volume reversal` 叙事被 public probe 直接否掉；唯一相对较好的 `high-volume` 子样本在粗成本后仍为负，而所谓 `15m -> 5m execution` / maker-first 也还只是未验证假设，不足以支撑 `keep_P1`。

## 对 runtime 的直接影响
- 不分配 Rank：因为本轮 verdict 不是 `keep_P1 / promote_P2 / promote_P3`。
- 当前小点可直接标记 `done`。
- `Fresh intake slot` 的该对象 latest result 更新为本条 `background/P0` 收口结论。
