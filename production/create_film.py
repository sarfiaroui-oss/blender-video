import bpy, math, random, os, sys, time
from mathutils import Vector
from math import sin, cos, pi
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'output'); os.makedirs(OUT,exist_ok=True)
random.seed(28)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=2;s.cycles.use_denoising=False
s.cycles.max_bounces=1;s.cycles.diffuse_bounces=0;s.cycles.glossy_bounces=0;s.cycles.transmission_bounces=0
s.cycles.use_adaptive_sampling=False;s.cycles.use_light_tree=False
s.render.threads_mode='FIXED';s.render.threads=8
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.fps=24;s.frame_start=1;s.frame_end=2880
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=15
s.render.film_transparent=False
s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('Interstellar night');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.007,.012,.026,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
s.render.use_persistent_data=True

def mat(name,color,em=0,rough=.65,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 nt=m.node_tree;nt.nodes.clear()
 geo=nt.nodes.new('ShaderNodeNewGeometry')
 d1=nt.nodes.new('ShaderNodeVectorMath');d1.operation='DOT_PRODUCT';d1.inputs[1].default_value=(-.35,-.55,.76);nt.links.new(geo.outputs['Normal'],d1.inputs[0])
 d2=nt.nodes.new('ShaderNodeVectorMath');d2.operation='DOT_PRODUCT';d2.inputs[1].default_value=(.8,.4,.4);nt.links.new(geo.outputs['Normal'],d2.inputs[0])
 def light(dot,fac):
  mx=nt.nodes.new('ShaderNodeMath');mx.operation='MAXIMUM';mx.inputs[1].default_value=0;nt.links.new(dot.outputs['Value'],mx.inputs[0])
  mu=nt.nodes.new('ShaderNodeMath');mu.operation='MULTIPLY';mu.inputs[1].default_value=fac;nt.links.new(mx.outputs[0],mu.inputs[0]);return mu
 l1=light(d1,.85);l2=light(d2,.3)
 ad=nt.nodes.new('ShaderNodeMath');ad.operation='ADD';nt.links.new(l1.outputs[0],ad.inputs[0]);nt.links.new(l2.outputs[0],ad.inputs[1])
 amb=nt.nodes.new('ShaderNodeMath');amb.operation='ADD';amb.inputs[1].default_value=.22;nt.links.new(ad.outputs[0],amb.inputs[0])
 glow=nt.nodes.new('ShaderNodeMath');glow.name='Glow';glow.operation='ADD';glow.inputs[1].default_value=em;nt.links.new(amb.outputs[0],glow.inputs[0])
 surf=nt.nodes.new('ShaderNodeEmission');surf.name='Stylized Surface';surf.inputs['Color'].default_value=(*color,1);nt.links.new(glow.outputs[0],surf.inputs['Strength'])
 out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(surf.outputs[0],out.inputs['Surface'])
 return m
ivory=mat('Warm porcelain | hull',(.78,.74,.58),.12)
gold=mat('Brushed copper',(.48,.21,.065),.12)
dark=mat('Carbon ceramic',(.025,.054,.068),.12)
black=mat('Obsidian glass',(.006,.018,.028),.1)
teal=mat('Engine plasma',(.025,.7,.95),3.5)
white=mat('Starlight',(.65,.85,1),2)
orange=mat('Awakening | amber',(.95,.30,.055),.35)
coremat=mat('Beacon heart',(.9,.35,.07),.45)
rockmat=mat('Asteroid basalt',(.07,.095,.12),.10)

def assign(o,m):o.data.materials.append(m);return o

def parent(o,p):
 if p:o.parent=p
 return o

def empty(name,loc=(0,0,0)):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.location=loc;return o

def uv(name,loc,scale,m,p=None,segs=32,rings=16):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segs,ring_count=rings,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;assign(o,m);parent(o,p)
 for f in o.data.polygons:f.use_smooth=True
 return o

def ico(name,loc,scale,m,p=None,sub=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;assign(o,m);parent(o,p);return o

def box(name,loc,scale,m,p=None,bevel=.06):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 assign(o,m);parent(o,p)
 if bevel:
  md=o.modifiers.new('Soft engineered edges','BEVEL');md.width=bevel;md.segments=2
  md=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def cyl(name,loc,r,depth,m,p=None,rot=(pi/2,0,0),vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc,rotation=rot)
 o=bpy.context.object;o.name=name;assign(o,m);parent(o,p)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o

def torus(name,loc,r,thick,m,p=None,rot=(0,0,0),segs=80):
 bpy.ops.mesh.primitive_torus_add(major_segments=segs,minor_segments=8,major_radius=r,minor_radius=thick,location=loc,rotation=rot)
 o=bpy.context.object;o.name=name;assign(o,m);parent(o,p)
 for f in o.data.polygons:f.use_smooth=True
 return o

def tube(name,coords,width,m,p=None):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=width;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(coords)-1)
 for pt,co in zip(sp.points,coords):pt.co=(*co,1)
 o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);assign(o,m);parent(o,p);return o

# A hand-built survey craft: four engines, porcelain shell and a luminous optical eye.
ship=empty('ARI-01 | survey craft')
uv('Porcelain pressure shell',(0,0,0),(1,1.35,.68),ivory,ship)
uv('Lower carbon shell',(0,.08,-.27),(1.01,1.18,.46),dark,ship)
uv('Copper equatorial band',(0,.02,-.03),(1.018,1.29,.25),gold,ship)
uv('Top cap',(0,-.1,.19),(.93,1.2,.51),ivory,ship)
cyl('Optical bezel',(0,-1.18,.07),.56,.28,dark,ship)
torus('Ceramic optical rim',(0,-1.35,.07),.46,.065,ivory,ship,(pi/2,0,0))
cyl('Glass optic',(0,-1.35,.07),.42,.045,black,ship)
torus('Eye | cyan annulus',(0,-1.385,.07),.275,.045,teal,ship,(pi/2,0,0),48)
cyl('Eye | pupil',(0,-1.41,.07),.14,.015,teal,ship)
for x in [-1,1]:
 box('Wing spar',(x*1.28,.28,.02),(1.3,.36,.2),gold,ship)
 for y in [-.28,.94]:
  cyl('Engine sleeve',(x*1.64,y,.0),.29,.78,dark,ship)
  cyl('Engine armor',(x*1.64,y-.1,.0),.305,.42,ivory,ship)
  torus('Engine exhaust rim',(x*1.64,y+.4,0),.21,.045,gold,ship,(pi/2,0,0),32)
  cyl('Engine ion disk',(x*1.64,y+.43,0),.17,.02,teal,ship)
  uv('Ion plume',(x*1.64,y+.65,0),(.13,.30,.13),teal,ship,segs=16,rings=8)
 fin=box('Navigation fin',(x*1.34,.93,.4),(.08,.65,.55),ivory,ship);fin.rotation_euler.y=x*.35
 uv('Navigation light',(x*1.36,1.12,.64),(.07,.07,.07),teal if x==1 else orange,ship,segs=12,rings=8)
 for y in [-.3,.12,.54]:box('Hull ventilation',(x*.86,y,.33),(.08,.1,.18),dark,ship,.01)
 tube('Landing strut',[(x*.5,.3,-.45),(x*.65,.5,-.85)],.05,gold,ship)
 box('Landing pad',(x*.65,.5,-.86),(.26,.42,.08),dark,ship,.02)
tube('Antenna',[(.32,.52,.55),(.42,.68,1.24)],.025,gold,ship)
uv('Antenna tip',(.42,.68,1.24),(.065,.065,.065),teal,ship,segs=12,rings=8)
box('Top dorsal stripe',(0,.1,.67),(.12,.75,.028),gold,ship,.01)
# Tiny physical hull lettering, also editable.
cu=bpy.data.curves.new('ARI-01 hull marking','FONT');cu.body='ARI—01';cu.size=.16;cu.align_x='CENTER';cu.extrude=.001
ob=bpy.data.objects.new('ARI-01 hull marking',cu);s.collection.objects.link(ob);ob.parent=ship;ob.location=(0,-.45,.65);assign(ob,dark)

# An orbital relic made from nested, articulated copper rings.
relic=empty('The beacon')
ringroots=[]
for i,r in enumerate([5.5,4.25,3.0]):
 p=empty('Gimbal %d'%(i+1));p.parent=relic;ringroots.append(p)
 torus('Structural ring',(0,0,0),r,.17,gold,p)
 torus('Carbon inner ring',(0,0,0),r-.13,.085,dark,p)
 torus('Signal filament',(0,0,.11),r,.028,orange,p)
 for j in range(12):
  a=j*2*pi/12
  o=box('Segment clasp',(r*cos(a),r*sin(a),0),(.32,.48,.32),dark,p,.025);o.rotation_euler.z=a
  o=box('Amber status notch',((r+.01)*cos(a),(r+.01)*sin(a),.175),(.10,.23,.02),orange,p,.005);o.rotation_euler.z=a
 for j in range(4):
  a=j*pi/2
  cyl('Gimbal bearing',(r*cos(a),r*sin(a),0),.23,.5,ivory,p,rot=(0,0,0),vertices=16)
heart=ico('A crystalline heart',(0,0,0),(1.03,1.03,1.03),coremat,relic,sub=2)
for i in range(6):
 a=i*pi/3
 o=ico('Orbiting crystal',(1.65*cos(a),0,1.65*sin(a)),(.16,.3,.38),gold,relic,sub=1);o.rotation_euler.y=-a
# Decorative antenna petals.
for i in range(8):
 a=i*pi/4
 tube('Outer radial arm',[(5.55*cos(a),0,5.55*sin(a)),(6.35*cos(a),.45,6.35*sin(a))],.09,dark,relic)
 ico('Petal',(6.45*cos(a),.5,6.45*sin(a)),(.32,.23,.6),gold,relic,sub=1)

# Activation pulses expand out into space during the final act.
pulses=[]
for i in range(5):
 o=torus('Expanding signal %02d'%i,(0,0,0),1,.018,teal,rot=(pi/2,0,0),segs=96);pulses.append(o)
# Starfield is one emissive mesh to keep the render efficient.
verts=[];faces=[]
for i in range(1000):
 z=random.uniform(-1,1);a=random.uniform(0,2*pi);q=math.sqrt(1-z*z)
 center=Vector((240*q*cos(a),240*q*sin(a),240*z));normal=center.normalized()
 side=normal.cross(Vector((0,0,1))).normalized();up=normal.cross(side).normalized();radius=random.choice([.045,.06,.09,.13,.20])
 idx=len(verts)
 verts.extend([center+side*radius,center-side*radius+up*radius,center-side*radius-up*radius]);faces.append((idx,idx+1,idx+2))
me=bpy.data.meshes.new('A thousand distant suns');me.from_pydata(verts,[],faces);me.update()
o=bpy.data.objects.new('Starfield',me);s.collection.objects.link(o);assign(o,white)
# Ringed gas planet.
planetmat=mat('Planet | blue atmospheric bands',(.08,.17,.2),.12)
nt=planetmat.node_tree;bs=nt.nodes.get('Stylized Surface');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3.4;tex.inputs['Detail'].default_value=3
coord=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,1,7)
nt.links.new(coord.outputs['Generated'],mapping.inputs[0]);nt.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(.016,.055,.075,1)
ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.25,.53,.52,1)
nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Color'])
planetroot=empty('The sleeping giant',(-58,95,-4));planetroot.rotation_euler=(.2,.38,-.1)
uv('Gas giant',(0,0,0),(24,24,24),planetmat,planetroot,segs=96,rings=48)
ringmat=mat('Planet rings',(.27,.30,.28),.16)
# Thin annuli.
for inner,outer,m in [(29,32,gold),(32.3,35.4,ringmat),(36.4,39,ringmat)]:
 vs=[];fs=[]
 for j in range(160):
  a=j*2*pi/160;vs.extend([(inner*cos(a),inner*sin(a),0),(outer*cos(a),outer*sin(a),0)])
 for j in range(160):k=2*j;nk=2*((j+1)%160);fs.append((k,nk,nk+1,k+1))
 mesh=bpy.data.meshes.new('Dust annulus');mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new('Planet ring',mesh);s.collection.objects.link(o);parent(o,planetroot);assign(o,m)
# Sparse debris frames the approach without blocking the beacon.
asteroids=[]
for i in range(28):
 a=random.uniform(0,2*pi);r=random.uniform(14,34);loc=(r*cos(a),r*sin(a),random.uniform(-14,10))
 scale=random.uniform(.3,1.8)
 o=ico('Drifting basalt %02d'%i,loc,(scale,scale*.75,scale*.9),rockmat,sub=1);o.rotation_euler=[random.random()*3 for _ in range(3)];asteroids.append(o)
# A minimal lighting rig produces clean, readable forms without noisy indirect light.
def sun(name,rot,power,color):
 bpy.ops.object.light_add(type='SUN',rotation=rot);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.angle=.01
sun('Distant warm star',(.5,-.6,-.5),2.1,(1,.78,.53))
sun('Cold nebula fill',(1.7,.4,2.5),1.25,(.25,.65,1))
sun('Soft front fill',(.9,0,0),.6,(.55,.75,1))
# Optical bloom is restrained, keeping every mechanical detail readable.
s.use_nodes=True;nt=s.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');gl=nt.nodes.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='LOW';gl.threshold=1.4;gl.size=7;gl.mix=-.88
co=nt.nodes.new('CompositorNodeComposite');nt.links.new(rl.outputs['Image'],gl.inputs['Image']);nt.links.new(gl.outputs['Image'],co.inputs['Image'])

bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Cinema camera | ten shots';cam.data.lens=42;cam.data.clip_end=600;s.camera=cam

def ease(u):return u*u*(3-2*u)
def lerp(a,b,u):return tuple(x+(y-x)*u for x,y in zip(a,b))
def ship_state(t):
 if t<24:return lerp((0,-27,0),(0,-16,.35),ease(t/24))
 if t<48:return lerp((0,-16,.35),(0,-7,.3),ease((t-24)/24))
 if t<72:return lerp((0,-7,.3),(0,-3.8,0),ease((t-48)/24))
 if t<96:
  a=(t-72)/24*pi*.82
  return (7*sin(a),-6*cos(a),.7+1.5*sin(a*.8))
 return lerp((7*sin(pi*.82),-6*cos(pi*.82),.7+1.5*sin(pi*.82*.8)),(6,26,7),ease((t-96)/24))

def shot_state(t,shippos):
 k=min(int(t//12),9);u=(t-k*12)/12;e=ease(u);p=Vector(shippos)
 if k==0:return lerp((23,-40,15),(17,-32,10),e),(-2,-3,0),42
 if k==1:return tuple(p+Vector(lerp((4,-7,2.5),(-3.5,-6.8,1.4),e))),tuple(p+Vector((0,0,.1))),48
 if k==2:return lerp((1,-26,4),(4,-18,3),e),(0,0,.3),43
 if k==3:return lerp((11,-10,6),(6,-8,2),e),(0,0,0),44
 if k==4:return tuple(p+Vector(lerp((-4,-8.7,2),(4,-8,1.6),e))),tuple(p+Vector((0,-.4,.1))),46
 if k==5:return lerp((4.8,-7.5,4.4),(-4.2,-7,3.6),e),(0,0,0),40
 if k==6:
  a=-.9+e*1.2;return (15*sin(a),-15*cos(a),7-3*e),(0,0,0),42
 if k==7:return lerp((-2,-15,7),(13,-12,9),e),(0,0,0),39
 if k==8:return lerp((20,-27,12),(28,-34,17),e),(0,1,1),42
 return lerp((28,-34,17),(36,-44,22),e),(-1,2,1),42

# Bake every output frame so the .blend is entirely self-contained.
for frame in range(1,2881):
 t=(frame-1)/24;p=ship_state(t);ship.location=p
 if t<72:ship.rotation_euler=(.025*sin(t*.6),.035*sin(t*.45),.03*sin(t*.32))
 elif t<96:ship.rotation_euler=(.03,.13*sin((t-72)/24*pi),-(t-72)/24*pi*.82)
 else:ship.rotation_euler=(.08,.05,pi)
 ship.keyframe_insert('location',frame=frame);ship.keyframe_insert('rotation_euler',frame=frame)
 cl,tar,lens=shot_state(t,p);cam.location=cl;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame);cam.data.keyframe_insert('lens',frame=frame)
 # Three nested rings slowly reorient as the signal returns.
 activation=ease(max(0,min(1,(t-60)/24)))
 for i,r in enumerate(ringroots):
  r.rotation_euler=(pi/2+.28*sin(t*.05+i)*(.3+.7*activation),.3*sin(t*.07+i*2),t*(.015+i*.006)+activation*.8*(i-1))
  r.keyframe_insert('rotation_euler',frame=frame)
 heart.rotation_euler=(t*.035,t*.06,t*.02);heart.keyframe_insert('rotation_euler',frame=frame)
 heart.scale=(1+.07*activation*sin(t*2),)*3;heart.keyframe_insert('scale',frame=frame)
 for i,o in enumerate(pulses):
  phase=t-(77+i*7)
  radius=.001 if phase<0 or phase>28 else 1+phase*1.1
  o.scale=(radius,)*3;o.keyframe_insert('scale',frame=frame)
 # Material activation has a deliberate buildup rather than a sudden flash.
 for material,initial,final in [(orange,.35,3.2),(coremat,.45,4.6)]:
  inp=material.node_tree.nodes['Glow'].inputs[1];inp.default_value=initial+(final-initial)*activation;inp.keyframe_insert('default_value',frame=frame)
for ob in [ship,cam,heart]+ringroots+pulses:
 if ob.animation_data and ob.animation_data.action:
  for fc in ob.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
for i,title in enumerate(['01 | The last signal','02 | ARI-01','03 | An impossible return','04 | The relic','05 | A choice','06 | Contact','07 | Awakening','08 | The answer','09 | A new horizon','10 | Carry the light']):
 s.timeline_markers.new(title,frame=1+i*288)
s['Title']='THE LAST SIGNAL';s['Duration']='120 seconds';s['Synopsis']='A lone survey craft finds a silent orbital beacon and chooses to answer.'
s['Production']='Original procedural models, animation and music. Blender 4.3.'
s['Editorial note']='Final typography and original score are included in the packaged edit. Camera cuts at 12-second intervals.'
s.frame_set(1);s.render.filepath=os.path.join(ROOT,'frames','frame_')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'The_Last_Signal.blend'),compress=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if 'preview' in args:
 for tm in [6,18,30,42,54,66,78,90,102,114]:
  s.frame_set(int(tm*24)+1);s.render.filepath=os.path.join(ROOT,'previews','shot_%02d.png'%int(tm//12));t0=time.time();bpy.ops.render.render(write_still=True);print('SHOT',tm,'SECONDS',time.time()-t0,flush=True)
