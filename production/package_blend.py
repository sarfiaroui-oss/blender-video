import bpy,os,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source=bpy.context.scene;source.name='01 — Animated world';source.cycles.samples=4
source.render.use_sequencer=False;source.render.filepath='//frames/frame_'
final=bpy.data.scenes.new('02 — Final film');final.render.resolution_x=1280;final.render.resolution_y=720;final.render.resolution_percentage=100
final.render.fps=24;final.frame_start=1;final.frame_end=2880
final.render.image_settings.file_format='FFMPEG';final.render.ffmpeg.format='MPEG4';final.render.ffmpeg.codec='H264';final.render.ffmpeg.constant_rate_factor='HIGH';final.render.ffmpeg.audio_codec='AAC'
final.render.filepath='//The_Last_Signal.mp4';final.render.film_transparent=False
final.view_settings.view_transform='Standard'
ed=final.sequence_editor_create()
seq=ed.sequences if hasattr(ed,'sequences') else ed.strips
strip=seq.new_scene('The complete 3D animation',source,1,1)
strip.frame_final_duration=2880
if hasattr(strip,'scene_input'):strip.scene_input='CAMERA'
snd=seq.new_sound('Original score — 120 seconds',os.path.join(ROOT,'output','The_Last_Signal_Original_Score.wav'),2,1)
# Letterbox framing.
for name,pos in [('Upper letterbox',338),('Lower letterbox',-338)]:
 bar=seq.new_effect(name,'COLOR',channel=3 if pos>0 else 4,frame_start=1,frame_end=2881)
 bar.color=(.001,.002,.004);bar.transform.scale_y=44/720;bar.transform.offset_y=pos

def title(body,start,end,size,y,name='Title',x=.5,align='CENTER'):
 a=int(start*24)+1;b=int(end*24)+1
 strip=seq.new_effect(name,'TEXT',channel=5+len([q for q in seq if q.type=='TEXT']),frame_start=a,frame_end=b)
 strip.text=body;strip.font_size=size;strip.color=(.93,.95,.96,1)
 strip.location=(x,y);strip.align_x=align;strip.align_y='CENTER';strip.use_shadow=True;strip.shadow_color=(0,0,0,.8)
 for f,v in [(a,0),(a+24,1),(b-24,1),(b,0)]:
  strip.blend_alpha=v;strip.keyframe_insert('blend_alpha',frame=f)
 return strip
# Text remains editable in the Video Sequencer.
title('A SMALL VOYAGER. AN IMPOSSIBLE ECHO.',1.5,9.8,16,.608,'Opening kicker')
title('THE LAST SIGNAL',2,10,64,.511,'Opening title')
title('A TWO-MINUTE JOURNEY',3,9.5,16,.424,'Opening subtitle')
title('ARI–01\nLONG-RANGE SURVEY',13.5,19.5,18,.82,'Craft identifier',.05,'LEFT')
for txt,a,b in [('For years, there was only silence.',25,31.5),('Then something answered.',37.5,44.5),('A small light can make a choice.',51,57.5),('And wake a sleeping universe.',80,87),('Some signals are meant to be answered.',102,109)]:
 title(txt,a,b,24,.125,'Story caption')
title('SIGNAL FOUND\nCONNECTION ESTABLISHED',62,67,18,.82,'Contact identifier',.05,'LEFT')
title('THE LAST SIGNAL',112,119,64,.528,'Closing title')
title('CARRY THE LIGHT FORWARD',113,119,16,.442,'Closing line')
readme=bpy.data.texts.new('START HERE — The Last Signal')
readme.write('THE LAST SIGNAL\n120 seconds | 1280 × 720 | 24 fps\n\nScene 01 contains the original editable 3D models, materials, rig animation, camera and ten chapter markers.\nScene 02 is the assembled film, with editable typography and the packed original soundtrack.\n\nThe delivered MP4 was rendered in Blender and finished with FFmpeg.\nThe final MP4 uses ASS typography with tracking and fades; the Blender edit preserves matching text and timing with native text strips.\nRender Scene 02 to export a new edit directly from Blender.\n\nOriginal spacecraft, beacon, planet, stars, animation and synthesized music created for this request. No downloaded models or third-party music.\n')
# Include reproducible procedural source inside the project.
for name in ['create_film.py','render.py','score.py','encode.py','titles.ass']:
 text=bpy.data.texts.new(name);text.write(open(os.path.join(ROOT,'production',name)).read())
bpy.context.window.scene=source;source.frame_set(433)
# Set a useful startup view and pack the original soundtrack.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'output','The_Last_Signal.blend'),compress=True)
print('PACKAGED',len(seq),'strips; packed sound',snd.sound.packed_file is not None,flush=True)
