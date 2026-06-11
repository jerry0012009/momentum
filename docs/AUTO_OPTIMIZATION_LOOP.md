# AUTO_OPTIMIZATION_LOOP

> 兼容壳。当前不再作为独立规则源。
> authoritative source：
> 1. `docs/BOT2_BOT3_POLICY.md`
> 2. `docs/BOT2_BOT3_STATE.md`
> live payload 模板：`docs/AUTO_OPTIMIZATION_CRON_PROMPT.txt`

bot3 每轮只执行 `cycle_plan` 里的一个小点，并用一句 `result` 写回这一步让对象发生了什么变化。
