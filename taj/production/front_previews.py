import bpy,os,math
from mathutils import Vector
R=os.path.abspath('taj')
for lab in ['A','B','C']:
 bpy.ops.wm.open_mainfile(filepath=f'{R}/assets/{lab}/Character.blend',load_ui=False,use_scripts=False);s=bpy.context.scene
 if lab=='A':
  rig=next(o for o in s.objects if o.type=='ARMATURE')
  for tr in rig.animation_data.nla_tracks:tr.mute=True
  rig.animation_data.action=bpy.data.actions['12_wait'];s.frame_set(45)
 meshes=[o for o in s.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 lo=Vector([min(v[j] for v in coords) for j in range(3)]);hi=Vector([max(v[j] for v in coords) for j in range(3)]);center=(lo+hi)/2;size=max(hi-lo)
 bpy.ops.object.camera_add(location=center+Vector((size*2.0,size*.03,size*.12)));cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=size*1.12;s.camera=cam
 s.world=bpy.data.worlds.new('Preview');s.world.color=(.13,.13,.13)
 s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=700;s.render.resolution_y=900;s.render.resolution_percentage=100
 s.display.shading.light='STUDIO';s.display.shading.color_type='TEXTURE';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
 s.render.image_settings.file_format='PNG';s.render.use_sequencer=False;s.render.filepath=f'{R}/previews/front_{lab}.png';bpy.ops.render.render(write_still=True)
