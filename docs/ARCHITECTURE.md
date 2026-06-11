# Architecture

## 一、分层
- `domain/`：统一领域对象定义（Bar, Signal, Order, Position）
- `data/`：数据接入与标准化（不同市场同一输出 schema）
- `factors/`：因子计算（纯函数，便于测试）
- `signals/`：因子组合与交易信号生成
- `risk/`：仓位、止损、风控规则
- `engines/`：回测引擎适配（当前 Backtrader）
- `execution/`：模拟盘/实盘执行（后续）
- `analytics/`：绩效与归因分析

## 二、执行路径（M1）
`raw data -> standardized bars -> factors -> signals -> backtrader strategy -> trades -> analytics`

## 三、扩展策略
- 从单市场扩展到多市场时，优先扩展 `data/` 适配层。
- 从回测扩展到模拟盘/实盘时，复用 `factors/signals/risk`，只替换 `execution/`。
- 新策略通过新增 `config/strategies/*.yaml` + `signals/` 模块完成。

## 四、当前落地状态（M1）
- 已完成：项目分层、配置分层、数据契约、样例数据（`1810.HK`）
- 进行中：Backtrader 引擎接入与第一版策略实现
- 未开始：paper/live execution 层
