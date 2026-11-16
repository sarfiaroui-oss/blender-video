import subprocess
from pathlib import Path
R=Path(__file__).resolve().parent.parent
vf='tpad=stop_mode=clone:stop_duration=0.2,framerate=fps=24:interp_start=15:interp_end=240:scene=2,drawbox=x=0:y=0:w=iw:h=32:color=0x151514:t=fill,drawbox=x=0:y=ih-32:w=iw:h=32:color=0x151514:t=fill,subtitles=production/titles.ass,fade=t=in:st=0:d=1,fade=t=out:st=117.5:d=2.5'
cmd=['ffmpeg','-hide_banner','-y','-framerate','12','-start_number','1','-i','frames/frame_%04d.jpg','-i','output/Taj_Mahal_ONNX_Dialogue.wav','-vf',vf,'-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','120','-movflags','+faststart','-metadata','title=Taj Mahal — A Sunset Conversation','-metadata','comment=User-supplied characters and monument, animated in Blender; original environment background; Piper ONNX dialogue.','output/Taj_Mahal_Sunset_Conversation.mp4']
subprocess.run(cmd,cwd=R,check=True)
