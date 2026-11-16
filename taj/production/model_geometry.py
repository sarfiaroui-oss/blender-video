import bpy,os,json
from mathutils import Vector
R=os.path.abspath('taj')
for lab in ['A','C']:
 bpy.ops.wm.open_mainfile(filepath=f'{R}/assets/{lab}/Character.blend',load_ui=False,use_scripts=False)
 d={}
 for o in bpy.context.scene.objects:
  d[o.name]={'type':o.type,'matrix':[list(r) for r in o.matrix_world]}
  if o.type=='ARMATURE':
   o.animation_data_clear()
   for p in o.pose.bones:p.matrix_basis.identity()
   d[o.name]['bones']={b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in o.data.bones}
  if o.type=='MESH':
   d[o.name]['range']=[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)]
   d[o.name]['shape_keys']=[b.name for b in o.data.shape_keys.key_blocks] if o.data.shape_keys else []
 open(f'{R}/previews/geometry_{lab}.json','w').write(json.dumps(d,indent=2))
 print('GEOMETRY',lab,flush=True)
