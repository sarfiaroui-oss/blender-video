import json,subprocess,math
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly,lfilter
ROOT=Path(__file__).resolve().parent.parent
lines=json.loads((ROOT/'production/dialogue_raw.json').read_text());gap=.65;start=4.5
rate=sum(x['raw_duration'] for x in lines)/(110-gap*(len(lines)-1))
SR=44100;audio=np.zeros((SR*120,2),dtype=np.float32)
for i,line in enumerate(lines):
 path=ROOT/'audio'/f'timed_{i:02}.wav'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(ROOT/'audio'/f'line_{i:02}.wav'),'-af',f'atempo={rate:.8f},highpass=f=70,afade=t=in:d=0.025','-ar',str(SR),str(path)],check=True)
 sr,a=wavfile.read(path);a=a.astype(np.float32)/32768
 peak=np.max(abs(a));a=a/(peak+1e-9)*.72
 begin=int(start*SR);end=begin+len(a);pan=-.12 if line['speaker']=='A' else .12
 audio[begin:end,0]+=a*np.sqrt((1-pan)/2);audio[begin:end,1]+=a*np.sqrt((1+pan)/2)
 line['start']=start;line['end']=end/SR;line['voice_model']='en_US-amy-medium' if line['speaker']=='A' else 'en_US-lessac-medium';start=end/SR+gap
 # Speech envelope for geometry-driven mouth movement, sampled at output frame rate.
 samples=[]
 for frame in range(2880):
  t=frame/24;idx=int((t-line['start'])*SR);chunk=a[max(0,idx):max(0,idx)+int(.04*SR)] if 0<=idx<len(a) else np.zeros(1)
  samples.append(float(min(1,np.sqrt(np.mean(chunk**2))*8)))
 line['envelope']=samples
# A quiet original meadow atmosphere: filtered breeze, sparse bird-like chirps and airy chords.
rng=np.random.default_rng(24);n=len(audio);t=np.arange(n,dtype=np.float32)/SR
for ch in [0,1]:
 noise=rng.normal(0,1,n).astype(np.float32);wind=lfilter([.008],[1,-.992],noise).astype(np.float32)
 audio[:,ch]+=wind*.026*(.65+.35*np.sin(t*.17+ch))
for sec,freq in [(1.6,2100),(3.2,2500),(21,2350),(43,1900),(67,2450),(91,2200),(116,2300)]:
 tt=np.arange(int(.22*SR))/SR;sig=np.sin(2*np.pi*(freq*tt+550*tt**2))*np.sin(np.pi*tt/.22)**2*.007
 idx=int(sec*SR);audio[idx:idx+len(sig),0]+=sig;audio[idx:idx+len(sig),1]+=sig*.6
for base in [146.83,220,293.66,369.99]:
 pad=np.sin(2*np.pi*base*t)*.0025*(.75+.25*np.sin(t*.12));audio[:,0]+=pad;audio[:,1]+=np.sin(2*np.pi*base*1.0006*t)*.0025
fade=np.minimum(t/1.5,1)*np.minimum((120-t)/3,1);audio*=fade[:,None]
# Preserve headroom for AAC encoding.
audio*=.85/(np.max(np.abs(audio))+1e-9)
wavfile.write(ROOT/'output'/'Taj_Mahal_ONNX_Dialogue.wav',SR,(audio*32767).astype(np.int16))
(ROOT/'production'/'dialogue_timed.json').write_text(json.dumps(lines))
summary=[{k:v for k,v in x.items() if k!='envelope'} for x in lines]
(ROOT/'production'/'dialogue_timing_readable.json').write_text(json.dumps(summary,indent=2))
print('Dialogue ends at',lines[-1]['end'],'seconds; tempo',rate,'peak',np.max(abs(audio)),flush=True)
