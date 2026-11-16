from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent.parent
vf="drawbox=x=0:y=0:w=iw:h=44:color=0x04070b:t=fill,drawbox=x=0:y=ih-44:w=iw:h=44:color=0x04070b:t=fill,subtitles=production/titles.ass,fade=t=in:st=0:d=1.5,fade=t=out:st=117:d=3"
cmd=['ffmpeg','-hide_banner','-y','-framerate','24','-start_number','1','-i','frames/frame_%04d.jpg','-i','output/The_Last_Signal_Original_Score.wav','-vf',vf,'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','44100','-t','120','-movflags','+faststart','-metadata','title=The Last Signal','-metadata','comment=An original Blender animated short with an original synthesized score.','output/The_Last_Signal.mp4']
subprocess.run(cmd,cwd=root,check=True)
