"""Preserve every original cache sample, then continue the same analytic waves."""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np

from film import FRAMES,FPS
from water_simulation import topology,basin_solver,NX,NY,LEVEL

OUT=Path(__file__).resolve().parent.parent


def sha256(path):
    with path.open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()


def main():
    source=OUT/'source/v6_water.mdd'
    destination=OUT/'cache/pool_gravity_capillary.mdd'
    assert not destination.exists(),'Preserve cache generations; do not overwrite a rendered input.'
    assert sha256(source)=='5ce6bd8df1c3950cbbca3c48af8570c0d5973eafbf517b0407b962051704eaf8'
    vertices,_=topology();surface,_=basin_solver()
    with source.open('rb') as old:
        old_frames,count=struct.unpack('>2i',old.read(8))
        assert count==len(vertices) and FRAMES>=old_frames
        times=old.read(old_frames*4)
        block=count*12
        old.seek(8+old_frames*4+(old_frames-2)*block)
        penultimate=np.frombuffer(old.read(block),dtype='>f4').reshape(-1,3).copy()
        last=np.frombuffer(old.read(block),dtype='>f4').reshape(-1,3).copy()
        vertices[:NX*NY,2]=LEVEL+surface((old_frames-1)/FPS+12).ravel()
        error=float(np.max(np.abs(vertices.astype(np.float32)-last)))
        assert error<2e-6,'The solver must reproduce the inherited cache before extending it.'
        old.seek(8+old_frames*4)
        prefix=hashlib.sha256()
        with destination.open('xb') as new:
            new.write(struct.pack('>2i',FRAMES,count));new.write(times)
            new.write((np.arange(old_frames,FRAMES,dtype='>f4')*(1/FPS)).astype('>f4').tobytes())
            while data:=old.read(8*1024*1024):
                prefix.update(data);new.write(data)
            boundary=[]
            previous=last
            for frame in range(old_frames,FRAMES):
                vertices[:NX*NY,2]=LEVEL+surface(frame/FPS+12).ravel()
                current=vertices.astype('>f4')
                new.write(current.tobytes())
                if frame<old_frames+3:
                    boundary.append(float(np.max(np.abs(current-previous))))
                previous=current.copy()
    with destination.open('rb') as handle:
        handle.seek(8+FRAMES*4)
        copied=hashlib.sha256()
        remaining=old_frames*block
        while remaining:
            data=handle.read(min(8*1024*1024,remaining));assert data
            copied.update(data);remaining-=len(data)
    assert copied.hexdigest()==prefix.hexdigest()
    preceding=float(np.max(np.abs(last-penultimate)))
    assert max(boundary)<max(.015,preceding*2),'Unexpected discontinuity at the extension boundary.'
    report=dict(model='Continuation of the inherited finite-depth gravity-capillary eigenmodes',
        source='source/v6_water.mdd',source_sha256=sha256(source),
        cache=str(destination.relative_to(OUT)),sha256=sha256(destination),bytes=destination.stat().st_size,
        fps=FPS,frames=FRAMES,vertices=count,preserved_prefix_frames=old_frames,
        source_coordinate_prefix_sha256=prefix.hexdigest(),copied_coordinate_prefix_sha256=copied.hexdigest(),
        analytic_last_source_error_m=error,preceding_step_max_m=preceding,extension_step_max_m=boundary,
        limitation='Small-amplitude surface waves; the existing spillway remains a separate thin-sheet approximation.')
    (OUT/'review/water_extension.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
