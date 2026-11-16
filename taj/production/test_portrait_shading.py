import bpy,os,time
from mathutils import Vector
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=False;s.cycles.max_bounces=1;s.cycles.diffuse_bounces=0;s.cycles.glossy_bounces=0;s.cycles.transparent_max_bounces=8;s.cycles.use_light_tree=False;s.render.use_persistent_data=True
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not bs:continue
 out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
 geo=nt.nodes.new('ShaderNodeNewGeometry');normal=bs.inputs['Normal'].links[0].from_socket if bs.inputs['Normal'].is_linked else geo.outputs['Normal']
 key=nt.nodes.new('ShaderNodeVectorMath');key.operation='DOT_PRODUCT';key.inputs[1].default_value=(-.45,-.55,.70);nt.links.new(normal,key.inputs[0])
 mx=nt.nodes.new('ShaderNodeMath');mx.operation='MAXIMUM';mx.inputs[1].default_value=0;nt.links.new(key.outputs['Value'],mx.inputs[0]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.55;nt.links.new(mx.outputs[0],mul.inputs[0]);amb=nt.nodes.new('ShaderNodeMath');amb.operation='ADD';amb.inputs[1].default_value=.58;nt.links.new(mul.outputs[0],amb.inputs[0])
 tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(1,.91,.86,1)
 if bs.inputs['Base Color'].is_linked:nt.links.new(bs.inputs['Base Color'].links[0].from_socket,tint.inputs[1])
 else:tint.inputs[1].default_value=bs.inputs['Base Color'].default_value
 # A broad, soft reflection supports eyes and the textured hair without hard highlights.
 half=nt.nodes.new('ShaderNodeVectorMath');half.operation='ADD';half.inputs[1].default_value=(-.45,-.55,.70);nt.links.new(geo.outputs['Incoming'],half.inputs[0]);norm=nt.nodes.new('ShaderNodeVectorMath');norm.operation='NORMALIZE';nt.links.new(half.outputs[0],norm.inputs[0]);spec=nt.nodes.new('ShaderNodeVectorMath');spec.operation='DOT_PRODUCT';nt.links.new(normal,spec.inputs[0]);nt.links.new(norm.outputs[0],spec.inputs[1]);cl=nt.nodes.new('ShaderNodeMath');cl.operation='MAXIMUM';cl.inputs[1].default_value=0;nt.links.new(spec.outputs['Value'],cl.inputs[0]);power=nt.nodes.new('ShaderNodeMath');power.operation='POWER';power.inputs[1].default_value=28;nt.links.new(cl.outputs[0],power.inputs[0]);specmul=nt.nodes.new('ShaderNodeMath');specmul.operation='MULTIPLY';specmul.inputs[1].default_value=.055;nt.links.new(power.outputs[0],specmul.inputs[0])
 base=nt.nodes.new('ShaderNodeEmission');nt.links.new(tint.outputs[0],base.inputs[0]);nt.links.new(amb.outputs[0],base.inputs[1]);shine=nt.nodes.new('ShaderNodeEmission');shine.inputs[0].default_value=(1,.9,.75,1);nt.links.new(specmul.outputs[0],shine.inputs[1]);add=nt.nodes.new('ShaderNodeAddShader');nt.links.new(base.outputs[0],add.inputs[0]);nt.links.new(shine.outputs[0],add.inputs[1]);nt.links.new(add.outputs[0],out.inputs['Surface'])
for tm,loc,tar in [(16,(1.6,-6.6,3.25),(2.1,0,2.38)),(24,(-1.6,-6.6,3.10),(-2.1,0,2.13)),(2,(0,-11.4,4.05),(0,.1,1.43))]:
 s.frame_set(tm*24+1);s.camera.location=loc;s.camera.rotation_euler=(Vector(tar)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=70 if tm!=2 else 46;s.render.filepath=os.path.abspath(f'taj/previews/portrait_{tm:03}.png');t=time.time();bpy.ops.render.render(write_still=True);print('PORTRAIT',tm,time.time()-t,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('taj/output/Taj_Mahal_Portrait_Lighting.blend'),compress=True)
