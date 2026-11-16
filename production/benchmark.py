import bpy,time,os
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.samples=8
s.cycles.use_denoising=True
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Space');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.03,.03,.06,1)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16)
o=bpy.context.object
m=bpy.data.materials.new('metal');m.diffuse_color=(.1,.5,.6,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.05,.45,.6,1);m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.5;o.data.materials.append(m)
bpy.ops.object.light_add(type='AREA',location=(2,-3,4));bpy.context.object.data.energy=700;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
bpy.ops.object.camera_add(location=(4,-6,3));c=bpy.context.object;c.rotation_euler=(Vector((0,0,0))-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c
for engine in ['BLENDER_EEVEE_NEXT','BLENDER_WORKBENCH','CYCLES']:
 s.render.engine=engine;s.render.filepath=f'previews/test_{engine}.png';t=time.time()
 if engine=='CYCLES':s.render.threads_mode='FIXED';s.render.threads=8
 try:
  bpy.ops.render.render(write_still=True);print('BENCHMARK',engine,time.time()-t,flush=True)
 except Exception as e:print('FAIL',engine,str(e),flush=True)
