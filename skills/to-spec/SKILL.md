---
name: to-spec
description: 把当前讨论整理成本次工作的规格（spec）。
disable-model-invocation: true
metadata:
  upstream: https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/engineering/to-spec/SKILL.md
---

# 整理规格

把当前对话和对代码库的理解合成为一份 spec。这是整理而不是访谈：只用已经讨论过和查明的内容。

1. 读相关代码和已有文档，确认现状。全文使用项目 `CONTEXT.md` 的术语，遵守相关 ADR。
2. 把内容分成四类：已确认的决定、本期范围、后续事项、未决问题。只有已确认的内容写成要求；未决问题写明它影响什么。
3. 按项目已有格式写；没有时用 [规格结构](references/spec.md)。篇幅与任务规模相称。
4. 写到用户指定位置或项目已有的规格目录；都没有时写到 `.scratch/<topic>/spec.md`。发布到 issue tracker 需要用户明确要求。
5. 回复 spec 位置、本期范围和关键未决问题。整理完即结束；之后是否开发听用户安排。
