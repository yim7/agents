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

安装器只配置上述 Codex 指令位置与共享技能目录，不配置 DSH 的全局指令、preset 或 Claude Code 安装目录。另一宿主是否读取这些指令和技能，应检查其实际配置，不能从安装成功推定。

### 技能替换与清理

2026-09-16 合入的重构（`15f5173`）将 `design-before-coding` 替换为 `software-design`，将 `domain-modeling` 的领域知识维护与项目指令模板合并到 `project-context`。当前不提供两个旧名入口，也不另建 `project-instructions` skill。

若目标目录的 manifest 已登记旧名，同步会备份并删除旧技能、安装新技能。若 manifest 缺失或未登记旧名，旧目录会保留；安装新技能不代表旧技能已经禁用。先核对旧副本的路径、来源和本地修改，再通过对应安装方式清理，不要按同名批量删除。其他项目目录或第三方安装位置也不在本脚本的清理范围。

## 使用与调用策略

普通任务说明目标、上下文、约束和验收即可，已有信息可引用。需要充分访谈时选择 `grill-me`，同时记录领域术语和决定时选择 `grill-with-docs`；需要任务清单时选择 `to-tickets`；多步交付使用 `deliver`。这些不是每次必经的顺序流程。

`software-design` 交付推荐方案、取舍依据和必要边界；`design-review` 交付有证据的问题与检查结论。按主要产物选择，两者可独立使用，不默认互相触发。同时要求审查与修订时，在原授权内完成，不新增确认步骤。

`project-context` 维护已核实的项目事实和已确认决定，按用途更新项目指令、领域文档或 ADR；`project-conventions` 仍只提供工具链默认值。它可由用户调用，也可用于已授权任务的相关同步，不因发现文档不完整就自动扩展维护范围。`grill-with-docs` 用它记录术语和决定，不自动改写项目指令。

`to-spec` 把已有讨论整理为本次规格，不重开访谈；`handoff` 保存下一会话需要的任务状态，不代替长期项目知识。`code-review` 检查具体代码变更的需求符合性、正确性与回归，区别于 `design-review` 的专项结构审查；它按审查请求或已授权评审任务选择，不是所有开发的强制收尾。

例如：

> 使用 $project-context，核对并更新本项目过期的运行说明和已确认术语，沿用现有文档，不改变业务规则。

> 使用 $deliver，完成文档中已确认的当前交付目标，提供使用入口和验证结果，不部署。

六个显式入口为 `grill-me`、`grill-with-docs`、`implement`、`to-tickets`、`to-spec`、`handoff`。它们同时维护两类调用声明：

| 宿主 | 仓内声明 | 用户显式选择 |
| --- | --- | --- |
| Codex | `agents/openai.yaml` 中 `policy.allow_implicit_invocation: false` | `$skill-name` |
| DSH | `SKILL.md` frontmatter 中 `disable-model-invocation: true` | `/skill-name` |
| Claude Code 等识别该字段的宿主 | 同一 frontmatter 声明 | 按宿主提供的显式入口 |

配置依据见 [设计说明](docs/prompt-design.md#配置依据)。当前验证目标为实际使用的 Codex 与 DSH，宿主版本与模型版本分别记录；上游支持某字段不等于本机某版本已经通过集成测试。

调用策略不是权限隔离。DSH 的模型侧加载工具也检查该字段，不只是隐藏目录；用户显式选择一个入口，不会让模型自动获得加载其他显式入口的能力。旧 `implement` 只保留用户显式调用兼容，不保证外部工作流把它当作内部依赖时仍可加载。更新前保存有效配置，从要保留的入口沿有向依赖检查实际加载和产物；不能仅以没有悬空链接认定兼容，也不批量给全部外部技能加此标记。

## 选择性移植

`to-spec`、`handoff`、`code-review` 改编自 Matt Pocock 的 skills，来源固定在 `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`。各技能 frontmatter 记录上游文件；本地取舍见 [设计说明](docs/prompt-design.md#选择性移植)。它们不依赖上游 setup、tracker 配置或其他上游技能，不要求同时安装整包。

三个技能沿用上游名称。同步时，安装器会备份并替换目标目录中的同名副本，即使它未被旧 manifest 登记；先核对来源与本地修改。其他目录、preset 或插件提供的同名版本不会自动清理，安装后仍需核对实际解析来源。上游其他技能的卸载或停用是独立的本机操作，不由本仓库安装器按来源批量处理。

## 验证与维护

安装契约测试仅依赖 Python 标准库，在临时目录运行安装脚本，不修改本机 agent 配置：

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

这些测试验证 manifest 清理范围、预览无写入、符号链接拒绝及技能资源的安装（包括新技能模板和同名副本备份），不验证模型行为。

本库的非运行资料也有明确消费者：

- [Prompt 系统设计](docs/prompt-design.md)：维护本库的人或 Agent 在调整规则时读取背景与边界，不是全局运行指令。
- [行为回归规格](evals/prompt-behavior.md)：评估者运行相关场景，分别检查授权内推进与必要暂停；规格不是自动 runner。
- [移植技能回归](evals/ported-skills.md)：规格、交接和代码审查的成对场景，尚未执行模型行为对照。
- [实验记录约定](evals/records/README.md)：保存有效配置快照、案例结果、证据与决定，包括失败和“未观察到差异”；目前尚无模型行为实验报告。
- [项目上下文技能](skills/project-context/SKILL.md)：需要维护目标项目知识时使用，其 `references/` 提供项目指令、领域上下文和决定记录的可裁剪结构。

不再保留独立的任务写法教程或无人消费的项目模板。维护本库时按相关设计说明和回归规格处理；普通业务开发不额外加载它们。
