import bpy,time,os
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.cycles.max_bounces=3;s.cycles.diffuse_bounces=1;s.cycles.glossy_bounces=1;s.cycles.transparent_max_bounces=6;s.render.threads_mode='FIXED';s.render.threads=8;s.render.use_persistent_data=True
for tm in [16,24]:
 s.frame_set(tm*24+1);s.render.filepath=os.path.abspath(f'taj/previews/cycles_{tm:03}.png');t=time.time();bpy.ops.render.render(write_still=True);print('CYCLES',tm,time.time()-t,flush=True)
