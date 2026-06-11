# 32B Canary TODO

> 把你的长文档直接粘贴到这里；网页保存后会直接写回服务器。

## 目标
- 为 32b 策略落地一个独立的实盘 canary 研发清单
- 明确不能阻塞或影响 bot2 / bot3 / bot6 / bot7 当前的定时任务

## 约束
- 独立文档
- 独立服务 / 独立调度
- 优先复用现有底层交易执行基础
- 先 canary，再放量

## 你可以从这里开始写
- [ ] 粘贴完整需求
- [ ] 拆分成 canary 交付阶段
- [ ] 标记哪些部分适合 OpenClaw 定时任务，哪些必须靠你我对话推进

你现在的任务不是继续扩展研究报告，而是把当前 alpha 落地成一个“可运行、可观测、可控风险”的实盘执行原型。

# 一、项目目标

当前目标不是正式生产级策略系统，也不是继续做离线回测美化。
当前目标是：

1. 把现有 alpha 信号接入交易执行链路；
2. 以“live canary / 极小实盘验证”为目标完成最小可用执行系统；
3. 优先验证执行正确性、订单状态流、退出逻辑、风控、日志与对账；
4. 让网站可以展示：
   - 当前版本的执行规则
   - 最近信号与订单状态
   - 实盘 / 仿真运行结果摘要
   - 异常与告警摘要
5. 明确区分：
   - 研究报告层（research/report）
   - 执行系统层（execution/live canary）
   本轮重点是 execution，不是 report。

# 二、当前要完成的研发任务（按优先级）

## P0：搭建“可上线的最小执行版本”
必须先完成以下最小闭环：

- 读取现有 alpha 信号
- 生成交易指令
- 下单
- 管理订单状态
- 管理持仓状态
- 执行退出逻辑
- 记录日志
- 风控拦截
- 输出网站可展示的运行状态

不要先做复杂优化，不要先发散研究新因子，不要优先做大量回测扩展。

## P1：实现 canary 版本的固定执行规则
本轮执行版本先固定为一个“笨但稳”的版本，不追求最优，只追求可运行、可验证。

### 交易范围
- 先只支持 BTCUSDT、ETHUSDT
- 暂不启用 SOL
- 暂不做多资产同时放量
- 暂不做加仓、补仓、金字塔

### 入场规则
- 使用现有 alpha 信号作为唯一入场信号
- 采用 maker-first entry
- 限价偏移：2 bps
- TTL：15 分钟
- 若 TTL 到期未成交，则取消订单
- 本轮是否允许 fallback to taker：
  - 先做成可配置
  - 默认先关闭 fallback
  - 配置项保留，后续可切换

### 退出规则
先不要等待 ATR-OCO 完整版，也不要先上 break-even / trailing stop。
本轮退出逻辑固定实现为：

- 止盈：1.0 ATR 的限价止盈
- 超时退出：16 x 15m bars timeout
- 到达 timeout 后强制平仓
- 本轮先不加 break-even
- 本轮先不加 trailing stop
- 本轮先不做复杂 OCO 联动撮合仿真，只需在执行系统里保证“一个主退出路径生效后，其他相关退出挂单被取消”

### 风控规则
- 必须实现 kill switch
- 必须支持“禁止开新仓，仅允许平仓”
- 必须限制单账户最大同时暴露
- 必须限制单资产最多一个活动仓位
- 必须限制重复信号叠单
- 必须限制异常订单悬挂时间
- 必须限制下单失败后的重试次数

# 三、系统模块拆分要求

请按模块开发，不要写成一个混乱脚本。

## 1. Signal Adapter
职责：
- 读取 alpha 信号
- 标准化为统一格式

输出字段建议：
- signal_id
- timestamp
- symbol
- side
- signal_price
- alpha_name
- alpha_version
- metadata

要求：
- 信号输入源可替换
- 保证幂等：同一个 signal_id 不应重复触发多次下单

## 2. Order Intention Layer
职责：
- 把信号转成交易意图，而不是立刻下单
- 统一生成 entry / exit intention

输出字段建议：
- intention_id
- signal_id
- symbol
- side
- order_role (entry / take_profit / timeout_exit / forced_exit)
- order_type (limit / market)
- target_price
- qty
- ttl
- created_at
- status

## 3. Execution Engine
职责：
- 实际与交易所交互
- 下单 / 撤单 / 查单 / 同步订单状态
- 记录 maker-first TTL 生命周期

必须支持：
- place_limit_order
- cancel_order
- query_order
- sync_open_orders
- emergency_flatten_position

要求：
- 对交易所 API 错误做分类
- 所有请求必须有日志
- 所有状态变化必须可追踪
- 不允许 silent failure

## 4. Position Manager
职责：
- 管理当前持仓
- 维护单资产状态机

状态建议：
- flat
- entry_pending
- live_position
- exit_pending
- closed
- blocked

要求：
- 严格限制“一个 symbol 同时最多一个 live position”
- 从订单成交回报更新 position
- 支持部分成交
- 支持异常状态恢复

## 5. Exit Manager
职责：
- 管理止盈与超时退出
- 本轮只实现：
  - ATR 目标止盈
  - timeout 强平
- 先不要实现 break-even
- 先不要实现 trailing stop

要求：
- 进入持仓后立即登记 exit plan
- 到期 timeout 必须触发强平逻辑
- 当止盈成交后，应取消相关其他退出任务
- 当超时强平成交后，应关闭整个 position 生命周期

## 6. Risk Guard
职责：
- 在下单前统一做拦截
- 在运行中支持风控中止

必须拦截的情形：
- kill_switch = true
- trade_enabled = false
- symbol 不在白名单
- 当前已有 live_position
- 当前已有 entry_pending
- 超过单日最大交易次数
- 超过最大同时仓位数
- API 状态异常
- 时钟漂移 / 数据延迟超过阈值
- ATR 不可用 / 行情数据不完整

## 7. Event Bus / Audit Log
职责：
- 所有关键事件必须结构化输出
- 后续网站展示与排障都依赖这个层

事件类型至少包括：
- SignalReceived
- IntentionCreated
- RiskRejected
- OrderPlaced
- OrderAck
- OrderPartiallyFilled
- OrderFilled
- OrderCancelled
- TimeoutTriggered
- PositionOpened
- PositionClosed
- ExecReject
- EmergencyStop
- WarningRaised

要求：
- JSONL 或数据库结构化存储
- 每个事件带 timestamp、symbol、side、event_type、trace_id
- 能够完整重建一笔交易生命周期

# 四、配置项要求

请把关键策略参数全部配置化，不要硬编码。

配置项至少包括：

- enabled_symbols = [BTCUSDT, ETHUSDT]
- trade_enabled = true/false
- kill_switch = true/false
- maker_entry_offset_bps = 2
- entry_ttl_minutes = 15
- take_profit_atr_mult = 1.0
- timeout_bars = 16
- fallback_to_taker = false
- max_concurrent_positions = 1 or 2
- max_position_notional_per_symbol
- max_daily_trades
- log_level
- dry_run / live_mode

要求：
- 支持 YAML / TOML / JSON 之一
- 支持热读取或重启生效
- 配置变更必须进入日志

# 五、本轮暂不开发的内容

以下内容明确列为“暂缓”，不要抢跑：

1. 不要优先开发新的 alpha 因子研究
2. 不要优先开发大规模参数搜索框架
3. 不要优先开发复杂机器学习选股 / 选币层
4. 不要优先开发 full portfolio optimizer
5. 不要优先开发 break-even
6. 不要优先开发 trailing stop
7. 不要优先开发完整 ATR-OCO 回测美化器
8. 不要优先开发 SOL 执行支持
9. 不要先做花哨前端

先把“能安全跑一轮 canary”的最小闭环做出来。

# 六、验收标准

不是看回测收益，而是看执行正确性。

本轮验收标准如下：

## A. 功能验收
- 能接收信号
- 能发 entry 限价单
- 能在 TTL 后撤单
- 能在成交后建立 position
- 能挂出 ATR take profit
- 能在 timeout 后强平
- 能维护仓位状态
- 能执行 kill switch
- 能输出完整审计日志

## B. 稳定性验收
- 无重复下单
- 无漏撤单
- 无订单状态丢失
- 无 position 状态错乱
- 无 silent failure
- API 异常时系统不崩溃
- 重启后可恢复未完成状态

## C. 可观测性验收
- 网站能展示最近信号
- 网站能展示最近订单
- 网站能展示最近持仓
- 网站能展示最近平仓结果
- 网站能展示异常事件
- 网站能展示当前配置版本

# 七、网站展示要求

本轮网站不是做营销页，而是做“运行看板”。

请为网站准备数据输出接口或静态数据文件，至少支持以下区块：

## 1. Strategy Status
- alpha_name
- version
- mode (dry_run / live_canary)
- enabled_symbols
- current_config_hash
- last_signal_time
- system_health

## 2. Recent Signals
- time
- symbol
- side
- signal_price
- signal_id
- accepted / rejected
- reject_reason

## 3. Recent Orders
- time
- symbol
- side
- order_role
- order_type
- price
- qty
- status
- exchange_order_id

## 4. Recent Positions
- symbol
- side
- entry_time
- entry_price
- current_state
- exit_plan
- unrealized_pnl
- realized_pnl

## 5. Recent Closed Trades
- symbol
- side
- entry_price
- exit_price
- holding_time
- exit_reason
- gross_pnl
- fee
- net_pnl

## 6. Warnings / Alerts
- time
- level
- event_type
- message

网站展示优先真实运行信息，不优先展示复杂研究图表。

# 八、开发顺序

请严格按以下顺序推进：

Step 1:
先完成本地可跑的模块骨架：
- Signal Adapter
- Risk Guard
- Order Intention Layer
- Event Bus / Log

Step 2:
接入交易所 API 的最小订单闭环：
- place limit
- cancel
- query
- sync

Step 3:
完成 Position Manager 与 Exit Manager
- 成交后建仓
- ATR 止盈
- timeout 平仓

Step 4:
完成 kill switch / 风控拦截 / 异常恢复

Step 5:
输出网站展示数据接口或 JSON 文件

Step 6:
做一次 end-to-end 演练
- 信号 → 下单 → 成交 → 挂退出 → 平仓 → 记账 → 展示

# 九、交付物要求

每完成一个阶段，都必须交付以下内容：

1. 代码
2. 配置示例
3. 运行说明
4. 状态机说明
5. 已知限制
6. 演示数据
7. 网站展示所需的数据样例

禁止只交付“研究结论”或“回测截图”。
必须交付可运行执行代码。

# 十、你当前的成功标准

你的成功标准不是“把报告做得更好看”，而是：

- 把这个 alpha 从研究对象变成可控执行对象；
- 让团队可以尽快在极小实盘中发现执行问题；
- 让网站可以持续显示运行状态与结果；
- 为下一阶段补 break-even / trailing stop / 更严格 friction 仿真打基础。

如果在开发过程中遇到“研究优化”和“执行落地”之间的冲突，优先选择执行落地。
本轮以 canary live infrastructure 为最高优先级。
