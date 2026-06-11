# Rank 344 / winner-only × loser-short veto XS continuation — fresh intake first verdict

- 时间：2026-04-06 00:26 UTC
- 对象：`research/quant_digests/2026-04-05_1919_winneronly-losershort-veto-xs-alpha.md`
- 本轮角色：`fresh intake`
- 结论：`keep_P1`
- 正式编号：`Rank 344`

## 这轮只回答一件事
这条 intake 到底是不是一条 **distinct 的 cross-sectional raw alpha 壳**，还是只是把 textbook `winner-minus-loser` / market beta / long-only drift 重新包装了一遍。

本轮 first verdict：**它值得保留到 `P1`。**

但保留的主语不是“经典 WML 还有效”，而是更窄、更诚实的：
- **alpha 本体：** `winner-only cross-sectional continuation`
- **必要边界：** `loser-short veto`
- **默认诚实对照：** `cash` / `light BTC hedge` / `beta-adjusted attribution`

## 为什么不是直接打回 background
### 1. 它不是把老的 WML 叙事原样搬来
原 digest 里最有用的不是“横截面动量强”，而是相反：
- XSM 整体并不稳；
- short loser 那条腿经常带来 jump / rebound / liquidation-style path damage；
- 真正留下来的更像 **winner leg continuation**，而不是 `winner-minus-loser` 这整个 textbook 配方。

这使它和“默认 long winners + short losers”的旧读法有了清楚分界：
**这条新 intake 的独立主张是：把 loser short 当作默认 veto 对象，而不是默认组成件。**

### 2. 它回答的是 desk 还值得测的一条 raw alpha，而不是纯 overlay
如果这条东西只是在说“beta 好的时候 winners 也涨”，那不值得留。

但它至少明确压出了一个可测壳：
- 在高流动性 perp 主池内，按 recent cross-sectional relative strength 选 top bucket；
- 只保留 winner continuation 这条腿；
- 用 `loser short veto`、`after-cost mean log return`、`path-wise liquidation stress` 去阻止把假 alpha 误判成真 alpha。

这已经不是泛泛的宏观解释，而是一个可进入下一步便宜诚实验证的 raw alpha skeleton。

### 3. 它的诚实边界写得比常见 momentum intake 清楚
这轮最值钱的不是收益数字本身，而是边界被压清：
- 不能只看 `mean return`，必须看 `after-cost mean log return`；
- 不能默认 loser short 合法；
- 不能把 `winner-only` 裸奔收益直接当作 alpha，必须对照 `cash / BTC light hedge / beta-adjusted attribution`。

也就是说，这条线**不是先假设能赚，再补风险说明**；而是一开始就把最可能误判的部分写出来了。

## 为什么也还不能直升 P2
它现在仍停在 source / paper-level壳体：
- 证据主要来自日级 paper 口径；
- 还没有证明在我们 desk 的 `15m / 5m high-liquidity perp` 口径里，winner-only 仍然留下独立于市场 beta 的 after-cost 增益；
- `loser-short veto` 的必要性在论文里有强提示，但还没在我们自己的 universe / fee / holding 设定里做最小并排验证。

所以这轮最诚实的 first verdict 不是 `P2`，而是：
**先保留到 `P1`，等待一次唯一 follow-up 去确认它到底是 distinct XS continuation，还是最终会塌回“long-only beta 包装”。**

## 本轮写回的 runtime 含义
- 新对象正式编号：`Rank 344`
- verdict：`keep_P1`
- 它占据新的 survivor 合法入口，等待那唯一一次最小 follow-up
- follow-up 的核心问题应收敛为：
  1. `winner-only` 相对 `WML` 是否在我们口径里确实更稳；
  2. `loser-short veto` 是否是必要规则，而非样本期巧合；
  3. 去掉市场 beta 后，这条线是否还留下可转移的 cross-sectional alpha。

## 发布/通知
- 首页刷新：已执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，但运行态卡在脚本内的 `sudo mkdir/install/chown`；当前 cron 运行环境不提供 elevated exec，因此这轮未能完成 `/var/www/momentum-report/index.html` 部署。
- 邮件摘要：已发送（subject=`[momentum-bot3-auto] Rank 344首判保留`）。

## 一句话结论
`Rank 344 / winner-only × loser-short veto` 值得保留，因为它把“crypto 横截面动量真正可搬运的部分可能只在 winner leg，而 loser short 主要制造尾部伤害”压成了一个独立且诚实的 raw alpha 壳；但它还没证明自己已经脱离 market beta 包装，因此本轮只写 `keep_P1`，不直升 `P2`。
