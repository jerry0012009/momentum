# Roadmap

> 说明（2026-03-24）：本页属于较早期的工程路线图，`M1~M5` 仍保留作长期工程层参考；但**当前真正 authoritative 的短期调度依据**已经是 `docs/BOT2_BOT3_POLICY.md` + `docs/BOT2_BOT3_STATE.md`。
>
> 当前短期优先级不再按本页直接排：
> - bot2 / bot3 先看 `docs/BOT2_BOT3_POLICY.md` + `docs/BOT2_BOT3_STATE.md`
> - `docs/TODO.md` 只作项目层摘要与导航
> - 本页只作长期工程参考，不应再被误读成“当前正在主推的唯一 roadmap”
>
> `tiny-live / live-shadow` 当前不属于主目标，视为已冻结的旧 deployment 话题。

## M1：单市场 Backtrader 回测（当前）
- [x] 定义数据 schema 与目录规范（`docs/DATA_CONTRACT.md`）
- [x] 定义策略配置 schema（`config/strategies/trend_momentum_v1.yaml`）
- [x] 建立 M1 依赖与环境基线（`requirements-m1.txt` + `.venv`）
- [x] 准备单标的示例数据（小米港股 `1810.HK`，1d，1y/5y）
- [x] 落地第一版筹码分布特征工程脚本（`build_chip_distribution.py`）
- [x] 落地第一版上涨浪/下跌浪信号（MA20 + 4日持久性）
- [ ] 落地第一版趋势策略（`trend_momentum_v1`）
- [x] 完成 Up/Down Wave 5日事件回测（小米单标的粗测）
- [x] 完成信号流水线文档化（生成 -> 回测 -> 维护约定）
- [x] 完成 Up/Down Wave 网页化评估报告（可复用模板 + 图表）
- [ ] 生成标准回测报告（收益、回撤、交易次数、夏普）

## M2：研究效率提升
- [ ] 参数扫描/网格搜索
- [ ] Walk-forward
- [ ] 回测回归测试（防止改动导致结果漂移）

## M3：模拟盘
- [ ] paper broker
- [ ] 订单状态机
- [ ] 风控熔断

## M4：实盘
- [ ] 交易所适配器（先 crypto）
- [ ] 下单重试与幂等
- [ ] 监控与告警

## M5：多市场
- [ ] A 股（交易时段、停牌、复权）
- [ ] 美股（拆分、分红、时区）
- [ ] 黄金（数据源适配）
