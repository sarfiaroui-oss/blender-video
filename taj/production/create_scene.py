import bpy,math,random,json,os,time,sys
from mathutils import Vector,Matrix,Quaternion
from math import sin,cos,pi,exp
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='Sunset conversation — animated world'
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.fps=24;s.frame_start=1;s.frame_end=2880;s.render.film_transparent=True
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.compression=20
s.render.threads_mode='FIXED';s.render.threads=8
s.world=bpy.data.worlds.new('Soft evening ambient');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.52,.43,.55,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
s.view_settings.view_transform='AgX'
random.seed(9)

def material(name,color,rough=.5,metal=0,em=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=em;return m
cream=material('Warm ivory',(.71,.64,.49),.48);brass=material('Brushed warm brass',(.38,.19,.055),.34,.55);dark=material('Deep green ceramic',(.022,.051,.041),.55);petal=material('Ivory daisy petals',(.88,.81,.65),.65);pollen=material('Golden pollen',(.65,.31,.045),.7);leaf=material('Meadow leaves',(.045,.115,.025),.8);mouthmat=material('Soft mouth interior',(.11,.018,.018),.85);tooth=material('Soft ivory teeth',(.8,.75,.65),.55)

def assign(o,m):o.data.materials.append(m);return o

def empty(name):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);return o

def sphere(name,loc,scale,m,parent=None,segments=24):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;assign(o,m)
 for p in o.data.polygons:p.use_smooth=True
 if parent:o.parent=parent
 return o

def cylinder(name,loc,r,depth,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;assign(o,m)
 be=o.modifiers.new('Rounded crafted edge','BEVEL');be.width=.035;be.segments=3
 o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');return o

def import_model(lab):
 with bpy.data.libraries.load(os.path.join(R,'assets',lab,'Character.blend'),link=False) as (src,dst):dst.objects=src.objects
 objs=[]
 for o in dst.objects:
  if o and o.type in ['MESH','ARMATURE']:s.collection.objects.link(o);objs.append(o)
 return objs

def improve_materials(ob):
 for mat in ob.data.materials:
  if not mat or not mat.use_nodes:continue
  bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if not bs:continue
  for key,val in [('Metallic',0),('Roughness',.5),('Specular IOR Level',.28),('Coat Weight',.08),('Coat Roughness',.35)]:
   for l in list(bs.inputs[key].links):mat.node_tree.links.remove(l)
   bs.inputs[key].default_value=val
  if bs.inputs['Normal'].is_linked:
   normalnode=bs.inputs['Normal'].links[0].from_node
   if normalnode.type=='NORMAL_MAP':normalnode.inputs['Strength'].default_value=.22
 for poly in ob.data.polygons:poly.use_smooth=True
 mod=ob.modifiers.new('Smooth facial contours','SUBSURF');mod.subdivision_type='CATMULL_CLARK';mod.levels=1;mod.render_levels=1

# Original character A: preserve the supplied skin rig and idle animation.
objsA=import_model('A');rig=next(o for o in objsA if o.type=='ARMATURE');a=next(o for o in objsA if o.type=='MESH')
rootA=empty('Character A — position');rootA.location=(-2.18,0,0);rootA.rotation_euler.z=-pi/2+.24;rootA.scale=(2.65,)*3
for o in objsA:
 if o.parent not in objsA:o.parent=rootA
rig.animation_data_create()
for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
rig.animation_data.action=None
idle=bpy.data.actions.get('12_wait');tr=rig.animation_data.nla_tracks.new();tr.name='Gentle idle — supplied animation';st=tr.strips.new('Waiting and listening',1,idle);st.repeat=20;st.frame_end=2881
improve_materials(a)
# Original character C: add restrained deformation controls to the supplied static model.
objsC=import_model('C');c=next(o for o in objsC if o.type=='MESH')
c.data.transform(c.matrix_world);c.matrix_world=Matrix.Identity(4)
rootC=empty('Character C — position');rootC.location=(2.18,0,1.47);rootC.rotation_euler.z=-pi/2-.24;rootC.scale=(3.0,)*3;c.parent=rootC
improve_materials(c)
# Preserve the original high-resolution face textures; reduce secondary maps only.
for im in bpy.data.images:
 if 'BaseColor' not in im.name and im.size[0]>2048:im.scale(2048,2048)
 if 'BaseColor' in im.name and im.size[0]>4096:im.scale(4096,4096)

def clamp(v):return max(0,min(1,v))
def smooth(a,b,x):
 u=clamp((x-a)/(b-a));return u*u*(3-2*u)
def shape(mesh,name,fn):
 if not mesh.data.shape_keys:mesh.shape_key_add(name='Basis')
 key=mesh.shape_key_add(name=name)
 for v,co in zip(mesh.data.vertices,key.data):co.co=fn(v.co.copy())
 return key

def rotate_weight(p,pivot,axis,angle,w):
 return p+(Matrix.Rotation(angle,3,axis)@(p-pivot)+pivot-p)*w
# Mild, identity-preserving expressions; the faces are not re-sculpted.
Ckeys={}
Ckeys['nod']=shape(c,'Head — gentle nod',lambda p:rotate_weight(p,Vector((0,0,.235)),'Y',.10,smooth(.19,.285,p.z)))
Ckeys['turn']=shape(c,'Head — turn toward companion',lambda p:rotate_weight(p,Vector((0,0,.235)),'Z',-.19,smooth(.19,.285,p.z)))
def c_arm(p):
 w=smooth(.055,.11,p.y)*(1-smooth(.15,.22,p.z))*smooth(-.27,-.16,p.z)
 return rotate_weight(p,Vector((0,.075,.18)),'X',.26,w)
Ckeys['gesture']=shape(c,'Hand — conversational gesture',c_arm)
Ckeys['breath']=shape(c,'Breathing',lambda p:p+Vector((.003*exp(-((p.z-.1)/.17)**2),0,0)))
def c_speech(p):
 w=exp(-((p.y)/.031)**2)*smooth(.025,.055,p.x)*(1-smooth(.328,.341,p.z))*smooth(.275,.305,p.z)
 return p+Vector((.001*w,0,-.008*w))
Ckeys['speech']=shape(c,'Speech — soft jaw movement',c_speech)
def c_blink(p):
 w=exp(-((abs(p.y)-.035)/.021)**4)*exp(-((p.z-.382)/.018)**4)*smooth(.025,.055,p.x)
 return p+Vector((0,0,-(p.z-.382)*.85*w))
Ckeys['blink']=shape(c,'Blink',c_blink)
# Character A expressions are added before the original armature deforms the mesh.
bpy.context.view_layer.update();aw=rig.matrix_world.inverted()@a.matrix_world;ai=aw.inverted()
def a_speech(p):
 w=aw@p;g=exp(-((w.y-.002)/.046)**2)*smooth(.09,.14,w.x)*(1-smooth(.716,.734,w.z))*smooth(.675,.702,w.z)
 return p+ai.to_3x3()@Vector((.001*g,0,-.010*g))
Akeys={'speech':shape(a,'Speech — soft jaw movement',a_speech)}
def a_blink(p):
 w=aw@p;g=exp(-((abs(w.y-.002)-.069)/.035)**4)*exp(-((w.z-.802)/.025)**4)*smooth(.08,.11,w.x)
 return p+ai.to_3x3()@Vector((0,0,-(w.z-.802)*.8*g))
Akeys['blink']=shape(a,'Blink',a_blink)
headctrl=empty('A — expressive head control');headctrl.rotation_mode='QUATERNION'
con=rig.pose.bones['mixamorig:Head'].constraints.new('COPY_ROTATION');con.name='Gentle conversational head motion';con.target=headctrl;con.owner_space='LOCAL';con.target_space='LOCAL';con.mix_mode='AFTER'
# A small dark inner mouth follows each character's lips, for readable speech at conversational distance.
mouthA=sphere('A — speaking mouth',(0,0,0),(.001,.023,.005),mouthmat,segments=20)
mouthC=sphere('C — speaking mouth',(0,0,0),(.001,.014,.004),mouthmat,parent=rootC,segments=20)
# User's Taj Mahal model becomes a miniature exhibit between the two characters.
B=next(o for o in import_model('B') if o.type=='MESH');B.name='Taj Mahal — supplied model';B.data.transform(B.matrix_world);B.matrix_world=Matrix.Identity(4)
coords=[v.co for v in B.data.vertices];lo=Vector([min(p[j] for p in coords) for j in range(3)]);hi=Vector([max(p[j] for p in coords) for j in range(3)])
center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));B.data.transform(Matrix.Translation(-center));B.rotation_euler.z=-pi/2;B.scale=(2.15,)*3;B.location=(0,.30,.66)
for p in B.data.polygons:p.use_smooth=True
for mat in B.data.materials:
 if mat and mat.use_nodes:
  bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs:
   for l in list(bs.inputs['Metallic'].links):mat.node_tree.links.remove(l)
   bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.8
base=cylinder('Exhibit | deep green plinth',(0,.3,.31),1.37,.60,dark);base.scale.y=.84
rim=cylinder('Exhibit | brass rim',(0,.3,.62),1.39,.065,brass);rim.scale.y=.84
# Engraved exhibit label facing the camera.
cu=bpy.data.curves.new('Exhibit lettering','FONT');cu.body='TAJ MAHAL';cu.align_x='CENTER';cu.size=.13;cu.extrude=.001
o=bpy.data.objects.new('Exhibit lettering',cu);s.collection.objects.link(o);o.location=(0,-.87,.32);o.rotation_euler=(pi/2,0,0);assign(o,cream)
# Contact shadows are feathered cards, preserving the photographed meadow beneath the actors.
def shadow(name,loc,scale):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexCoord');dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,0);nt.links.new(tex.outputs['UV'],dist.inputs[0]);r=nt.nodes.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=.05;r.inputs['From Max'].default_value=.5;r.inputs['To Min'].default_value=.55;r.inputs['To Max'].default_value=0;nt.links.new(dist.outputs['Value'],r.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.012,.018,.008,1);mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(r.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0])
 bpy.ops.mesh.primitive_plane_add(size=2,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;assign(o,m)
 if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'
shadow('A — contact shadow',(-2.18,.10,.01),(.55,.43,1));shadow('C — contact shadow',(2.18,.10,.01),(.55,.43,1));shadow('Exhibit — contact shadow',(0,.3,.015),(1.55,1.2,1))
# A few real three-dimensional daisies at the frame edges add depth and a soft breeze.
flowers=[]
for k in range(22):
 x=random.choice([-1,1])*random.uniform(3.15,4.8);y=random.uniform(-1.5,1.2);z=random.uniform(.16,.36)
 root=empty('Daisy %02d'%k);root.location=(x,y,0);flowers.append(root)
 stem=cylinder('Daisy stem',(0,0,z/2),.008,z,leaf);stem.parent=root
 center=sphere('Golden daisy heart',(0,0,z),(.045,.045,.027),pollen,root,segments=12)
 for j in range(9):
  aa=j*2*pi/9;o=sphere('Daisy petal',(.068*cos(aa),.068*sin(aa),z-.01),(.073,.023,.009),petal,root,segments=12);o.rotation_euler.z=aa
# A soft three-light portrait rig shapes faces and gives the hair a sunset rim.
def area(name,loc,target,power,color,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Large peach key',(-4,-5,6),(0,0,1.6),950,(1,.77,.60),5.0)
area('Soft lavender face fill',(4,-4,4),(0,0,1.6),700,(.68,.75,1),4.5)
area('Golden hair rim',(-3,4,5),(0,0,1.7),1400,(1,.50,.25),4)
area('Eye catchlight',(0,-6,4),(0,0,1.9),150,(1,.94,.82),2.5)
# The generated clean reference environment is a full-resolution background plate.
s.use_nodes=True;nt=s.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');bg=nt.nodes.new('CompositorNodeImage');bg.image=bpy.data.images.load(os.path.join(R,'assets','sunset_meadow.png'));scale=nt.nodes.new('CompositorNodeScale');scale.space='RENDER_SIZE';scale.frame_method='CROP';nt.links.new(bg.outputs['Image'],scale.inputs['Image']);over=nt.nodes.new('CompositorNodeAlphaOver');over.inputs[0].default_value=1;nt.links.new(scale.outputs[0],over.inputs[1]);nt.links.new(rl.outputs[0],over.inputs[2]);out=nt.nodes.new('CompositorNodeComposite');nt.links.new(over.outputs[0],out.inputs[0])
# Camera shots alternate between two-shot, speaker close-ups, and the user's monument model.
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Conversation camera';s.camera=cam;cam.data.clip_end=100
lines=json.load(open(os.path.join(R,'production','dialogue_timed.json')))

def camera_pose(kind,u):
 if kind=='wide':return (0,-11.4+.25*sin(u*pi),4.05),(0,.1,1.43),46
 if kind=='A':return (-1.25,-8.1+.14*u,3.05),(-2.08,0,1.74),60
 if kind=='C':return (1.25,-8.2+.14*u,3.15),(2.08,0,1.92),62
 if kind=='model':return (1.2-.7*u,-6.6,3.0),(0,.3,1.32),57
 if kind=='pair':return (0,-9.4+.1*u,3.5),(0,.1,1.76),47

def current_line(t):
 for i,l in enumerate(lines):
  if l['start']-.25<=t<=l['end']+.4:return i,l
 return None,None
# Stable camera cut choices leave both faces visible often.
shotkinds=['wide','C','A','C','A','model','A','C','A','model','A','pair','A','C']
headbone=rig.data.bones['mixamorig:Head'];mouthA.parent=rig;mouthA.parent_type='BONE';mouthA.parent_bone=headbone.name;mouthA.matrix_parent_inverse=Matrix.Identity(4);mouthA.matrix_basis=Matrix.Translation((0,-headbone.length,0))@headbone.matrix_local.inverted()@Matrix.Translation((.159,.0018,.713));head_axis=headbone.matrix_local.to_3x3().inverted()@Vector((0,1,0))
for f in range(1,2881):
 t=(f-1)/24;idx,line=current_line(t)
 ampA=sum(l['envelope'][f-1] for l in lines if l['speaker']=='A');ampC=sum(l['envelope'][f-1] for l in lines if l['speaker']=='C')
 talkingA=1 if line and line['speaker']=='A' else 0;talkingC=1 if line and line['speaker']=='C' else 0
 Akeys['speech'].value=ampA*.7;Akeys['speech'].keyframe_insert('value',frame=f)
 # A short blink every few seconds, never a permanent squint.
 blinkA=max(0,1-abs((t+1.0)%4.9-2.4)/.11);blinkC=max(0,1-abs((t+.7)%5.7-2.8)/.12)
 Akeys['blink'].value=blinkA*.85;Akeys['blink'].keyframe_insert('value',frame=f)
 nod=.025*sin(t*1.7)+.028*talkingA*sin(t*3.1);headctrl.rotation_quaternion=Quaternion(head_axis,nod);headctrl.keyframe_insert('rotation_quaternion',frame=f)
 vals={'nod':.18+.35*sin(t*1.4)*(.3+.7*talkingC),'turn':.35+.18*sin(t*.65),'gesture':talkingC*(.35+.3*sin(t*2.2)),'breath':.45+.45*sin(t*1.2),'speech':ampC*.8,'blink':blinkC*.85}
 for name,v in vals.items():Ckeys[name].value=v;Ckeys[name].keyframe_insert('value',frame=f)
 # Keep the mouth shapes small and aligned with the actual animated face.
 mouthA.scale=(.0011,.023,.0002+.004*ampA);mouthA.keyframe_insert('scale',frame=f)
 nodmat=Matrix.Rotation(.10*vals['nod'],3,'Y');turnmat=Matrix.Rotation(-.19*vals['turn'],3,'Z');headpivot=Vector((0,0,.235));mouthC.location=headpivot+(turnmat@nodmat)@(Vector((.073,0,.326))-headpivot);mouthC.rotation_euler=(turnmat@nodmat).to_euler();mouthC.scale=(.0013,.014,.00015+.0035*ampC)
 mouthC.keyframe_insert('location',frame=f);mouthC.keyframe_insert('rotation_euler',frame=f);mouthC.keyframe_insert('scale',frame=f)
 if idx is None:kind='wide';u=t/120
 else:kind=shotkinds[idx];u=clamp((t-line['start'])/(line['end']-line['start']))
 # During pauses preserve the preceding camera until the next speaker cut.
 if line is None and 4.5<t<115:
  prior=[(i,l) for i,l in enumerate(lines) if l['end']<t]
  if prior:kind=shotkinds[prior[-1][0]];u=1
 loc,target,lens=camera_pose(kind,u);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('lens',frame=f)
 if f%24==1:
  for j,fl in enumerate(flowers):fl.rotation_euler=(.04*sin(t*.9+j),.03*sin(t*1.1+j),0);fl.keyframe_insert('rotation_euler',frame=f)
print('ANIMATION BAKED',flush=True)
for o in [cam,mouthA,mouthC,headctrl]:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
for i,l in enumerate(lines):s.timeline_markers.new(f"{i+1:02d} | Character {l['speaker']} speaks",frame=int(l['start']*24)+1)
s['Title']='TAJ MAHAL — A SUNSET CONVERSATION';s['Duration']='120 seconds';s['Speech engine']='Piper / ONNX Runtime';s['Voice A']='en_US-amy-medium';s['Voice C']='en_US-lessac-medium';s['Reference']='The user-supplied sunset flower-field image; original supplied characters and monument model.'
s.frame_set(1);s.render.filepath=os.path.join(R,'frames','frame_')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'output','Taj_Mahal_Sunset_Conversation.blend'),compress=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if 'preview' in args:
 for tm in [2,8,16,24,33,46,62,101,111]:
  s.frame_set(int(tm*24)+1);s.render.filepath=os.path.join(R,'previews',f'scene_{tm:03}.png');t0=time.time();bpy.ops.render.render(write_still=True);print('PREVIEW',tm,'SECONDS',round(time.time()-t0,2),flush=True)
