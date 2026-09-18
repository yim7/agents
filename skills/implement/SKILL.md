---
name: implement
description: 用户显式选择旧版实现入口时，转入 deliver 完成当前交付；普通开发和其他技能不自动调用本入口。
disable-model-invocation: true
---

读取同级目录中的 [deliver](../deliver/SKILL.md)，按同一任务和已有授权继续执行。实现、验证和评审统一遵循该技能，不再单独运行旧版实现流程。
