import bpy,math,os,time
from mathutils import Matrix,Vector
s=bpy.context.scene
mat=bpy.data.materials.new('Gentle eye catchlights');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(1,.96,.87,1);em.inputs[1].default_value=1.6;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
rig=bpy.data.objects['Character_Rig'];bone=rig.data.bones['mixamorig:Head'];rootC=bpy.data.objects['Character C — position'];a=[];c=[]
for char in ['A','C']:
 for side in [-1,1]:
  if char=='A':pos=(.146,side*.069-.008,.811);radius=.0048
  else:pos=(.083,side*.034-.003,.391);radius=.0022
  bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8);o=bpy.context.object;o.name=f'{char} — eye glint {side}';o.data.materials.append(mat)
  for p in o.data.polygons:p.use_smooth=True
  if char=='A':
   o.parent=rig;o.parent_type='BONE';o.parent_bone=bone.name;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Translation((0,-bone.length,0))@bone.matrix_local.inverted()@Matrix.Translation(pos);a.append((o,radius))
  else:o.parent=rootC;o.location=pos;c.append((o,radius,Vector(pos)))
  o.scale=(radius*.25,radius,radius)
for f in range(1,2881):
 t=(f-1)/24
 blinkA=max(0,1-abs((t+1.0)%4.9-2.4)/.11);blinkC=max(0,1-abs((t+.7)%5.7-2.8)/.12)
 for o,r in a:o.scale=(r*.25*(1-blinkA),r*(1-blinkA),r*(1-blinkA));o.keyframe_insert('scale',frame=f)
 # Read the existing shape controls by evaluating their scalar curves, without evaluating the whole scene.
 key=bpy.data.objects['tripo_node_3f9f64c3-81bf-4055-88e5-2bcaaeceb93b'].data.shape_keys
 vals={}
 for n in ['Head — gentle nod','Head — turn toward companion']:
  path='key_blocks["'+n+'"].value';fc=next(fc for fc in key.animation_data.action.fcurves if fc.data_path==path);vals[n]=fc.evaluate(f)
 transform=Matrix.Rotation(-.19*vals['Head — turn toward companion'],3,'Z')@Matrix.Rotation(.1*vals['Head — gentle nod'],3,'Y');pivot=Vector((0,0,.235))
 for o,r,p in c:o.location=pivot+transform@(p-pivot);o.rotation_euler=transform.to_euler();o.scale=(r*.25*(1-blinkC),r*(1-blinkC),r*(1-blinkC));o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f);o.keyframe_insert('scale',frame=f)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('taj/output/Taj_Mahal_Sunset_Conversation.blend'),compress=True)
for tm in [16,21,24,30.6]:
 s.frame_set(int(tm*24)+1);s.render.filepath=os.path.abspath(f'taj/previews/eyes_{int(tm*10):04}.png');t=time.time();bpy.ops.render.render(write_still=True);print('EYE CHECK',tm,time.time()-t,flush=True)
