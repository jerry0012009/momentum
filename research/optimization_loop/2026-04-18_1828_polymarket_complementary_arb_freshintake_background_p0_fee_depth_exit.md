# Polymarket complementary arb fresh intake：background/P0

- 时间：2026-04-18 18:28 UTC
- 对象：`research/quant_digests/2026-04-18_1240_polymarket-dumphedge-complementary-arb.md`
- 动作：fresh intake 最小首判，只补 1 个 honesty / execution realism blocker：公开 CLOB 下 `YES+NO<1` 的补体错价，在手续费、滑点、可成交深度与到期前退出约束后，是否仍留下独立可交易净边际。

## 读取到的最关键公开证据
1. digest 的 base alpha 是 `YES ask + NO ask < 1` 的结构性补体错价；但它并没有给出公开盘口分布、可成交深度统计、或 fee 后真实 net edge 分布。
2. repo README 把 `dump_hedge` 描述成 guaranteed locked profit，但同时它自己的默认参数不是“只要 `<1` 就做”，而是：
   - `DH_SUM_TARGET=0.93`
   - `DH_MIN_DISCOUNT=0.02`
   - `PAPER_SLIPPAGE_PCT=0.005`
3. 这说明作者自己默认也不把“轻微 `<1` 折价”当作可直接成交的 alpha，而是要求至少数个百分点的 gross 折价，给 fee / slippage / 双腿成交失败 / 提前退出折损留出缓冲。
4. 该 README 仍未给出：
   - 公开市场中 `YES+NO<1` 事件的频度与持续时间
   - 双腿同时按可见 ask / FAK 真正成交的深度证明
   - 提前退出时 `combined sell` 的可实现分布
   - 不持有到结算时的资金占用与剩余寿命筛选后 net PnL 分布

## 本轮最小 honesty 结论
把题目诚实压成“公开 CLOB 的 `YES+NO<1` 补体错价本身是否足以成为 front object”时，当前公开证据并没有证明泛化的 `<1` discount 在现实口径下仍有独立净边际；反而 repo 自己的默认 admission 已经隐含承认：只有深折价（约 `<=0.93`，且至少 `2c` 缓冲）才可能覆盖执行摩擦。

因此，本轮不能把它保留成一个“只要 `YES+NO<1` 就值得继续跟进”的前排新对象。当前更诚实的表述是：
- 若未来能拿到真实 order-book 事件样本，证明**深折价 complementary mispricing** 在公开盘口下可重复出现且双腿可成交，才值得作为一个更窄 spec 重新 intake；
- 但以目前 digest + README 公开信息，`YES+NO<1` 这条泛命题尚未证明自己足够独立、足够可执行。

## Verdict
`Polymarket YES+NO < 1 补体错价` 本轮 fresh intake 直接收口 `background/P0`：repo 默认入场门槛已隐含要求远深于 `<1` 的折价缓冲（`DH_SUM_TARGET=0.93`、`DH_MIN_DISCOUNT=0.02`），而当前公开材料没有给出 fee / slippage / depth / early-exit 后仍可复制为正的真实盘口证据，因此它暂时更像一个需要极深折价才成立的结构性想法，而不是已被公开证据支撑的独立 front object。

## Tail step status（异步回执）
- homepage publish：`bash scripts/publish_homepage_index.sh` 任务在等待中被 SIGKILL 终止（非阻断尾部失败，不回滚本轮 verdict/state/log）。
- email notify：`send_text_email.py` 已成功发送。
