# agents

个人 AI agent 配置：一份全局指令和一组 skills，同步到 Codex 与 Claude Code。

只写模型自己不知道的东西：我的偏好、授权边界、工具用法和产物格式。模型已经会做的工程实践不重复。写作规范见 [writing-for-agents](skills/writing-for-agents/SKILL.md)，修改指令或技能前先读它。

## 安装

在仓库根目录运行，先预览再同步：

```bash
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

| 仓库来源 | 安装位置 |
| --- | --- |
| `AGENTS.md` | `~/.codex/AGENTS.md`、`~/.claude/CLAUDE.md` |
| `skills/` | `~/.agents/skills/`、`~/.claude/skills/` |

自定义目录：

```bash
uv run python scripts/install.py --codex-home /path/to/codex --agents-home /path/to/agents --claude-home /path/to/claude
```

安装方式是独立复制，覆盖或删除前备份到目标目录的 `.backups/`。每个目标目录的 `.installed-skills.json` 记录本仓库装过的技能；仓库里删掉的技能，下次同步时只在登记过的目录中移除。目标 `skills/` 是符号链接时，脚本在写入前退出。`tests/` 不参与安装。

## 技能

| 技能 | 调用方式 | 用途 |
| --- | --- | --- |
| `improve-codebase-architecture` | 手动 | 架构体检：扫描热点、出 HTML 报告，再拷问选中的改进项 |
| `project-conventions` | 自动 | 工具链与前端默认值 |
| `writing-for-agents` | 自动 | 编写指令和技能的规范 |
| `ncm-converter` | 自动 | 网易云 `.ncm` 转换 |
| `video-summary` | 自动 | 视频字幕与转写总结 |

“手动”技能只在用户输入 `/name`（Claude Code）或 `$name`（Codex）时加载，同时声明两处：`SKILL.md` frontmatter 中的 `disable-model-invocation: true`，以及 `agents/openai.yaml` 中的 `policy.allow_implicit_invocation: false`。只在用户想要该产物时才用的技能设为手动，省去常驻上下文的 description。

`improve-codebase-architecture`、`writing-for-agents` 译自 [mattpocock/skills](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336)，各技能 frontmatter 的 `metadata.upstream` 记录对应原文件。与上游的差异：

- 上游的 `codebase-design` 只有 `improve-codebase-architecture` 用到，作为它的参考文件放入同一目录；该技能把 deletion test 译作“假想删除”以区别于“删掉旧测试”，补上了 `DEEPENING.md` 的指针，拷问循环不再加载上游的 `grilling` 和 `domain-modeling`，术语表和 ADR 改为项目自己记录决定和词汇的文档，依赖分类补了浏览器环境的例外，报告要求真打开一次验证渲染。
- `HTML-REPORT.md` 删掉了与正文重复的段落。

提交信息格式并入 `AGENTS.md`，不再是单独技能。上游的访谈、spec、拆任务和交接技能（`grilling`、`grill-me`、`grill-with-docs`、`domain-modeling`、`to-spec`、`to-tickets`、`handoff`）曾移植过，一个月没有使用后于 2026-11-08 删除；需要时模型按要求直接产出，或从 git 历史恢复。

## 验证

安装契约测试只依赖 Python 标准库，在临时目录中运行安装脚本：

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

它验证文件安装行为，不验证模型行为。修改指令或技能后，在真实会话里按实际任务检查效果。
