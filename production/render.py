import bpy,sys,os,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a=sys.argv[sys.argv.index('--')+1:];start,end=map(int,a[:2]);s=bpy.context.scene
s.cycles.samples=4;s.render.threads_mode='FIXED';s.render.threads=3
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96;s.render.image_settings.color_mode='RGB'
s.render.use_sequencer=False
starttime=time.time()
for f in range(start,end+1):
 filename=os.path.join(ROOT,'frames',f'frame_{f:04d}.jpg')
 if os.path.exists(filename):continue
 s.frame_set(f);s.render.filepath=filename;bpy.ops.render.render(write_still=True)
 if (f-start)%24==0 or f==end:print('PROGRESS',start,end,f,round(time.time()-starttime,1),flush=True)
