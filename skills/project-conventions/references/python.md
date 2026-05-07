# Python

- 新建 Python 项目默认使用 `uv` 管理项目、依赖和运行环境。
- 初始化项目用 `uv init`。
- 添加运行依赖用 `uv add <package>`。
- 添加开发依赖用 `uv add --dev <package>`。
- 运行脚本、测试或工具命令时优先使用 `uv run ...`。
- 已有项目先遵循现有工具链；不要主动迁移，除非用户明确要求。
