import bpy,os
p=os.path.abspath('output/The_Last_Signal.blend')
s=bpy.data.scenes['02 — Final film'];s.view_settings.view_transform='AgX'
seq=s.sequence_editor.sequences if hasattr(s.sequence_editor,'sequences') else s.sequence_editor.strips
world=seq['The complete 3D animation'];world.blend_type='ALPHA_OVER'
for f,v in [(1,0),(37,1),(2809,1),(2880,0)]:
 world.blend_alpha=v;world.keyframe_insert('blend_alpha',frame=f)
bpy.ops.wm.save_as_mainfile(filepath=p,compress=True)
print('FINAL PROJECT READY')
