# 历史制作源码

这里保留基础场景及 v2–v10 的 204 份 Python 脚本，覆盖建模、材质、森林、水面缓存、运镜、视频合成和核验。每个版本继续使用原来的 `scripts/` 相对布局。

| 版本 | 主要内容 |
| --- | --- |
| [base](base/scripts/) | 原始住宅、抱枕、材质、森林和镜头生成 |
| [v2](forest_retreat_v2/scripts/) | 森林住宅、完整室内、庭院与物理水面 |
| [v3](forest_retreat_v3/scripts/) | 细节和镜头迭代 |
| [v4](forest_retreat_v4/scripts/) | 场景与素材修整 |
| [v5](forest_retreat_v5/scripts/) | 模型、表面与植被精修 |
| [v6](forest_retreat_v6/scripts/) | 空间连接与电影运镜 |
| [v7](forest_retreat_v7/scripts/) | 加快运镜、三段长镜头、56 秒场景 |
| [v8](forest_retreat_v8/scripts/) | 播放器与封面展开片头 |
| [v9](forest_retreat_v9/scripts/) | 简化播放器和同步展开 |
| [v10](forest_retreat_v10/scripts/) | Apple Music 风格、SF Pro 字体、三秒停留 |

这些是制作过程快照。旧控制脚本可能要求前一版 `.blend`、渲染帧、字体、冻结记录或 ProRes 输入，也可能生成历史母版；公共默认入口为仓库根的 `tools/`，只输出 MP4。

发布时仅把早期脚本中的个人 FFmpeg 路径回退改为从 PATH 调用；其余源码保持原样。原始与公开副本的哈希及差异说明见 [源码索引](../docs/source-index.json)。大型中间场景没有作为 Git 文件分发，最新可编辑场景由 Releases 提供。
