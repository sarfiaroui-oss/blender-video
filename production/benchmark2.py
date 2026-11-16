exec(open('production/benchmark.py').read().split("for engine in")[0])
s.render.resolution_x=960;s.render.resolution_y=540
s.cycles.use_denoising=False
s.eevee.taa_render_samples=8
for engine in ['CYCLES','BLENDER_EEVEE_NEXT','BLENDER_WORKBENCH']:
 s.render.engine=engine;s.render.threads_mode='FIXED';s.render.threads=8
 for n in range(3):
  s.camera.location.x=4+n*.1;s.render.filepath=f'previews/bench_{engine}_{n}.png';t=time.time();bpy.ops.render.render(write_still=True);print('RESULT',engine,n,time.time()-t,flush=True)
