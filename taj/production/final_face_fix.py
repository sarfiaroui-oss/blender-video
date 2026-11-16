import bpy,json,math,os
from mathutils import Matrix,Vector
s=bpy.context.scene;rig=bpy.data.objects['Character_Rig'];bone=rig.data.bones['mixamorig:Head'];rootC=bpy.data.objects['Character C — position'];positions=json.load(open('taj/production/eye_positions.json'))
c_glints=[]
for label in ['A','C']:
 for i,side in enumerate([-1,1]):
  o=bpy.data.objects[f'{label} — eye glint {side}'];o.hide_viewport=False;p=Vector(positions[label][i]);p.y-=.004 if label=='A' else .0015;p.z+=.004 if label=='A' else .0018;p.x+=.001
  if label=='A':o.matrix_basis=Matrix.Translation((0,-bone.length,0))@bone.matrix_local.inverted()@Matrix.Translation(p)
  else:c_glints.append((o,p))
# Correct the child's eye-control region to the actual eye positions in the supplied mesh.
a=bpy.data.objects['tripo_node_9eef1479-c5bf-4540-84a9-4249edd92803']
aw=rig.matrix_world.inverted()@a.matrix_world;ai=aw.inverted();blink=a.data.shape_keys.key_blocks['Blink'];basis=a.data.shape_keys.key_blocks['Basis']
for dst,src in zip(blink.data,basis.data):
 w=aw@src.co;g=math.exp(-((abs(w.y+.004)-.048)/.027)**4)*math.exp(-((w.z-.782)/.026)**4)*max(0,min(1,(w.x-.07)/.035));dst.co=src.co+ai.to_3x3()@Vector((0,0,-(w.z-.782)*.83*g))
for obj in [a,bpy.data.objects['tripo_node_3f9f64c3-81bf-4055-88e5-2bcaaeceb93b']]:
 for fc in obj.data.shape_keys.animation_data.action.fcurves:
  if fc.data_path=='key_blocks["Blink"].value':
   for k in fc.keyframe_points:k.co.y*=.70
key=bpy.data.objects['tripo_node_3f9f64c3-81bf-4055-88e5-2bcaaeceb93b'].data.shape_keys
curves={n:next(fc for fc in key.animation_data.action.fcurves if fc.data_path=='key_blocks["'+n+'"].value') for n in ['Head — gentle nod','Head — turn toward companion']}
for f in range(1,2881):
 t=(f-1)/24;blinkA=max(0,1-abs((t+1)%4.9-2.4)/.11);blinkC=max(0,1-abs((t+.7)%5.7-2.8)/.12)
 for side in [-1,1]:
  o=bpy.data.objects[f'A — eye glint {side}'];r=.0033*(1-blinkA);o.scale=(r*.25,r,r);o.keyframe_insert('scale',frame=f)
 transform=Matrix.Rotation(-.19*curves['Head — turn toward companion'].evaluate(f),3,'Z')@Matrix.Rotation(.1*curves['Head — gentle nod'].evaluate(f),3,'Y');pivot=Vector((0,0,.235))
 for o,p in c_glints:
  o.location=pivot+transform@(p-pivot);o.rotation_euler=transform.to_euler();r=.0015*(1-blinkC);o.scale=(r*.25,r,r);o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f);o.keyframe_insert('scale',frame=f)
s.frame_set(1);s.cycles.samples=8;s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB';s.render.image_settings.quality=96
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('taj/output/Taj_Mahal_Sunset_Conversation.blend'),compress=True)
for tm in [16,21,24]:
 s.frame_set(tm*24+1);s.render.filepath=os.path.abspath(f'taj/previews/approved_{tm:03}.jpg');bpy.ops.render.render(write_still=True)
print('FACE POLISH COMPLETE',flush=True)
