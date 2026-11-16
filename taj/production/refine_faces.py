import bpy,os,time
from mathutils import Vector
s=bpy.context.scene;s.cycles.samples=8
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;out=next((n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'),None)
 if not out or not out.inputs['Surface'].is_linked:continue
 add=out.inputs['Surface'].links[0].from_node
 if add.type!='ADD_SHADER':continue
 base=add.inputs[0].links[0].from_node;shine=add.inputs[1].links[0].from_node
 rgb=nt.nodes.new('ShaderNodeMixRGB');rgb.blend_type='MULTIPLY';rgb.inputs[0].default_value=1;nt.links.new(base.inputs[0].links[0].from_socket,rgb.inputs[1]);nt.links.new(base.inputs[1].links[0].from_socket,rgb.inputs[2])
 plus=nt.nodes.new('ShaderNodeMixRGB');plus.blend_type='ADD';plus.inputs[0].default_value=1;nt.links.new(rgb.outputs[0],plus.inputs[1]);nt.links.new(shine.inputs[1].links[0].from_socket,plus.inputs[2])
 surf=nt.nodes.new('ShaderNodeEmission');surf.inputs[1].default_value=1.18;nt.links.new(plus.outputs[0],surf.inputs[0]);nt.links.new(surf.outputs[0],out.inputs['Surface'])
# Keep the original lips; the subtle jaw deformation supplies articulation.
for name in ['A — speaking mouth','C — speaking mouth']:bpy.data.objects[name].hide_render=True
# Bake more flattering portrait camera choices into the existing camera animation.
import json,math
lines=json.load(open('taj/production/dialogue_timed.json'))
shotkinds=['wide','C','A','C','A','model','A','C','A','model','A','pair','A','C']
def pose(kind,u):
 if kind=='wide':return (0,-11.4+.25*math.sin(u*math.pi),4.05),(0,.1,1.43),46
 if kind=='A':return (-1.6,-6.8+.12*u,3.1),(-2.10,0,2.12),74
 if kind=='C':return (1.6,-6.8+.12*u,3.25),(2.10,0,2.37),77
 if kind=='model':return (1.2-.7*u,-6.6,3.0),(0,.3,1.32),57
 return (0,-9.4+.1*u,3.5),(0,.1,1.76),47
for f in range(1,2881):
 t=(f-1)/24;idx=next((i for i,l in enumerate(lines) if l['start']-.25<=t<=l['end']+.4),None)
 if idx is None and 4.5<t<115:
  prior=[i for i,l in enumerate(lines) if l['end']<t];idx=prior[-1] if prior else None
 kind='wide' if idx is None else shotkinds[idx];u=t/120 if idx is None else max(0,min(1,(t-lines[idx]['start'])/(lines[idx]['end']-lines[idx]['start'])))
 loc,tar,lens=pose(kind,u);s.camera.location=loc;s.camera.rotation_euler=(Vector(tar)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens
 s.camera.keyframe_insert('location',frame=f);s.camera.keyframe_insert('rotation_euler',frame=f);s.camera.data.keyframe_insert('lens',frame=f)
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('taj/output/Taj_Mahal_Sunset_Conversation.blend'),compress=True)
for tm in [16,24,2]:
 s.frame_set(tm*24+1);s.render.filepath=os.path.abspath(f'taj/previews/face_final_{tm:03}.png');t=time.time();bpy.ops.render.render(write_still=True);print('FACE FINAL',tm,time.time()-t,flush=True)
