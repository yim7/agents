---
name: handoff
description: 把当前对话压缩成一份交接文档，供另一个 agent 接手。
argument-hint: "下一会话要做什么？"
disable-model-invocation: true
metadata:
  upstream: https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/productivity/handoff/SKILL.md
---

写一份交接文档，总结当前对话，让一个全新的 agent 能继续这项工作。保存到用户操作系统的临时目录，而不是当前工作区。

在文档中加入“建议技能”一节，写明下一个 agent 应该调用 Skill 工具加载哪些技能。

不要重复其他产物中已经记录的内容（spec、计划、ADR、issue、提交、diff）。改为用路径或 URL 引用它们。

删除任何敏感信息，例如 API 密钥、密码或个人身份信息。

如果用户传入了参数，把它当作下一会话关注重点的描述，并据此调整文档。
