---
name: video-summary
description: 根据字幕或转写总结视频内容。用户给出视频 URL 或本地媒体并要求总结、提炼要点时使用。
---

# 视频内容总结

总结依据必须是实际取得的字幕或转写；只有标题和元数据时，说明无法据此总结。弹幕不代替字幕。

## 环境与权限

- 用现有的 `yt-dlp`、`ffmpeg` 和转写工具；缺少时说明影响，不自动安装。
- 字幕、音频、转写等中间文件写到任务临时目录或用户指定目录。
- 登录态只在已获授权且明确了浏览器和配置范围时使用，不要求用户粘贴密码、cookies 或 token；系统权限弹窗不等于任务授权。没有授权时用公开字幕或公开音频转写。

## 内容获取

先用 `yt-dlp --list-subs` 查看可用字幕，按语言、质量和获取成本在人工字幕、自动字幕、音频转写之间选择，不必逐一执行。认证参数放在一个数组里（例如 `auth_args=(--cookies-from-browser "chrome:Default")`，未授权时为空），探测和下载使用同一组参数。

需要转写时，Mac 上有 `mlx_whisper` 就先用 small 模型；识别不足以支撑结论时说明或换模型：

```bash
mlx_whisper audio.mp3 --model mlx-community/whisper-small-mlx \
  --task transcribe --output-format txt --output-dir ./transcripts --output-name <video_id> --verbose False
```

明确语言时设置 `--language`，不确定时省略。长文本可分段总结，保留影响结论的限定条件。

## 交付

按用户问题总结，附来源和实际依据，标明自动字幕或转写的重要不确定性；只取得部分内容时标明覆盖范围，获取失败时不补写不存在的内容。交易/金融视频保留原作者的关键价位、方向、触发条件和风险，区分视频观点与已核实事实。取得足以支撑总结的内容后即停止。
