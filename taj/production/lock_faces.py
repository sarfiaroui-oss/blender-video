import bpy,os
s=bpy.context.scene
for obj in bpy.data.objects:
 if obj.type!='MESH' or not obj.data.shape_keys:continue
 keys=obj.data.shape_keys
 if 'Blink' in keys.key_blocks:
  for fc in keys.animation_data.action.fcurves:
   if fc.data_path=='key_blocks["Blink"].value':fc.mute=True
  keys.key_blocks['Blink'].value=0
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('taj/output/Taj_Mahal_Sunset_Conversation.blend'),compress=True)
print('FINAL FACE CONTROLS LOCKED',flush=True)
