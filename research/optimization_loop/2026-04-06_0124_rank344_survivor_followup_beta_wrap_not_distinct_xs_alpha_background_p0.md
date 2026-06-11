# Rank 344 / winner-only × loser-short veto XS continuation — survivor follow-up

- 时间：2026-04-06 01:24 UTC
- 对象：`Rank 344 / winner-only × loser-short veto`
- 本轮角色：`Surviving candidate`（唯一一次 follow-up）
- 结论：`drop_to_background / P0`

## 本轮只回答一件事
`Rank 344` 在 desk `high-liquidity perp` 口径下，是否已经足够证明自己是**独立于市场 beta 的 after-cost winner-only XS continuation**，从而值得升入 `P2`。

本轮答案是否定的。

## 为什么这轮不升 P2
### 1. 现有证据仍主要证明“loser short 很危险”，没有证明“winner-only 是独立 XS alpha”
首判里最清楚的结论其实是：
- textbook `winner-minus-loser` 在 crypto 里不该默认照搬；
- `loser short` 容易引入 jump / rebound / liquidation-style path damage；
- 评估时必须看 `after-cost mean log return` 与路径诚实性。

这些都成立，但它们更像**风险否定结论**，不是足以单独抬升层级的正向 admission。

换句话说，当前证据说明了“不要轻易 short losers”，却还没有说明：
**在去掉 `loser short` 以后，剩下的 `winner-only` 到底是可迁移的横截面 alpha，还是只是 crypto risk-on / BTC beta / trend participation 的包装。**

### 2. 对象自己的 surviving question 还没有被正面答穿
这条 survivor 的唯一任务，是并排回答：
1. `winner-only` 相对 textbook `WML` 是否更稳；
2. `loser-short veto` 是否必要；
3. `cash / BTC light hedge / beta-adjusted attribution` 后是否仍保留可迁移增益。

第 1、2 点在 paper 级别有方向性支持；
但第 3 点——也是最决定层级的那一问——当前并没有 desk 口径的新证据把它答穿。

没有这一步，就不能把它诚实写成 `P2 admission candidate`。

### 3. 它与已有“只做强状态 long、少做空头”家族高度相邻，但 distinctness 仍未被压清
在当前库里，`winner-only / long-leg-dominant / loser-short-veto` 这条叙事，与已有的：
- `bull-state-only` 市场动量读法
- `winner basket` 替代书
- `long-only + light hedge` 这类 desk 迁移口径

是高度相邻的。

也就是说，现阶段我们更清楚地知道：
- **short 端会伤害复利**；
- **long 端可能值得保留**；

但还没有足够新证据证明 `Rank 344` 提供的是一条**不同于现有 long-only momentum/beta participation 家族**的独立 XS raw alpha 身份。

如果现在硬升 `P2`，本质上是在拿“去掉明显有害的 short 腿”替代“证明剩余 alpha 独立成立”。这一步不诚实。

## 为什么这轮也不是 keep_P1
按固定 policy，survivor 只有这一次 follow-up 预算。

这轮 follow-up 后，系统认知已经收口到：
- `loser-short veto` 作为风险约束是成立的；
- 但 `winner-only` 在 desk `high-liquidity perp`、`after-cost`、`beta-adjusted` 口径下仍未证明自己是独立 XS alpha；
- 因此它不能继续以“再补一点 beta 归因 / 再补一点并排验证”的名义留在前排。

所以这轮必须按 policy 收口，而不是继续开放式拖延。

## 本轮写回 runtime 的含义
- `Rank 344` 的 survivor 唯一 follow-up 已用完；
- 结论不是 `promote_P2`，而是：
  - 现有证据只足够把它保留为一个**有价值的 research note / risk lesson**：`crypto XS momentum 不应默认带 loser short`；
  - 不足以把它升级成当前前排的独立 `P2` admission 对象；
- 因此本轮将其移入 `Background pool / P0`。

## 发布/通知
- 首页刷新：已执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，但脚本卡在 `sudo mkdir/install/chown`；当前 cron 运行环境不提供 elevated exec，因此本轮未能完成 `/var/www/momentum-report/index.html` 部署。
- 邮件摘要：已发送（subject=`[momentum-bot3-auto] Rank 344收口退回背景`）。

## 一句话结论
`Rank 344` 成功证明了“textbook WML 不该直接照搬、loser short 应默认 veto”，但还没有证明去 beta 与成本后仍存在可迁移的独立 winner-only XS alpha；因此 survivor 预算在本轮耗尽，按 policy 收口到 `Background pool / P0`，不升 `P2`。
