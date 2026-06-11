# Rank 192 / PAXG-XAUT rich-spread rolling-fair residual mean reversion — survivor follow-up park_to_background

- 时间：2026-03-27 02:59 UTC
- 对象：`Rank 192 / PAXG-XAUT rich-spread rolling-fair residual mean reversion`
- 轮次角色：bot3 survivor follow-up（唯一一次 cheap decisive check）
- 结论：`park_to_background`

## 本轮只回答一个问题
在 Bybit 公共 `1m` 主时钟下，`PAXG/XAUT` 的 `rolling fair spread` rich-side residual（`z > 2 / 2.5`）相对 fixed absolute grid，是否能在显式 maker/taker repair stress 与 UTC 时间分桶下，仍保留足以进入 `P2` 的单边净收敛轮廓。

## 最小实验口径
- 数据：Bybit 公共 `PAXGUSDT` / `XAUTUSDT` 线性合约 `1m` K 线
- 区间：近 `14d`（`2026-03-13 02:56` ~ `2026-03-27 02:55` UTC）
- fair spread：`24h rolling mean/std`
- 方向：只做 rich-side fade（spread 高于 fair spread 时，`short rich / long cheap`）
- 对照组：fixed absolute grid `>20 / 30 / 40bps`
- horizon：`15m / 60m / 180m`
- 成本 stress：
  - `maker4bps_total`
  - `maker_plus_one_repair8.5bps_total`
  - `heavy_repair13bps_total`
- 时间分桶：`UTC 00-08 / 08-16 / 16-24`

## 关键结果
### 1) rolling-fair residual 确实优于 fixed grid，但优势主要停在“毛边更像真”，还没到“净值足够升 P2”
- `z > 2.0`
  - `15m`: gross `+1.54bps`
  - `60m`: gross `+3.12bps`
  - `180m`: gross `+6.71bps`
- `z > 2.5`
  - `15m`: gross `+2.80bps`
  - `60m`: gross `+4.83bps`
  - `180m`: gross `+6.16bps`

对照 fixed grid：
- `fixed > 20bps` 到 `> 40bps` 的 `180m` gross 只有 `+0.97 ~ +1.81bps`
- 说明系统认知确实应继续偏向“rolling fair residual 比固定绝对阈值更有信息量”

### 2) 但 survivor 这一刀要回答的是“够不够进 P2”，答案仍是否定
扣掉显式成本后：
- `z > 2.0, 180m`
  - `maker4bps_total`: net mean `+2.71bps`
  - `maker_plus_one_repair8.5bps_total`: net mean `-1.79bps`
  - `heavy_repair13bps_total`: net mean `-6.29bps`
- `z > 2.5, 180m`
  - `maker4bps_total`: net mean `+2.16bps`
  - `maker_plus_one_repair8.5bps_total`: net mean `-2.34bps`
  - `heavy_repair13bps_total`: net mean `-6.84bps`

也就是说：
- 这条线只有在相当理想的 maker-only 世界里才勉强保留正净值；
- 只要显式承认“成对 maker 不会永远完美、至少会有一次 repair 落到 taker”这一更真实的执行假设，均值立刻转负；
- 这还没算 quote/tick 级 fill uncertainty，只是用 `1m` close 做的最宽松 proxy。

### 3) 时间稳定性也不够干净，180m 的毛边明显带有时段集中
- `z > 2.0, 180m`
  - `UTC 00-08`: `+9.78bps`
  - `UTC 08-16`: `+8.48bps`
  - `UTC 16-24`: `+1.56bps`
- `z > 2.5, 180m`
  - `UTC 00-08`: `+8.92bps`
  - `UTC 08-16`: `+9.21bps`
  - `UTC 16-24`: `+3.32bps`

fixed grid 同样存在时段偏斜，但 rolling-fair residual 也没有展示出“全天段都足够稳、足够厚”的 admission 质量。当前更像少数时间窗里的可疑 pocket，而不是已经足够扎实的前排 P2 候选。

## 为什么这轮不是 promote_P2
`Rank 192` 通过了 survivor follow-up 的一半：
- **方向定义更对了**：rolling-fair rich-side residual 明显优于 fixed absolute grid；
- **但 admission 还没过线**：一旦把单腿 repair 明确写进成本假设，净值就系统性转负；同时 180m 毛边存在明显时间分桶集中。

翻成人话：
这不是“完全没东西”，但也远没到“值得占用 Active P2 槽位继续做 admission”的程度。现在最诚实的动作不是再给它一轮开放式 `keep_P1`，也不是硬升 `P2`，而是承认它目前只是在非常理想的 maker 世界里看起来还行；在更现实的 repair 假设下还不够硬。

## 单一句子结果
`Rank 192 / PAXG-XAUT rich-spread rolling-fair residual mean reversion` 的唯一 survivor follow-up 已收口：rolling-fair rich-side residual 相对 fixed absolute grid 确实更像真信号，但在 Bybit 公共 `1m` proxy 下，一旦显式加入单腿 repair stress，`60m/180m` 净收敛即转负，且 180m 毛边明显集中于部分 UTC 时段，因此当前不足以进入 `P2`，本轮直接 `park_to_background`。

## 运行态回写
- `Surviving candidate slot`：清空（本对象已用完唯一 follow-up）
- `Background pool.latest_parked`：更新为 `Rank 192`
- `cycle_plan[2]`：写入上述单句结果并标记 `done`
- 其余前排槽位保持不变

## 发布备注
- 已重建首页源码：`reports/site/index.html`
- 正式发布到 `/var/www/momentum-report/index.html` 这一步依赖 `sudo`，而当前 bot3 cron 运行态无 elevated 能力，因此本轮只能如实停在“源码已刷新、系统发布受权限阻塞”
