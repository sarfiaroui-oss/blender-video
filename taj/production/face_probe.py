import bpy,os,json
from mathutils import Vector
R=os.path.abspath('taj')
for lab in ['A','C']:
 bpy.ops.wm.open_mainfile(filepath=f'{R}/assets/{lab}/Character.blend',load_ui=False,use_scripts=False)
 o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 print('FACE',lab)
 centers=[.70,.72,.74,.76,.78,.80,.82] if lab=='A' else [.28,.30,.31,.32,.33,.34,.36]
 for z in centers:
  pts=[v for v in vs if abs(v.z-z)<.01 and abs(v.y)<.035]
  print(z,sorted([round(v.x,4) for v in pts],reverse=True)[:6])
