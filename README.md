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

先预览安装动作：

```bash
uv run python scripts/install.py --dry-run
```

确认后执行安装：

```bash
uv run python scripts/install.py
```

默认安装到：

```text
~/.codex/AGENTS.md
~/.agents/skills/
```

如果要安装到其他目录：

```bash
uv run python scripts/install.py --codex-home ~/.codex --agents-home ~/.agents
```

## 同步到新电脑

```bash
git clone git@github.com:<your-name>/agents.git
cd agents
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

## 注意事项

- 提交前检查不要包含密钥、token、缓存和本地会话。
- `skills/` 只放自己维护的 skill。
- 如果目标位置已有同名文件或 skill，安装脚本会在覆盖前备份到目标目录的 `.backups/`。
- Codex 全局指令安装到 `~/.codex/AGENTS.md`；用户级 skills 安装到 `~/.agents/skills/`。
