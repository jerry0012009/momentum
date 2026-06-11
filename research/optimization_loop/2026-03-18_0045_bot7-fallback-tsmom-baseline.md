# 2026-03-18 00:45 UTC — bot7 fallback：补《Time Series Momentum》基础 alpha 母论文 digest

## 为什么这次选这个
- 顶板顺序先看 `Run 1 -> Run 2 -> Run 3`。
- `Run 1 / EMA` 已在 `00:02 UTC` 完成 crypto due-now refresh，当前重新回到 `running paper / waiting_not_due`。
- `Run 2 / Scout Fast Lane` 仍是 authoritative board 已明确写死的 `exhaustion state`，没有新的合格 `paper / repo based 5m / 15m crypto` intake 可认领。
- `Run 3 / tiny-live plumbing` 当前唯一会改状态的 `Rank 2 / SOLUSDT whitelist-bound test/no-fill replay` 仍卡在 **execution surface 缺席**：browser 可见 openclaw context `tabs=[]`，没有可附着的交易 venue / operator tab。
- 由于满足 `Run 1 waiting_not_due + Run 2 exhausted + Run 3 externally blocked`，按 desk 规则，这轮在写 `NO_PROGRESS` 前允许借用一次 `bot7-style quant digest`。最近 `30m` 内没有新的 quant digest，因此本轮改做 1 篇不重复的小 digest。

## 做了什么
1. 重读 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`，确认本轮应走 fallback。
2. 重读 `docs/RESEARCH_AUTOMATION_BRIEF.md`、`docs/RECENT_PAPER_SEEDS.md`、`reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`，从未重复主题里挑出 `Moskowitz, Ooi, Pedersen (2012) / Time Series Momentum`。
3. 用开放可读页面抓取论文摘要与元数据，写成新 digest：
   - `research/quant_digests/2026-03-18_0043_moskowitz-tsmom-alpha-baseline.md`
4. 追加更新：
   - `research/quant_digests/INDEX.md`
5. 生成 reader-facing 页面并刷新首页：
   - `python3 scripts/build_quant_digest_site.py`
   - `bash scripts/publish_homepage_index.sh`

## 核心结论
- 这篇论文最重要的价值，不是给当前 15m crypto desk 一个现成执行模板，而是给出一条**足够硬的基础 alpha 母主线**：资产自己的过去方向，确实可能对未来方向有预测力。
- 它对当前项目最值得复用的点，是 **baseline framing**：先用最朴素的 own-past persistence 检查“有没有 alpha 味道”，再谈 pullback / breakout confirmation / no-overlap / friction honesty。
- 因此这轮产物的定位是 **reader-facing baseline doctrine digest**，不是重新打开 `Run 2` fast lane，也不是假装 `Run 3` blocker 已解除。

## 验证 / 证据
- 外部来源：`https://www.sciencedirect.com/science/article/pii/S0304405X11002613`
- 抓到的开放摘要核心证据：
  - 在 `58` 个流动性较好的股指、外汇、商品、债券期货上观察到显著 `time series momentum`；
  - `1~12` 个月过去收益存在延续，更长周期才开始部分反转；
  - 跨资产分散的 TSMOM 组合带来显著 abnormal returns，并在极端市场里更强。
- 网页落点：
  - `reports/site/reading/quant_digests/2026-03-18_0043_moskowitz-tsmom-alpha-baseline.html`
  - `reports/site/reading/quant_digests/report.html`
  - 首页索引已刷新到 `https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 本轮读取到的是开放摘要页与文献元数据，不是完整逐节精读；因此这次更像 **小而诚实的 baseline digest**，不是 full replication brief。
- 论文证据来自较长周期期货，不应直接把收益幅度或窗口长度硬套到 `15m crypto`。
- 当前工作区仍有大量与本轮无关的脏文件，不适合混合提交。

## 下一步建议
- 若后续仍遇到 `EMA waiting_not_due + Scout exhaustion + Run 3 execution surface absent`，可以继续低频用 `bot7-style digest` 补 desk 真正缺的“母论文 / 机制 / 验证层”空白，但前提是不要和最近 digest 重复。
- 真正会改变当前 tiny-live 状态的动作，仍然只有：出现一个已附着、已登录、能回填 `intent + ack + cancel/close` 真实 refs 的 execution surface。

## Commit hash
- 未提交。
- 原因：repo 中存在大量与本轮无关的脏文件；本轮只做了新增 digest / 索引 / 网站生成，不适合安全 selective commit。
