import bpy,sys,os,time
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args=sys.argv[sys.argv.index('--')+1:];start,end=map(int,args[:2]);s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=8;s.render.use_persistent_data=True;s.render.use_sequencer=False
s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB';s.render.image_settings.quality=96
begin=time.time()
for i in range(start,end+1):
 path=os.path.join(R,'frames',f'frame_{i:04d}.jpg')
 if os.path.exists(path):continue
 s.frame_set((i-1)*2+1);s.render.filepath=path;bpy.ops.render.render(write_still=True)
 if (i-start)%12==0 or i==end:print('RENDER',start,end,i,round(time.time()-begin,1),flush=True)
