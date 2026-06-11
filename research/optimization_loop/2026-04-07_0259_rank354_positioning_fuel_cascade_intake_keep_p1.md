# Rank 354 — BTC crowd-positioning fuel-cascade fresh intake first verdict: keep P1

- Time: 2026-04-07 02:59 UTC
- Object: `research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `keep_P1` → promote into `Surviving candidate slot`
- Assigned rank: `Rank 354`

## Why this changed system belief
这条对象不是把常见 funding / basis / sentiment 叙事换壳；它的独立主语是 **public crowd positioning + OI 所刻画的 squeeze / cascade / forced-liquidation fuel state**，并且已经给出可直接拆成 `state -> trigger -> hold -> exit` 的最小交易壳：

1. 输入口径独立且公开可取：`top/global long-short ratio + OI + klines`；
2. 交易语义不是慢情绪温度计，而是“拥挤燃料是否已装满 / 是否快烧完”；
3. entry / exit 已有可独立复现的最小规则，尤其 `fuelShift >= 13pp` 与 `24h` 固定退出把 trend/cascade 与 liquidation-bounce 两种书分开；
4. 当前更像 `high-idea / medium-evidence`：README 研究长文把主语与规则写清了，但尚未给出可审计代码、trade blotter 与独立复算结果。

## First verdict
**结论：`keep_P1`。**

原因不是相信 README 自报收益，而是确认这条线已经满足 fresh intake 的最低保留标准：
- 有独立 raw alpha 主语；
- 有公开数据口径；
- 有可拆开的最小实验壳；
- 与最近的 carry / basis / microstructure / pairs 家族不重合。

但本轮还不能直接升 `P2`，因为决定性缺口仍在：
- 目前证据仍主要是 source-audited README，而不是 code-audited 结果；
- 尚未独立确认 `PB14-L / PB12 / FLIQ-L` 三个最清楚分支在更诚实 cost 口径下是否仍保留可迁移 edge；
- `fuel exit` 优于普通 trailing stop 的关键说法仍未独立复算。

## Slot consequence
- `Rank 354` 进入 `Surviving candidate slot`
- 默认只保留 **1 次** 最小 decisive follow-up
- 下一步若做 follow-up，应优先回答唯一高杠杆问题：
  **在独立复现语境下，`PB14-L / PB12 / FLIQ-L` 是否至少有一个分支在诚实 fee/slippage/funding 口径下仍保留最小可迁移 after-cost edge；若没有，就应直接退出前排。**

## Delivery notes
- 中文邮件摘要已发送。
- 首页刷新脚本已尝试执行，但本轮 cron 运行环境无法使用 elevated 权限，脚本在 `sudo mkdir/install/chown` 步骤无法完成；因此本轮 reader-facing 首页未成功发布，运行结论已先写回 runtime 与内部日志。
