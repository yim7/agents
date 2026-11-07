---
name: project-conventions
description: 个人项目的默认工具链和前端技术栈。新建或初始化项目、选择工具链、添加依赖、新建 Web 前端项目时使用。
---

# 项目约定

已有项目沿用现有工具链和技术栈。以下是新建项目时的默认值。

## Python

用 `uv` 管理项目、依赖和运行环境：`uv init` 初始化，`uv add <package>` 加运行依赖，`uv add --dev <package>` 加开发依赖，`uv run ...` 运行脚本、测试和工具。

## Web 前端

- `React` + `TypeScript` + `Vite`，UI 用 `shadcn/ui` + `Tailwind CSS`。
- 持续读取、刷新或修改服务端数据时用 `TanStack Query`；简单请求不引入。
