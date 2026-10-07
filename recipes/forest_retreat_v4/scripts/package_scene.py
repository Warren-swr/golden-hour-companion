"""A portable editable scene bundle with its real animated-water dependency."""
import hashlib
import json
import zipfile
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle,'sha256').hexdigest()


def main():
    scene=OUT/'Golden_Hour_Forest_Retreat.blend'
    cache=OUT/'cache/pool_gravity_capillary.mdd'
    gate=json.loads((OUT/'review/production_gate.json').read_text())
    assert digest(scene)==gate['scene_sha256']
    records=[dict(file=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=digest(p)) for p in (scene,cache)]
    destination=OUT/'Golden_Hour_Forest_Retreat_v4_scene.zip'
    readme='''Golden Hour Companion — A Forest Retreat v4

可编辑场景包 / Editable scene bundle

使用 Blender 4.5.12 LTS 打开 Golden_Hour_Forest_Retreat.blend。
请保留同级 cache 文件夹，里面是泳池水面的动画缓存；所有图像贴图均已嵌入工程。
场景包含 9 个镜头，时间轴为 1–1008 帧、24 fps，共 42 秒。
可以直接编辑几何、材质、灯光和镜头。没有可用 GPU 时，将 Cycles 的 Device 改为 CPU。
成片视频和完整建模、渲染脚本单独交付，本包只包含可编辑场景及其播放所需资源。
扫描材质来源见 ASSET_SOURCES.json。新增几何和动画由项目脚本创建。

Keep the cache folder beside the .blend file. Image textures are packed into the project.
The film and construction/render scripts are delivered separately.
'''
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as archive:
        for path in (scene,cache):
            archive.write(path,str(path.relative_to(OUT)))
        archive.writestr('README.txt',readme)
        archive.writestr('ASSET_SOURCES.json',(OUT/'assets/sources.json').read_bytes())
        archive.writestr('SCENE_MANIFEST.json',json.dumps(dict(files=records),indent=2))
    report=dict(bundle=destination.name,bytes=destination.stat().st_size,sha256=digest(destination),files=records)
    (OUT/'review/scene_bundle.json').write_text(json.dumps(report,indent=2))
    print('SCENE_BUNDLE_COMPLETE',json.dumps(report),flush=True)


if __name__=='__main__':
    main()
