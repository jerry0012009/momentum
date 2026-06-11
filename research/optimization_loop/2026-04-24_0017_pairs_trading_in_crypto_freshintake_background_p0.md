# `5m intraday mean reversion / pairs trading in cryptocurrency markets` — fresh intake first verdict `background/P0`

- time: `2026-04-24 00:17 UTC`
- target: `research/quant_digests/2026-04-23_2210_ma-breakout-bubble-admission-crypto.md`
- action: fresh intake：对 `5m intraday mean reversion / pairs trading in cryptocurrency markets` 做 first verdict，只补 1 个最小 decisive blocker（它是否留下相对已 live `Rank 424 / 431` 仍具独立新增价值的 after-cost pairs pocket，而不是只剩 pairs admission / timeout / stat-arb 提示）
- success_criterion: 必须直接输出 `keep_P1` 或 `background/P0`；只有当至少一个非单 pair、非单窗口 lucky-run 的 after-cost pairs pocket 明显成立，且相对现有 live pairs family 仍有独立新增价值，才 `keep_P1`

## 本轮只回答的 blocker
这篇 2020 paper 的 desk 问题不是“pairs 会不会均值回归”，而是：**它现在是否还留下一个相对已 live `Rank 424 / 431` 可独立排队的新 after-cost pairs pocket。**

## 已有 runtime 对照
### Rank 424
- `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`
- 已经把 pairs family 收口成：`cointegration-first admission + strongest residual z-score spread fade` 的可运行宿主。
- 其前序结论已确认至少不是单一 pair 幻觉，核心 pair 集合可落到 live paper runner。

### Rank 431
- `Rank 431 / cointegration maker-first + hard time-stop pairs`
- 已经把同一家族进一步收口到 `rolling admission + maker-first realism + hard time-stop` 的可运行宿主。
- fresh/P2/P3 过程都已明确：这条线真正有价值的是可持续 pair pocket + execution realism，而不是再重复“5m pairs 可能比慢频更好”的母命题。

## 本轮证据
1. 当前 digest 本身给出的硬信息，主要是：
   - `daily` 常见 distance 方法约 `-0.07%` 月收益；
   - `5m` 约 `+11.61%` 月收益；
   - 结果对参数、交易成本、执行窗口高度敏感。
2. 这组信息最多说明：**crypto pairs 的 alpha 更可能出现在 intraday，而不是日频自动成立。**
3. 但这个认知在当前 runtime 中已经不再新：
   - `Rank 424` 已把 `cointegration-first pair admission × spread fade` 接到 live；
   - `Rank 431` 已把 `maker-first + hard time-stop` 的 intraday pairs shell 接到 live；
   - 同家族近期多条 fresh intake 也都被诚实收口为：若没有拿出独立 pair set、独立 after-cost pocket、或更强 execution 壳，就只算 pairs family 组件提示，而不是新的前排对象。
4. 现有可见补充材料也没有推翻这一点：
   - `research/quant_digests/2026-03-25_0958_pairs-selection-funnel-stable-relationships.md` 与其本地 artifact 证明了“稳定选对 funnel”有研究价值，但那条新增点在于 **pair selection funnel**，不是这篇 2020 paper 的主语；
   - `reports/artifacts/quant_digests/pairsbot_transfer_summary_15m_2026-04-21_costladder.csv` 已显示当前 live family 自身就保有多个 after-cost pocket（例如 `AVAXUSDT-ATOMUSDT`、`AVAXUSDT-SUIUSDT` 在 `8/12/16bps` 仍为正），说明 runtime 已经拥有比“5m pairs 可能优于日频”更具体、更可执行的宿主。
5. 因此，本对象当前没有额外证明：
   - 一个区别于 `Rank 424 / 431` 的 durable pair set；
   - 至少两个非单 pair、非单窗口 lucky-run 支撑的新 after-cost pocket；
   - 一个未被现有 live pairs family 吸收的独立 queue-facing alpha 主语。

## 结论
`5m intraday mean reversion / pairs trading in cryptocurrency markets` 的 fresh intake first verdict 已诚实收口 `background/P0`：这篇 2020 paper 当前只再次确认了“crypto pairs 的可交易厚度更可能出现在 intraday，且对成本/参数/执行高度敏感”这一母命题，但没有拿出区别于已 live `Rank 424 / 431` 的新 durable pair set 或独立 after-cost pairs pocket；因此它新增的系统价值只剩 `pairs family historical support / stat-arb 背景论据`，不构成新的 survivor。

## 尾部执行记录（non-blocking）
- homepage publish（`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`）在异步执行中收到 `SIGKILL`，记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知已独立执行并成功发送：`[momentum-bot3-auto] pairs 论文首判收口`。
