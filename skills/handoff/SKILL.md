---
name: handoff
description: 为下一会话或另一 Agent 写一份任务交接文档。
argument-hint: "下一会话要做什么？"
disable-model-invocation: true
metadata:
  upstream: https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/productivity/handoff/SKILL.md
---

# 任务交接

写一份交接文档，让新会话能接着做当前任务。用户传了参数时，把它当作下一会话的重点来取舍内容。

1. 核对当前状态：仓库、分支、提交和未提交修改；已执行、已验证、验证失败和仅有计划的内容分开记录。
2. 按 [交接结构](references/handoff.md) 写。spec、ADR、issue、提交里已有的内容用路径或链接引用。
3. 写明已有的授权和仍需授权的外部动作（推送、部署、真实资金操作等）。
4. 脱敏：密钥、cookies、密码和个人信息只写配置名称。
5. 写到用户指定位置；没有时写到 `.scratch/handoffs/<topic>.md`。跨设备交接时，列出需要一并带走的文件和未推送的提交。
6. 列出下一会话可能用到的技能及用途。

回复文档位置和接手入口。
