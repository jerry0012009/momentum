# BTC shock × low-trade-count ALT lagged transmission — fresh intake 收口 background/P0

- 时间：2026-04-20 04:13 UTC
- 轮次角色：bot3 fresh intake 执行
- 对象：`BTC shock × low-trade-count ALT lagged transmission`
- 来源：`research/quant_digests/2026-04-20_0028_btc-alt-lagged-transmission-alpha.md`
- 本轮小点：cycle_plan 第 2 项

## 本轮只回答的 blocker

按 bot2 排班，本轮只补 1 条最小 blocker：在严格 delayed-confirmation、防前视时序、coin admission 与统一成本后，BTC→低交易笔数 ALT 的 lead-lag 是否仍有可复制 after-cost pocket。

## 已有公开/本地产物复核

本 digest 自带最近 7d Binance Spot `1m` probe：

- `QKCUSDT`：`corr_lag0=0.0293`，`corr_btc_leads_1m=0.0641`，粗 shock-follow `1m gross≈+5.01bps`；underreaction 子集 `25` 笔，`gross≈+11.05bps`。
- `GNOUSDT`：`lag0=0.0348`，`lag1=0.1098`，粗 shock-follow `gross≈+4.99bps`；underreaction 子集 `42` 笔，`gross≈+8.72bps`。
- `PIVXUSDT`：`lag0=0.0232`，`lag1=0.0367`，粗 shock-follow `gross≈+4.90bps`；underreaction 子集 `15` 笔，`gross≈+13.15bps`。
- `CITY/BIFI` 不满足稳定 lag admission：`CITY` 的 lag1 弱于 lag0，`BIFI` 的 lag1-lag0 为负。

这说明“BTC 先动、少数低交易笔数 ALT 慢半拍”这个机制影子仍存在，但可交易口径不是无脑低流动性篮子，而是非常窄的 coin-admission pocket。

## honesty / execution realism 判断

1. **统一 8bps 后，粗规则不成立。** 最粗的 `BTC shock -> next 1m ALT follow` gross 只有约 `+4.9~+5.0bps`，统一 `8bps` 后直接转负。
2. **underreaction 子集虽有表面正值，但太薄且太稀疏。** `QKC/GNO/PIVX` 的 underreaction 子集分别只有 `25/42/15` 笔；扣 `8bps` 后约只剩 `+3.05/+0.72/+5.15bps` 的小样本余量，且集中在少数 spot 低交易笔数币，缺少可承接的 desk universe / perp 迁移证明。
3. **旧同族对象已给出更强的负面 execution 证据。** `Rank 159 / BTC→ALT trade-count-sorted 1m lag follower` 已在 2026-03-25 survivor follow-up 中验证：desk 可交易 perp universe 内虽保留低 trade-count 更慢半拍的排序方向，但保守 `6bps` 后三个 bucket 最佳 pocket 全为负并已 `drop_to_background`。本轮新 digest 没有提供足以推翻该 runtime truth 的 after-cost / fillability 证据。
4. **可执行性方向仍可作为 background 素材保留。** 若未来人工 reopen，唯一值得重测的是“spot maker-first + 极窄 coin admission + participation cap”而非当前 fresh slot 继续占前排。

## verdict

**结论：`background/P0`。**

`BTC shock × low-trade-count ALT lagged transmission` 的机制证据仍在，但当前可见 edge 在统一成本与可交易 universe honesty 下不足以独立保留为新的 `P1`：粗 delayed-confirmation 规则被 `8bps` 成本吞掉，underreaction pocket 样本过少且集中，且与已被 survivor follow-up 收口为 background 的 `Rank 159` 同族高度重叠。

## runtime 更新

- `Fresh intake slot.current_target` 更新为本 digest。
- `Fresh intake slot.latest_result` 写成本轮 `background/P0` verdict。
- `Background pool.latest_parked` 前置追加本对象。
- `cycle_plan[2]` 标记为 `done`。

## 异步补充（同一小点内最小 honesty 子检查）

后续异步脚本（严格 `t+1` 入场、rolling `q97.5` BTC shock、underreaction gate、统一 `8bps`）完成后，五个候选币全部 `net8_mean_bps < 0`：

- `QKC`: `n=127`, `net8_mean=-7.16bps`, `winrate=11.0%`
- `GNO`: `n=119`, `net8_mean=-7.28bps`, `winrate=11.8%`
- `PIVX`: `n=118`, `net8_mean=-3.57bps`, `winrate=24.6%`
- `CITY`: `n=93`, `net8_mean=-4.74bps`, `winrate=33.3%`
- `BIFI`: `n=120`, `net8_mean=-6.90bps`, `winrate=16.7%`

该补充检查与主结论一致：在可执行时序与统一成本下，没有可独立承接的 after-cost pocket。

## 尾部执行状态

- homepage publish：`bash scripts/publish_homepage_index.sh` 异步进程超时后被 SIGKILL，记为**非阻断尾部失败**（不影响本轮 verdict/state/log）。
- 邮件通知：`send_text_email.py` 已成功发送。

## 一句话结果

`BTC shock × low-trade-count ALT lagged transmission` 在严格 delayed-confirmation + coin admission + 统一 `8bps` 成本后没有留下足够独立、可承接的 after-cost pocket；异步 `t+1` honesty 子检查也确认五币 net8 全负，本轮 fresh intake 直接收口 `background/P0`。
