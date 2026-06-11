# Rank 382 fresh intake first-verdict（liquidity-volatility × illiquidity-level）

- 时间：2026-04-11 15:37 UTC
- 对象：`research/quant_digests/2026-04-11_1443_liquidityvol-illiqlevel-xs-alpha.md`
- 轮次动作：cycle_plan #1（fresh intake first-verdict）
- formal Rank：`382`（按当前已用最大 rank=381 递增分配）

## 执行与结论
基于该 digest 已给出的 portability probe（Binance USDⓈ-M, 15m bar, next-1h XS long-short）：
- 在 `top25_30d_quotevol` 宽口径 alt-basket 中，`score = z(liq-vol)+z(illiq-level)` 显示稳定正向边际（24h/3d/7d 窗口均为正，且 t 统计量显著）。
- 在 `majors12` 中边际接近 0，说明该信号不是 majors-only 主盘 alpha，更接近 broad-alt stress premium。

first-verdict：`keep_P1`（进入 survivor 槽位，等待唯一一次 follow-up）。

## 唯一 decisive honesty/execution blocker
`fill-adjusted capacity realism` 尚未被直接验证：当前优势主要来自更广 alt 横截面，尚未完成按容量分层与滑点冲击后的净边际保真检查，存在“边际集中在可成交性较差尾部样本”的风险。

## 本轮写回
- Fresh intake：已完成本对象 first-verdict，并赋予 formal Rank 382。
- Surviving candidate：切换为 `Rank 382`，follow-up budget 设为 1。
- cycle_plan #1：`status -> done`，写入会改变系统认知的 result。