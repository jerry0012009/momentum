# 2026-03-17 04:16 UTC · Rank 22 up/down wave + MA20 persistence gate source intake

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：`Paper Seat / EMA` 当前仍是 `waiting_not_due`，因此本轮不得停在 `Run 1` 空转，必须切到 `Run 2 / Scout Fast Lane`。
- 先比较所有 active Scout 候选的当前边际价值：
  - `Rank 17` 与 `Rank 2` 都已经是 `P3 / narrow paper pilot`，当前没有新的 `append/review need`；继续认领大概率只会变成低边际值 wiring。
  - `Rank 7~21` 里能快筛的线基本都已经跑完 `clean replication + Light Stability Pack` 并回到 `park / evidence pool`。
- 因此本轮最诚实的主点不是继续磨旧候选，而是回到 board 明确允许的 **fresh intake**：只开 **1 条** 新的 paper/repo based `5m / 15m crypto` 候选，并把它压到下一轮可直接 `clean replication` 的状态。
- 经过 repo 检查，`src/momentum/signals/up_down_wave.py` 是当前边际价值最高的未进入本轮 Scout 漏斗的简洁结构候选：规则短、因果关系清楚、而且已经有现成模块与信号文档，不需要重新发明框架。

## 开始前检查
- `git status --short` 仍显示大量与本轮无关的历史脏文件 / 未跟踪文件；本轮只做 selective 写入，不混提。
- 最近 runs：
  - `2026-03-17_0334_rank17-narrow-paper-pilot.md`
  - `2026-03-17_0358_rank21-market-risk-onoff-intake.md`
  - `2026-03-17_0412_rank21-clean-replication-park.md`
- 当前 desk 状态：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = fresh intake first`

## 本轮主点 + 紧邻子点
- 主点：把 `up_down_wave.py` 压成当前 desk 可执行的 `Rank 22` source-intake 卡。
- 紧邻子点：把结论同步写回 `docs/TODO.md` 顶部 `Next 3 bot3 runs`，让下一轮可以直接接 `clean replication`，而不是只留在日志里。

## 做了什么
### 1) 完成 fresh intake / clean-room framing
我没有新开大框架，而是直接复用 repo 里现成的：
- `src/momentum/signals/up_down_wave.py`
- `docs/SIGNALS_UP_DOWN_WAVE.md`

把它压成当前 desk 语境下的候选：
- 候选名：`Rank 22 up/down wave + MA20 persistence gate`
- 目标市场：`BTC / ETH / SOL`
- 目标周期：`15m`
- 角色定位：不是单独裸跑，而是作为 **baseline momentum 之后的结构持续性确认门**

### 2) 冻结最小规则（trade on / trade off）
- `trade on`：
  - 先保留现有 `multi-tf momentum` 方向层；
  - 当方向同向时，只在当根形成 `upwave/downwave` 才允许入场；
  - 这里的 `upwave/downwave` 定义固定为：`t-3` 为顺势 K，且最近 4 根收盘连续站上 / 跌破 `MA20`。
- `trade off`：
  - 基线方向缺失；或
  - 对应 `wave` 没有形成。

### 3) 完成最小诚实守门
- 这条线只使用 `t-3..t` 已知数据，默认下一根 bar 执行；
- 现有定义里**没有明显 `lookahead / repaint / data leakage`**；
- 因此它符合进入下一轮 `clean replication` 的最低门槛。

### 4) 新增 deployable artifact
新增：
- `reports/artifacts/literature/scout_rank22_updownwave_source_intake_card.csv`

它把这条 fresh intake 的来源、规则、诚实边界、desk fit、下一步动作写成了可复用卡片，而不是只靠日志描述。

### 5) 作战板同步
更新：
- `docs/TODO.md`

同步内容：
- 当前窗口排班改为：`Rank 22 up/down wave + MA20 persistence gate` 成为当前 fresh intake 主线；
- `Next 3 bot3 runs` 中新增 `2o` 条目，明确它当前只是 `fresh intake accepted / pending Stage A + clean replication`；
- 同时保留：只有当 `Rank 17 / Rank 2` 出现真实 `append/review need` 或 verdict-changing check 时，才回补现有 P3。

## 核心证据 / hard read
### 为什么它值得拿这一轮主资源
1. **边际价值高于继续补 P3 近义 wiring**
   - `Rank 17 / Rank 2` 当前都没有新的真实 append/review need；
   - 再碰它们，大概率只是继续写“看起来像进展”的纸面接线。
2. **规则足够短，适合快筛**
   - `up/down wave` 本质是“连续 4 根站在均线上方/下方 + 一根更早的顺势 K”这种持续性过滤；
   - 非常适合当前 Scout 的 `source intake -> clean replication -> Light Stability Pack` 节奏。
3. **诚实门槛通过**
   - 不是 repaint 型结构线，不依赖未来 pivot；
   - 也不需要追最新 bar 才能开始研究。

### 当前 verdict
- **`Rank 22` 当前只到：`fresh intake accepted / pending Stage A + clean replication`**。
- 这不是 `paper candidate`，更不是 `narrow paper pilot`。
- 当前最诚实的下一步只有一个：
  - 用固定 `BTC/ETH/SOL 120d 15m cache` 跑一次最小 `clean replication`；
  - 再决定它是 `park / paper candidate / narrow paper pilot`。

## 最小验证
已执行并通过：
1. Python 校验 `reports/artifacts/literature/scout_rank22_updownwave_source_intake_card.csv` 已写出；
2. Python 字符串校验 `docs/TODO.md` 已写入：
   - `Rank 22 up/down wave + MA20 persistence gate`
   - `fresh intake accepted / pending Stage A + clean replication`
3. 本轮未重跑重型下载，也未触碰与本轮无关的历史 artifacts。

## 风险 / 边界
1. 这轮只做了 **fresh intake**，没有偷做 clean replication，更没有提前给 alpha verdict。
2. `up/down wave` 过去在日线 / 股票语境里更常见；迁到 `15m crypto` 后可能会因为交易数、持续性或成本而被迅速打回 `park`。
3. 但当前 desk 规则本来就要求：先用便宜而诚实的方式筛掉不行的线，而不是在 spec 阶段无限空想。

## 下一步建议
1. 若下一轮 `Paper Seat` 仍是 `waiting_not_due`，默认继续 `Rank 22` 的最小 `clean replication`。
2. clean replication 时优先复用现有 `BTC/ETH/SOL 120d 15m` cache，不新增重型下载。
3. 若 replication 后交易数极稀疏、成本后立刻归零，按 desk 规则直接 `park`，不要再为它扩写新框架。

## 网页可见落点
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`
- 首页索引将在本轮结尾刷新：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## Git / 提交
- 本轮未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
