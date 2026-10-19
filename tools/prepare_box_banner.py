from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1])
media=ROOT/'assets/media'
# Original Finer Packaging production film: feed, print, lamination and box work.
starts=[37,44,57,65,76]
filters=[]
for i,start in enumerate(starts):
 filters.append(f'[0:v]trim=start={start}:duration=3.6,setpts=PTS-STARTPTS,fps=24,crop=1280:480:0:64,setsar=1[v{i}]')
filters.append(''.join(f'[v{i}]' for i in range(len(starts)))+'concat=n=5:v=1:a=0[out]')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(source),'-filter_complex',';'.join(filters),'-map','[out]','-an','-c:v','libx264','-preset','medium','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(media/'box-production-banner.mp4')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(media/'box-production-banner.mp4'),'-vf','scale=720:-2,setsar=1','-an','-c:v','libx264','-preset','medium','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(media/'box-production-banner-mobile.mp4')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss','44.5','-i',str(source),'-vf','crop=1280:480:0:64','-frames:v','1','-q:v','2','-y',str(media/'box-production-banner-poster.jpg')],check=True)
print('Created 18-second paper-box production banner, mobile video and poster.')
