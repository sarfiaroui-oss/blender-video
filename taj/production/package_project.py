import bpy,os,json,textwrap
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source=bpy.context.scene;source.name='01 — Characters and sunset';source.render.use_sequencer=False;source.render.filepath='//frames/frame_';source.render.image_settings.file_format='PNG';source.render.image_settings.color_mode='RGB';source.render.fps=24;source.frame_end=2880
final=bpy.data.scenes.new('02 — Final film with dialogue');final.render.resolution_x=1280;final.render.resolution_y=720;final.render.resolution_percentage=100;final.render.fps=24;final.frame_start=1;final.frame_end=2880;final.view_settings.view_transform='AgX'
final.render.image_settings.file_format='FFMPEG';final.render.ffmpeg.format='MPEG4';final.render.ffmpeg.codec='H264';final.render.ffmpeg.audio_codec='AAC';final.render.ffmpeg.constant_rate_factor='HIGH';final.render.filepath='//Taj_Mahal_Sunset_Conversation.mp4'
ed=final.sequence_editor_create();seq=ed.sequences if hasattr(ed,'sequences') else ed.strips
movie=seq.new_scene('Animated scene',source,1,1);movie.frame_final_duration=2880;movie.scene_input='CAMERA';movie.blend_type='ALPHA_OVER'
for f,v in [(1,0),(25,1),(2821,1),(2880,0)]:movie.blend_alpha=v;movie.keyframe_insert('blend_alpha',frame=f)
snd=seq.new_sound('Two ONNX voices and original meadow ambience',os.path.join(R,'output','Taj_Mahal_ONNX_Dialogue.wav'),2,1)
for ch,pos in [(3,344),(4,-344)]:
 o=seq.new_effect('Cinematic framing','COLOR',channel=ch,frame_start=1,frame_end=2881);o.color=(.006,.006,.006);o.transform.scale_y=32/720;o.transform.offset_y=pos
count=0
def text(body,a,b,size,y,name):
 global count
 count+=1;f1=int(a*24)+1;f2=int(b*24)+1;o=seq.new_effect(name,'TEXT',channel=4+count,frame_start=f1,frame_end=f2);o.text=body;o.font_size=size;o.color=(.98,.96,.91,1);o.location=(.5,y);o.align_x='CENTER';o.align_y='CENTER';o.use_shadow=True;o.shadow_color=(0,0,0,.9)
 for f,v in [(f1,0),(min(f1+6,f2-1),1),(max(f1+1,f2-6),1),(f2,0)]:o.blend_alpha=v;o.keyframe_insert('blend_alpha',frame=f)
text('TAJ MAHAL',.5,4.1,65,.59,'Film title');text('A SUNSET CONVERSATION',.9,4.1,18,.50,'Film subtitle')
lines=json.load(open(os.path.join(R,'production','dialogue_timing_readable.json')))
for line in lines:
 words=line['text'].split();chunks=[];chunk=[]
 for w in words:
  if len(' '.join(chunk+[w]))>100:chunks.append(chunk);chunk=[]
  chunk.append(w)
 if chunk:chunks.append(chunk)
 total=sum(len(c) for c in chunks);cursor=line['start']
 for ch in chunks:
  dur=(line['end']-line['start'])*len(ch)/total;body='\n'.join(textwrap.wrap(' '.join(ch),55));text(body,cursor,cursor+dur,23,.11,'Character '+line['speaker']+' subtitle');cursor+=dur
text('A STORY WORTH PRESERVING',115.2,119.4,24,.56,'Closing thought');text('BLENDER ANIMATION / ONNX VOICES',116,119.4,16,.49,'Closing credit')
readme=bpy.data.texts.new('START HERE — Taj Mahal film')
readme.write('TAJ MAHAL — A SUNSET CONVERSATION\nDuration: 120 seconds. Delivery: 1280 × 720 MP4 with stereo ONNX dialogue.\n\nScene 01 contains your two supplied characters and supplied Taj Mahal model. The environment uses a clean generated background plate based on your screenshot, with additional 3D foreground flowers and a display plinth.\nScene 02 contains the assembled movie, editable text strips, and packed dialogue soundtrack. Render this scene for a new full-frame Blender export.\n\nFaces: original face textures and character identity preserved; smoother geometry; soft portrait shading; restrained jaw movement, head motion and eye highlights. Character A retains its supplied idle rig. Character C uses new gesture and expression shape keys; experimental blink controls are retained but muted to preserve the facial appearance. These are approximate speaking motions, not phoneme-specific facial capture.\n\nVoice generation: Piper with ONNX Runtime, en_US-amy-medium and en_US-lessac-medium. Two generic synthetic voices. Generated speech is paced to the 120-second edit.\n\nThe delivered MP4 uses 12 rendered 3D frames per second and frame blending to 24 fps. The editable timeline is native 24 fps and can render every frame. Final typography was finished with FFmpeg; the project includes editable matching native text strips.\n\nOriginal model archives remain unchanged. The historical sources and voice model cards are included as text blocks.\n')
for folder,names in [('production',['dialogue_timing_readable.json','sources.txt','titles.ass','create_scene.py','test_portrait_shading.py','refine_faces.py','eye_polish.py','final_face_fix.py','render_final.py','encode.py']),('voices',['amy_MODEL_CARD.txt','lessac_MODEL_CARD.txt'])]:
 for name in names:
  path=os.path.join(R,folder,name)
  if os.path.isfile(path):t=bpy.data.texts.new(name);t.write(open(path).read())
bpy.context.window.scene=source;source.frame_set(577)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'output','Taj_Mahal_Sunset_Conversation.blend'),compress=True)
print('PROJECT PACKED',len(seq),'strips; audio packed',bool(snd.sound.packed_file),flush=True)
