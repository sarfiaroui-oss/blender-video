import bpy,os,json
from mathutils import Vector
ROOT=os.path.abspath('taj')
for label in ['A','B','C']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'assets',label,'Character.blend'),load_ui=False,use_scripts=False)
 s=bpy.context.scene
 info={'label':label,'objects':[],'actions':[],'images':[]}
 for ob in s.objects:
  d={'name':ob.name,'type':ob.type,'location':list(ob.location),'dimensions':list(ob.dimensions)}
  if ob.type=='ARMATURE':d['bones']=[b.name for b in ob.data.bones]
  if ob.type=='MESH':d['vertices']=len(ob.data.vertices);d['materials']=[m.name if m else '' for m in ob.data.materials]
  info['objects'].append(d)
 for a in bpy.data.actions:info['actions'].append({'name':a.name,'range':list(a.frame_range)})
 for i in bpy.data.images:info['images'].append({'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)})
 open(os.path.join(ROOT,'previews',f'model_{label}.json'),'w').write(json.dumps(info,indent=2))
 # Only the visible mesh is used to frame the model; remove any pre-existing cameras and lights.
 meshes=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
 coords=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 lo=Vector([min(v[j] for v in coords) for j in range(3)]);hi=Vector([max(v[j] for v in coords) for j in range(3)]);center=(lo+hi)/2;size=max(hi-lo)
 for o in list(s.objects):
  if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.object.camera_add(location=center+Vector((size*.15,-size*1.9,size*.2)))
 cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=size*1.2;s.camera=cam
 s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=700;s.render.resolution_y=700;s.render.resolution_percentage=100
 s.display.shading.light='STUDIO';s.display.shading.color_type='TEXTURE';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
 s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Preview world');s.world.color=(.12,.12,.12)
 s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(ROOT,'previews',f'model_{label}.png');s.render.use_sequencer=False
 bpy.ops.render.render(write_still=True)
 print('INSPECTED',label,flush=True)
