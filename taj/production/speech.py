import os,sys,json,wave,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runtime'))
from piper import PiperVoice,SynthesisConfig
voices={'A':PiperVoice.load(str(ROOT/'voices/en_US-amy-medium.onnx')),'C':PiperVoice.load(str(ROOT/'voices/en_US-lessac-medium.onnx'))}
lines=json.loads((ROOT/'production/dialogue.json').read_text())
(ROOT/'audio').mkdir(exist_ok=True)
for i,line in enumerate(lines):
 out=ROOT/'audio'/f'line_{i:02}.wav'
 with wave.open(str(out),'wb') as w:voices[line['speaker']].synthesize_wav(line['text'],w,syn_config=SynthesisConfig(length_scale=1.06,noise_scale=.55,noise_w_scale=.7,normalize_audio=True))
 with wave.open(str(out),'rb') as w:line['raw_duration']=w.getnframes()/w.getframerate()
 print(i,line['speaker'],round(line['raw_duration'],2),flush=True)
(ROOT/'production/dialogue_raw.json').write_text(json.dumps(lines,indent=2))
print('Total spoken duration',sum(l['raw_duration'] for l in lines),'words',sum(len(l['text'].split()) for l in lines),flush=True)
