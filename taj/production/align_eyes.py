import bpy,os,json,math
from mathutils import Vector,Matrix
s=bpy.context.scene;cam=s.camera;rig=bpy.data.objects['Character_Rig'];bone=rig.data.bones['mixamorig:Head'];rootC=bpy.data.objects['Character C — position']
for o in bpy.data.objects:
 if 'eye glint' in o.name:o.hide_viewport=True
results={}
for label,tm,points in [('A',24,[(574,381),(674,381)]),('C',16,[(626,265),(683,264)])]:
 s.frame_set(tm*24+1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();inv=cam.calc_matrix_camera(deps,x=1280,y=720,scale_x=1,scale_y=1).inverted();positions=[]
 for px,py in points:
  clip=Vector((2*px/1280-1,1-2*py/720,-1,1));p=inv@clip;p/=p.w;wp=cam.matrix_world@p.to_3d();ray=(wp-cam.location).normalized();hit,loc,norm,idx,ob,matrix=s.ray_cast(deps,cam.location,ray)
  if not hit:raise RuntimeError('No face hit')
  print('HIT',label,px,py,ob.name,list(loc),flush=True)
  if label=='A':
   deform=rig.matrix_world@rig.pose.bones['mixamorig:Head'].matrix@bone.matrix_local.inverted();local=deform.inverted()@(loc+norm*.003)
  else:
   keys=bpy.data.objects['tripo_node_3f9f64c3-81bf-4055-88e5-2bcaaeceb93b'].data.shape_keys.key_blocks;turn=keys['Head — turn toward companion'].value;nod=keys['Head — gentle nod'].value;mat=Matrix.Rotation(-.19*turn,3,'Z')@Matrix.Rotation(.1*nod,3,'Y');pivot=Vector((0,0,.235));local=pivot+mat.inverted()@(rootC.matrix_world.inverted()@(loc+norm*.002)-pivot)
  positions.append(list(local));print('REST',label,list(local),flush=True)
 results[label]=positions
open('taj/production/eye_positions.json','w').write(json.dumps(results))
