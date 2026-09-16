# agents

个人 AI agents 配置、skills 和同步脚本。提供项目知识、个人取舍与明确的任务要求，不重新规定一整套软件工程方法。

前期需要深入讨论时，用 Grill Me 充分消除模糊，再将结论落到文档。进入开发后，围绕已确认的当前交付目标迭代；具体阶段边界见 [AGENTS.md](AGENTS.md)。简单明确的任务无需强制经过访谈和文档流程。

## 安装

从包含 `AGENTS.md`、`scripts/install.py` 和全部待同步 `skills/` 的仓库根目录运行。不要求带 `.git/` 才能安装；但不能只复制安装脚本或部分技能，因为脚本把源 `skills/` 当作本仓库的完整安装集合，可能清理其余已登记技能。

先预览，再执行同步：

```bash
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

默认将 `AGENTS.md` 复制到 `~/.codex/AGENTS.md`，将 `skills/` 复制到 `~/.agents/skills/`。采用独立目录复制，不使用指向仓库的软链接；目标 `<agents-home>/skills` 如果是符号链接，脚本会退出，须先核对并迁移其中内容。

自定义目录：

```bash
uv run python scripts/install.py --codex-home /path/to/codex --agents-home /path/to/agents
```

覆盖或移除前，备份到目标目录的 `.backups/`。过期技能清理仅依据各目标目录的 `.installed-skills.json`；安装脚本不会按名称猜测未登记技能的来源。`skills/` 内的参考文件随对应技能一起复制；`docs/`、`evals/` 和 `tests/` 不参与安装。

### 技能替换与清理

本 PR 将 `design-before-coding` 替换为 `software-design`，将 `domain-modeling` 的领域知识维护与项目指令模板合并到 `project-context`，不提供两个旧名入口，也不另建 `project-instructions` skill。

若目标目录的 manifest 已登记旧名，同步会备份并删除旧技能、安装新技能。若 manifest 缺失或未登记旧名，旧目录会保留；安装新技能不代表旧技能已经禁用。先核对旧副本的路径、来源和本地修改，再通过对应安装方式清理，不要按同名批量删除。其他项目目录或第三方安装位置也不在本脚本的清理范围。

## 使用与调用策略

普通任务说明目标、上下文、约束和验收即可，已有信息可引用。需要充分访谈时选择 `grill-me`，同时记录领域术语和决定时选择 `grill-with-docs`；需要任务清单时选择 `to-tickets`；多步交付使用 `deliver`。这些不是每次必经的顺序流程。

`software-design` 交付推荐方案、取舍依据和必要边界；`design-review` 交付有证据的问题与检查结论。按主要产物选择，两者可独立使用，不默认互相触发。同时要求审查与修订时，在原授权内完成，不新增确认步骤。

`project-context` 维护已核实的项目事实和已确认决定，按用途更新项目指令、领域文档或 ADR；`project-conventions` 仍只提供工具链默认值。它可由用户调用，也可用于已授权任务的相关同步，不因发现文档不完整就自动扩展维护范围。`grill-with-docs` 用它记录术语和决定，不自动改写项目指令。

例如：

> 使用 $project-context，核对并更新本项目过期的运行说明和已确认术语，沿用现有文档，不改变业务规则。

> 使用 $deliver，完成文档中已确认的当前交付目标，提供使用入口和验证结果，不部署。

Codex 显式调用入口共有四个：`grill-me`、`grill-with-docs`、`implement`、`to-tickets`，各自的 `agents/openai.yaml` 设置了 `allow_implicit_invocation: false`。本 PR 为两个 grill 入口新增这份 YAML；`implement` 和 `to-tickets` 的配置在基线已存在。调用策略限制自动选择，不是权限隔离。

两个 grill 入口保留 `disable-model-invocation: true` frontmatter，供 Claude Code 等识别该字段的宿主使用；Codex 使用上述 YAML。两处声明面向不同宿主，并非同一解析器的重复配置，后续更改显式调用意图时应一起核对。当前安装脚本不配置 Claude Code 的安装目录。

## 验证与维护

安装契约测试仅依赖 Python 标准库，在临时目录运行安装脚本，不修改本机 agent 配置：

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

这些测试验证 manifest 清理范围、预览无写入、符号链接拒绝及上下文技能资源的安装，不验证模型行为。

本库的非运行资料也有明确消费者：

- [Prompt 系统设计](docs/prompt-design.md)：维护本库的人或 Agent 在调整规则时读取背景与边界，不是全局运行指令。
- [行为回归规格](evals/prompt-behavior.md)：受委托进行评估的人或 Agent 选取案例、运行新旧配置并记录证据；目前没有自动 runner，也没有已通过的模型行为结果。
- [项目上下文技能](skills/project-context/SKILL.md)：需要维护目标项目知识时使用，其 `references/` 提供项目指令、领域上下文和决定记录的可裁剪结构。

不再保留独立的任务写法教程或无人消费的项目模板。维护本库时按相关设计说明和回归规格处理；普通业务开发不额外加载它们。
