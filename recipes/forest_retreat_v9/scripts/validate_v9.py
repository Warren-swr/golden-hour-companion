"""Decode the full edit and verify the original source frames and seamless join."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw,ImageFont

from edit import OUT,SOURCE,OPENING,NATIVE_TAG,FPS,INTRO_FRAMES,PREROLL_FRAMES,OVERLAP_FRAMES,FINAL_FRAMES,DURATION,SOURCE_FRAMES,PILOT_FRAMES,animation


def sha(path):
    with path.open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],text=True))


def packet_hashes(path):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash,pts_time,duration_time',
        '-of','json',str(path)],text=True))
    return data['packets']


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pilot')
    args=p.parse_args()
    tag=args.pilot or 'final'
    name=f'Golden_Hour_Forest_Retreat_v9_{args.pilot or "2160"}.mp4'
    movie=OUT/name
    expected_frames=PILOT_FRAMES if args.pilot else FINAL_FRAMES
    resolution=720 if args.pilot else 2160
    expected_seconds=expected_frames/FPS
    info=probe(movie)
    assert len(info['streams'])==1 and info['streams'][0]['codec_type']=='video'
    stream=info['streams'][0]
    assert stream['width']==stream['height']==resolution and stream['avg_frame_rate']=='24/1'
    assert abs(float(info['format']['duration'])-expected_seconds)<.001
    original_plan=json.loads((SOURCE/'review/shot_plan.json').read_text())
    cuts={shot['frames'][0]+PREROLL_FRAMES for shot in original_plan[1:]}
    samples=set(range(1,145,6))|set(range(145,expected_frames+1,12))
    samples|={PREROLL_FRAMES,PREROLL_FRAMES+1,INTRO_FRAMES-1,INTRO_FRAMES,INTRO_FRAMES+1,INTRO_FRAMES+2,expected_frames}|cuts|{f-1 for f in cuts}
    folder=OUT/'review'/(tag+'_decoded');folder.mkdir(exist_ok=True)
    proc=subprocess.Popen(['ffmpeg','-hide_banner','-v','error','-i',str(movie),'-vf',
        'scale=320:320:flags=lanczos','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    chunk=320*320*3;previous=None;count=0;metrics=[];selected=[];duplicates=[];last_hash=None
    while True:
        data=bytearray()
        while len(data)<chunk:
            block=proc.stdout.read(chunk-len(data))
            if not block:break
            data.extend(block)
        if not data:break
        assert len(data)==chunk
        count+=1
        pixels=np.frombuffer(data,np.uint8).reshape(320,320,3)
        values=pixels.astype(np.float32)/255
        digest=hashlib.sha256(data).hexdigest()
        if digest==last_hash:duplicates.append(count)
        last_hash=digest
        delta=float(np.abs(values-previous).mean()) if previous is not None else 0
        lum=float((values*np.array([.2126,.7152,.0722],np.float32)).sum(axis=2).mean())
        metrics.append(dict(frame=count,delta=delta,luminance=lum,cut=count in cuts))
        if count in samples:
            path=folder/f'frame_{count:04d}.jpg';Image.fromarray(pixels).save(path,quality=95)
            selected.append((count,path))
        previous=values
    error=proc.stderr.read().decode()
    assert proc.wait()==0 and not error,error
    assert count==expected_frames
    black=[m['frame'] for m in metrics if m['luminance']<.012 and (args.pilot or m['frame']<FINAL_FRAMES-18)]
    jumps=[m for m in metrics if m['delta']>.075 and not m['cut']]
    assert not black and not jumps,(black,jumps)
    assert not [f for f in duplicates if f>PREROLL_FRAMES+1],duplicates
    assert max(metrics[f-1]['delta'] for f in (INTRO_FRAMES,INTRO_FRAMES+1,INTRO_FRAMES+2))<.012
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
    for page,start in enumerate(range(0,len(selected),24),1):
        canvas=Image.new('RGB',(1920,1400),'#211a14');d=ImageDraw.Draw(canvas)
        for i,(frame,path) in enumerate(selected[start:start+24]):
            x,y=i%6*320,i//6*350
            d.text((x+6,y+6),f'{(frame-1)/FPS:.2f} s / {frame:04d}',font=font,fill='#eee4d5')
            with Image.open(path) as image:canvas.paste(image,(x,y+30))
        canvas.save(OUT/'review'/f'{tag}_contact_{page:02d}.jpg',quality=95)
    rendered=json.loads((OUT/'review'/f'{args.pilot or NATIVE_TAG}_render.json').read_text())['frames']
    assert len(rendered)==INTRO_FRAMES
    playback=rendered[PREROLL_FRAMES:]
    assert [row['source_frame'] for row in playback]==list(range(1,OVERLAP_FRAMES+1))
    speeds=[(b['cover_side']-a['cover_side'])*FPS for a,b in zip(rendered,rendered[1:])]
    peak=max(range(len(speeds)),key=speeds.__getitem__)
    motion=dict(embedded_playback_start_seconds=PREROLL_FRAMES/FPS,
        embedded_consecutive_source_frames=OVERLAP_FRAMES,full_frame_handoff_seconds=INTRO_FRAMES/FPS,
        peak_expansion_speed_time=(peak+.5)/FPS,peak_expansion_speed_logical_pixels_per_second=speeds[peak],
        final_expansion_speed_logical_pixels_per_second=speeds[-1],
        scale_curve='logarithmic scale with asymmetric C2 easing; faster acceleration and gradual settling',
        position_curve='independent slightly leading asymmetric C2 easing',
        expected_static_interface_duplicate_frames=[f for f in duplicates if f<=PREROLL_FRAMES+1])
    (OUT/'review'/f'{tag}_opening_motion.json').write_text(json.dumps(motion,indent=2))
    result=dict(movie=name,movie_sha256=sha(movie),resolution=resolution,frames=count,duration=expected_seconds,
        silent=True,decoded_every_frame=True,black_frames=black,unexpected_jumps=jumps,decoded_duplicates=duplicates,
        playback_during_expansion=True,embedded_source_frames=OVERLAP_FRAMES,
        sampled_frames=len(selected),contact_sheets=(len(selected)+23)//24,
        join_frame_metrics=[metrics[f-1] for f in (PREROLL_FRAMES,PREROLL_FRAMES+1,INTRO_FRAMES-1,INTRO_FRAMES,INTRO_FRAMES+1,INTRO_FRAMES+2)],
        maximum_noncut_difference=max(m['delta'] for m in metrics if not m['cut']))
    if not args.pilot:
        native=json.loads((OUT/'review'/f'{NATIVE_TAG}_render.json').read_text())
        assert len(native['frames'])==INTRO_FRAMES and native['resolution']==2160
        for row in native['frames']:
            path=Path(row['file'])
            with path.open('rb') as handle:assert handle.read(25)[24]==16
            with Image.open(path) as im:
                assert im.size==(2160,2160);im.verify()
        assert sha(OUT/'frames'/NATIVE_TAG/f'frame_{INTRO_FRAMES:04d}.png')==sha(OPENING/f'frame_{OVERLAP_FRAMES:04d}.png')
        states=[animation(f) for f in range(INTRO_FRAMES)]
        assert states[-1]['cover_side']==1080 and states[-1]['cover_x']==states[-1]['cover_y']==0
        assert states[-1]['radius']==states[-1]['ui_opacity']==0
        assert all(a['cover_side']<=b['cover_side'] for a,b in zip(states,states[1:]))
        old_master=SOURCE/'Golden_Hour_Forest_Retreat_v7_ProRes_HQ.mov'
        new_master=OUT/'Golden_Hour_Forest_Retreat_v9_ProRes_HQ.mov'
        old_packets=packet_hashes(old_master);new_packets=packet_hashes(new_master)
        assert len(old_packets)==SOURCE_FRAMES and len(new_packets)==FINAL_FRAMES
        assert [p['data_hash'] for p in new_packets[INTRO_FRAMES:]]==[p['data_hash'] for p in old_packets[OVERLAP_FRAMES:]]
        for i,p in enumerate(new_packets):assert abs(float(p['pts_time'])-i/FPS)<.00001
        master_info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
            '-show_streams','-of','json',str(new_master)],text=True))
        assert len(master_info['streams'])==1
        master_stream=master_info['streams'][0]
        assert int(master_stream['nb_read_frames'])==FINAL_FRAMES
        assert master_stream['codec_name']=='prores' and master_stream['profile']=='HQ'
        assert master_stream['pix_fmt']=='yuv422p10le' and master_stream['width']==master_stream['height']==2160
        seam_bytes=subprocess.check_output(['ffmpeg','-v','error','-ss',str((INTRO_FRAMES-1)/FPS),'-i',str(new_master),
            '-frames:v','3','-vf','scale=320:320:flags=lanczos','-pix_fmt','rgb24','-f','rawvideo','-'])
        seam=np.frombuffer(seam_bytes,np.uint8).reshape(3,320,320,3).astype(np.float32)/255
        master_deltas=[float(np.abs(b-a).mean()) for a,b in zip(seam,seam[1:])]
        assert max(master_deltas)<.012,master_deltas
        preview=OUT/'Golden_Hour_Forest_Retreat_v9_1080_preview.mp4'
        preview_info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
            '-show_streams','-show_format','-of','json',str(preview)],text=True))
        ps=preview_info['streams'][0]
        assert len(preview_info['streams'])==1 and ps['width']==ps['height']==1080
        assert int(ps['nb_read_frames'])==FINAL_FRAMES and ps['avg_frame_rate']=='24/1'
        assert abs(float(preview_info['format']['duration'])-DURATION)<.001
        result.update(native_intro_frames_verified=INTRO_FRAMES,body_packets_preserved=SOURCE_FRAMES-OVERLAP_FRAMES,
            source_body_first_frame=OVERLAP_FRAMES+1,source_body_final_frame=SOURCE_FRAMES,final_intro_source_frame=OVERLAP_FRAMES,
            final_intro_png_matches_source=True,master_sha256=sha(new_master),master_stream=master_stream,
            master_decoded_frames=FINAL_FRAMES,master_join_deltas=master_deltas,
            preview_sha256=sha(preview),preview_decoded_frames=FINAL_FRAMES,
            source_master_sha256=sha(old_master))
        (OUT/'review/body_packet_preservation.json').write_text(json.dumps(dict(
            preserved_packets=SOURCE_FRAMES-OVERLAP_FRAMES,source_frame_range=[OVERLAP_FRAMES+1,SOURCE_FRAMES],output_frame_range=[INTRO_FRAMES+1,FINAL_FRAMES],
            source_master_sha256=result['source_master_sha256'],master_sha256=result['master_sha256'],
            method='SHA-256 of every reused compressed ProRes video packet, plus continuous 24 fps timestamps. The decoded source opening frames match the original master display color.'),indent=2))
    (OUT/'review'/f'{tag}_validation.json').write_text(json.dumps(result,indent=2))
    (OUT/'review'/f'{tag}_temporal_metrics.json').write_text(json.dumps(metrics))
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
