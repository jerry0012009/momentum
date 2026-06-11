# 2026-04-04 16:16 UTC｜Rank 73 / PSAR close-confirmed follow-up gate park reframe

## 轮次定位
- 席位：`bot6 park-reframe loop`
- 本轮处理对象：`Rank 73`
- 原始结论保持：`park / evidence pool`
- 本轮结论：`keep_park`

## 为什么本轮选 Rank 73
- 继续遵守 `PARK_REFRAME_QUEUE` 的优先顺序：先看 `Rank 50~79`。
- `Rank 73` 属于该号段，且最近 `7` 天内未见 bot6 对同一 rank 的 park-reframe 复盘记录。
- 最近新增证据里，刚好出现了几条能回答“PSAR 更像该放在 fixed-bar follow-up gate，还是放在别的职责层”的旁证，因此值得低频复盘一次。

## 原 rank 为什么被 park
原始 `source intake + minimal clean replication` 给出的 blocker 已经很清楚：
1. **它没有真正改善 follow-up 质量。**
   - 在 `breakout_short` 上，`close_confirmed_n2` 相比 `raw_trigger` 并没有减少 early fail / false break，反而 post-cost 更差。
   - 在 `ema_psar_long` 上，`close_confirmed_n2 / n3` 主要效果是砍单，而不是把 setup 救活；收益更差，`positive_asset_ratio` 也掉到 `0/3`。
2. **它的新增信息主要停留在“等几根 bar”这个机械层。**
   原假设把 PSAR 的价值写成 `close-confirmed + 第 N 根 trend bar 再放行`，但 clean replication 显示：这层 fixed time-bar 延后，并没有带来更诚实的 continuation 识别。
3. **它更像在制造 latency，不像在提供 edge。**
   如果改善主要来自 trade count 下降，而失败率/假突破率没有同步改善，那就不够诚实继续升格。

## 这条 rank 现在更像 hard park 还是 soft park
**结论：soft park，但已经明显偏硬。**

原因：
- 它不是逻辑上完全荒唐；“PSAR 不该看 wick，要看 close-confirmed”这一步本身并不离谱。
- 但原 rank 想表达的那种 **fixed-bar follow-up gate** 已经被 clean replication 否得比较干净：不是参数差一点，而是职责层大概率放错了。
- 所以它还留有一点“主题残余”，但这个残余更像会外流到别的宿主，而不是继续在 `Rank 73` 这条写法里自救。

## 有没有可救信号
**有，但很薄，而且不再支持继续救原 rank。**

可救信号只有一条：
- `PSAR` 作为“别急着把 wick flip 当 continuation”的**确认语义**并没有完全死掉；
- 但最近的新证据更像在说，这个语义应当被改写成：
  - 更上层的 `trend shell / regime / exit protection`（例如 `EMA(RSI)` 分层、Wilder RSI / dual-SuperTrend 这一类趋势壳）；或者
  - 更下层的 `event-confirm / same_dir_first / no_event_timeout` 一类 **event-driven confirm-veto**。

也就是说，残余价值还在，但**宿主已经变了**。

## 最值得改的唯一一刀是什么
**唯一主修改轴：把 `fixed N-bar close-confirmed follow-up` 改写成 `event-driven continuation confirm-veto`。**

人话版：
- 不再问“PSAR flip 后等第 2/3 根 bar 再进会不会更好”；
- 改问“signal 后，市场有没有在延迟预算内走出同向事件流”。

为什么这一刀最诚实：
- 它直接对准 `Rank 73` 原本失败的核心：**fixed time-bar latency 没提供真实增益**；
- 也和后续新证据方向一致：`CUSUM event bar confirm-veto` 更像 continuation 真实性检查，而不是继续迷信固定 `15m close + 再等 N 根`。

## 这刀值得形成新的 derived hypothesis 吗
**不值得；本轮结论维持 `keep_park`。**

原因：
1. 这条唯一主修改轴虽然成立，但它已经**不再是 Rank 73 的窄派生**，而更像一条新的 shared confirm-veto family 语言。
2. 相关残余价值已经被后来的更强宿主吸收：
   - `CUSUM event bar confirm-veto` 已经把“continuation 要不要等真实事件流”写得更直接；
   - `EMA(RSI)` / 趋势壳类新证据又把 PSAR 角色继续推向 regime / exit / loss-protection 层。
3. 如果现在硬写一个 `Rank 73b`，大概率只是把同一主题换个壳再重复一遍，审计上不够诚实。

## trade on / trade off（仅作为 keep_park 审计说明）
- **trade on：** 保留一个很窄的认知更新——PSAR 主题没死，但它更像 event-confirm 或 trend-shell 配角，不像 fixed-bar follow-up 主角。
- **trade off：** 放弃继续把 `close_confirmed_n2 / n3` 写成 queue-facing 派生假设，避免和已有 `CUSUM / trend-shell` 宿主重复占位。

## why now
- `Rank 73` 原始 park 已经过去一段时间，适合低频复盘；
- 最近新增的 `CUSUM event-confirm` 与 `EMA(RSI) hierarchy / trend-shell` 证据，正好让这条 rank 的“残余该往哪流”更清楚了；
- 结论不是推翻旧审计，而是把旧审计钉得更牢：**原 park 保留，且比当时更偏硬。**

## 最终结论
**`Rank 73 = keep_park`**

一句话总结：
> 原 `park` 不变；`Rank 73` 的问题不是“第几根确认 bar 还没调对”，而是 fixed-bar follow-up 这个职责层本身就不够诚实。PSAR 仍有少量 residual value，但它已更自然地外流到 event-confirm / trend-shell 宿主，不值得再单独 draft `Rank 73b`。

## 本轮最小改动
- 新增本轮日志：`research/park_reframe/2026-04-04_1616_rank73-park-reframe.md`
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
