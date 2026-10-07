# 复现与依赖

## 编辑和渲染最新场景

下载 Release 中的 `Golden_Hour_Forest_Retreat_v7_scene.zip`，解压到 `work/scene/`。工程中的 12 张纹理已经嵌入；`cache/pool_gravity_capillary.mdd` 必须留在 `.blend` 的相对路径下。

场景使用 Blender 4.5.12 LTS 制作。时间轴为 1–1344 帧、24 fps，九个相机切点已写入工程。`tools/render_scene.py` 支持 CPU、CUDA 或 OptiX，输出 RGB 16-bit PNG；它不覆盖输入工程或已存在的目标帧。

```bash
blender --background work/scene/Golden_Hour_Forest_Retreat.blend \
  --disable-autoexec --python-exit-code 1 --python tools/render_scene.py -- \
  --output work/final-frames --start 1 --end 1344 \
  --resolution 2160 --samples 192 --device OPTIX

python3 tools/encode_video.py --input 'work/final-frames/frame_%04d.png' \
  --frames 1344 --output work/final-video
```

编码从 PNG 直接生成 2160 MP4 与 1080 预览，保持 BT.709 色彩标记。两种输出均完成解码计数、尺寸、帧率、时长和无音轨检查。选择新的输出目录或名称可以避免覆盖已有影片。

## 播放器片头

`recipes/forest_retreat_v10/scripts/edit.py` 保存三秒停留、2.5 秒非线性展开和同步播放的时序；`render_intro.py` 包含排版、图标、字体和 RGB16 合成。正式 v10 由 132 张片头合成帧与原片第 61–1344 帧组成，共 1416 帧、59 秒。

研究或适配该片头时，需要准备原片前 60 帧的 2160 方形 RGB16 图像，以及 SF Pro Display Regular、Semibold 和 SF Pro Text Regular。字体从 [Apple 官方资源](https://developer.apple.com/fonts/) 获取并按其许可使用。原始字体及下载包不在仓库或 Release 中。

历史 `produce.py` 依赖当次的冻结输入和前置素材，不能在空克隆目录中直接得到原制作结果。它们保留了迭代证据；新的制作流程应沿用项目的 MP4 默认输出约定。

## 脚本依赖

`tools/encode_video.py` 仅需要 Python 标准库与 FFmpeg；场景渲染脚本由 Blender 自带 Python 执行。部分历史分析和合成脚本还使用 NumPy、Pillow 与 OpenCV，可在单独的虚拟环境中安装根目录的 `requirements.txt`。

完整重渲染的耗时和存储量取决于硬件、采样数和输出帧数。先用一小段 720 预览检查环境，再进行完整渲染。
