---
name: video-summary
description: 根据视频 URL 或本地媒体的字幕、转写总结内容。优先利用可用字幕，必要时转写音频；不凭标题概述，不自动读取浏览器登录态。
---

# 视频内容总结

总结依据必须是实际取得的字幕或转写；只有元数据时，说明无法据此完成内容总结。

## 环境与权限

使用现有 `yt-dlp`、`ffmpeg` 和可用的转写工具；缺少工具时说明影响，不自动安装。Mac 上已有 `mlx_whisper` 时，默认先用 small 模型；识别不足以支持结论时说明或调整，不把固定模型当作完成标准。

字幕、音频、转写和中间文件写入任务临时目录或用户指定目录，不污染当前代码仓库。

只有已获授权且明确浏览器/配置范围时才使用登录态，不要求用户粘贴密码、cookies 或 token。系统权限弹窗不替代任务授权。没有相应授权时可使用公开字幕或公开音频转写，不为遵守字幕优先而强制尝试凭据读取。

## 内容获取

先检查可用字幕。根据语言、质量和获取成本选择来源；人工字幕、自动字幕、音频转写是可选路径，不是必须逐一执行的流程。弹幕不代替字幕。

以下是 Bash 命令示例。在任务临时目录执行，替换 URL，并按实际字幕语言选择 `--sub-langs`。

```bash
VIDEO_URL="VIDEO_URL"
auth_args=()
# 仅在已授权且确认浏览器配置后设置，例如：
# auth_args=(--cookies-from-browser "chrome:Default")

yt-dlp "${auth_args[@]}" --no-playlist --dump-json "$VIDEO_URL"
yt-dlp "${auth_args[@]}" --no-playlist --list-subs "$VIDEO_URL"
```

下载选中的字幕时沿用同一组认证参数，不只在探测时使用登录态：

```bash
yt-dlp "${auth_args[@]}" --no-playlist \
  --skip-download --write-subs --write-auto-subs \
  --sub-langs "zh.*,en.*" --sub-format "vtt/best" \
  -o "%(id)s.%(ext)s" "$VIDEO_URL"
```

需要音频时选择对应入口：

```bash
yt-dlp "${auth_args[@]}" --no-playlist \
  --extract-audio --audio-format mp3 --audio-quality 5 \
  -o "%(id)s.%(ext)s" "$VIDEO_URL"

# 本地媒体：
ffmpeg -i input.mp4 -vn -acodec mp3 output.mp3
```

已有 `mlx_whisper` 时的转写示例：

```bash
mlx_whisper audio.mp3 \
  --model mlx-community/whisper-small-mlx \
  --task transcribe --output-format txt \
  --output-dir ./transcripts --output-name video_id \
  --verbose False
```

明确语言时可设置相应的 `--language`，不确定时省略。长文本可分段总结，但必须保留影响结论的限定条件。

## 交付

按用户问题总结，提供来源及实际依据，说明自动字幕或转写的重要不确定性。只取得部分内容时标明覆盖范围；获取失败时不补写不存在的内容。

交易/金融视频保留原作者的关键价位、方向、触发条件和风险，区分视频观点与已经核实的事实。取得足以支撑所需总结的内容后即停止额外获取。
