---
name: to-tickets
description: 把计划、spec 或当前讨论拆成一组带阻塞依赖的 tracer bullet 任务。
disable-model-invocation: true
metadata:
  upstream: https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/engineering/to-tickets/SKILL.md
---

# 拆分任务

把计划、spec 或当前讨论拆成一组 **tracer bullet** 任务，每个任务声明阻塞它的任务。

1. 读取用户给出的 spec 或 issue 和相关代码。标题和描述使用项目 `CONTEXT.md` 的术语，遵守相关 ADR。如果先做一次预重构能让实现变简单，把它列为第一个任务（make the change easy, then make the easy change）。
2. 起草纵向切片：
   - 每个切片打通一条窄而完整的路径，覆盖它实际涉及的各层（数据、接口、界面、测试），完成后能独立演示或验证。
   - 每个切片能在一个新的上下文窗口内完成。
   - 库修复、迁移和调查以各自的可验证结果作为切片终点。
3. 大范围机械改动（改名、改共享类型）用 **expand–contract**：先让新形式与旧形式并存；再按包或目录分批迁移调用方，每批一个任务，被 expand 阻塞；最后删除旧形式，被所有迁移批次阻塞。某些批次无法单独保持测试通过时，让它们共享整合分支，并加一个最终的整合验证任务。
4. 给每个任务标出阻塞依赖，只列真正阻止开工的任务。
5. 写入项目已有的任务系统；没有时在 `.scratch/<feature-slug>/issues/<NN>-<slug>.md` 每个任务一个文件，按依赖顺序从 01 编号。写入远程 tracker 需要用户明确要求。
6. 回复编号清单（标题、阻塞依赖、交付内容）；用户反馈后只调整受影响的任务。

## 任务模板

```markdown
# <NN>：<任务标题>

**交付内容：** 本任务让什么行为端到端可用，从使用者视角描述。

**阻塞依赖：** 编号和标题，或“无（可立即开始）”。

- [ ] 验收条件 1
- [ ] 验收条件 2
```

描述以行为为主，具体文件路径和代码片段很快会过时。例外：原型产出的、比文字更精确表达决定的片段（状态机、schema、类型），可以截取关键部分放进去并注明来源。
