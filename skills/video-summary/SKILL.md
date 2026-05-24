---
name: video-summary
description: 从视频 URL 或本地视频提取字幕/转写并总结内容。用于 YouTube、哔哩哔哩、Twitter/X、网页视频或本地媒体文件；优先字幕，无字幕则下载音频并用 mlx-whisper small 转写。
---

# 视频内容总结

把视频 URL 或本地视频文件变成可读总结。总结必须基于字幕或转写文本，不要只看标题猜内容。

## 边界

- 依赖工具：`yt-dlp`、`ffmpeg`、`mlx_whisper`。
- 缺少工具时说明影响，不要自动安装依赖。
- 需要登录、会员、地区权限或 cookies 时说明限制；不要要求或保存 cookies、token、会话文件。
- 字幕、音频、转写文本和中间 JSON 都是临时产物，放在任务临时目录或用户指定目录，不要写入当前代码仓库。

## 流程

先确认元数据和字幕：

```bash
yt-dlp --dump-json --no-playlist "VIDEO_URL"
yt-dlp --list-subs "VIDEO_URL"
```

有字幕时优先下载人工字幕，其次自动字幕；无字幕时下载音频。本地视频可直接用 `ffmpeg` 抽音频：

```bash
yt-dlp \
  --skip-download \
  --write-subs \
  --write-auto-subs \
  --sub-langs "zh.*,en.*" \
  --sub-format "vtt/best" \
  -o "%(id)s.%(ext)s" \
  "VIDEO_URL"

yt-dlp \
  --no-playlist \
  --extract-audio \
  --audio-format mp3 \
  --audio-quality 5 \
  -o "%(id)s.%(ext)s" \
  "VIDEO_URL"

ffmpeg -i input.mp4 -vn -acodec mp3 output.mp3
```

在 Mac 上优先用 `mlx-whisper` small 转写：

```bash
mlx_whisper audio.mp3 \
  --model mlx-community/whisper-small-mlx \
  --language zh \
  --task transcribe \
  --output-format txt \
  --output-dir ./transcripts \
  --output-name video_id \
  --verbose False
```

按视频内容调整 `--language zh/en`；不确定语言时省略该参数。文本很长时先按主题或时间顺序压缩分段摘要，再做最终总结。

## 输出

总结必须说明依据：人工字幕、自动字幕或音频转写。自动字幕或转写要提示可能有识别误差；字幕和转写都失败时，明确说明依据不足。

默认输出标题、来源链接、发布时间或时长、核心内容。交易/金融视频额外提取关键价位、方向判断、触发条件和风险。
