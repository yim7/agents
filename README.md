# agents

个人 AI agents 配置、skills 和同步脚本。

这个仓库只保存自己手写、可同步的内容，不保存 token、缓存、会话记录或机器相关的临时状态。

## 目录结构

```text
agents/
  AGENTS.md
  skills/
  scripts/
    install.py
  README.md
  .gitignore
```

## 使用方式

先预览同步动作：

```bash
uv run python scripts/install.py --dry-run
```

确认后执行：

```bash
uv run python scripts/install.py
```

默认同步到：

```text
~/.codex/AGENTS.md
~/.claude/CLAUDE.md
~/.agents/skills/
~/.claude/skills/
```

如果要安装到其他目录：

```bash
uv run python scripts/install.py --claude-home ~/.claude
```

## 同步到新电脑

```bash
git clone git@github.com:<your-name>/agents.git
cd agents
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

## 同步行为

脚本会保持目标目录和仓库一致：

- 仓库中新增的 skill → 安装到目标目录
- 仓库中已有的 skill → 内容有变化时更新
- 仓库中删除的 skill → 从目标目录移除（仅限本仓库安装过的）

每个目标目录维护一个 `.installed-skills.json` manifest，记录本仓库安装过的内容。用户自己添加的 skill 不会被触碰。

## 注意事项

- 提交前检查不要包含密钥、token、缓存和本地会话。
- `skills/` 只放自己维护的 skill。
- 覆盖或移除前会备份到目标目录的 `.backups/`。
