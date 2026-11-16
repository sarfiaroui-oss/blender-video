import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR=44100;DURATION=120;n=SR*DURATION
mix=np.zeros((n,2),dtype=np.float32)
rng=np.random.default_rng(120)
def note(m):return 440*2**((m-69)/12)
def add(sig,start,pan=0,vol=1):
 a=int(start*SR);b=min(n,a+len(sig));sig=sig[:b-a]*vol
 if b<=a:return
 mix[a:b,0]+=sig*np.sqrt((1-pan)/2);mix[a:b,1]+=sig*np.sqrt((1+pan)/2)
def pad(notes,start,dur=14):
 t=np.arange(int(dur*SR),dtype=np.float32)/SR
 env=np.minimum(1,t/2.3)*np.minimum(1,(dur-t)/3.5)
 for j,m in enumerate(notes):
  f=note(m);sig=(np.sin(2*np.pi*f*t)+.32*np.sin(2*np.pi*f*2.001*t)+.12*np.sin(2*np.pi*f*3*t))*.032*env
  sig*=.87+.13*np.sin(2*np.pi*.11*t+j)
  add(sig,start,pan=(j-1.5)*.35)
def pluck(m,start,vol=.09,pan=0,dur=3.3):
 t=np.arange(int(dur*SR),dtype=np.float32)/SR;f=note(m)
 env=(1-np.exp(-t*80))*np.exp(-t*2.1)
 sig=(np.sin(2*np.pi*f*t)+.19*np.sin(2*np.pi*f*2*t)*np.exp(-t*3)+.07*np.sin(2*np.pi*f*3*t))*env*vol
 add(sig,start,pan)
 for delay,gain in [(.375,.27),(.75,.14),(1.125,.075)]:add(sig*gain,start+delay,-pan)
chords=[[38,53,57,64],[34,50,57,60],[41,53,57,60],[36,52,55,62],[38,53,57,64],[34,50,57,60],[41,53,57,64],[36,52,55,62],[38,53,57,64],[41,53,57,60]]
for k,ch in enumerate(chords):
 pad(ch,k*12)
 # A quiet, sustained bass gives each camera shot a harmonic home.
 dur=12;t=np.arange(SR*dur,dtype=np.float32)/SR;env=np.minimum(t,1)*np.minimum(dur-t,1)
 add(np.sin(2*np.pi*note(ch[0]-12)*t)*env*.055,k*12)
 if k>=1:
  pattern=[ch[1]+12,ch[2]+12,ch[3]+12,ch[2]+12,ch[1]+24,ch[3]+12,ch[2]+12,ch[3]+12]
  for j in range(16):pluck(pattern[j%8],k*12+j*.75,vol=.034 if k<5 else .052,pan=.45*np.sin(j*1.7))
# The answer is a new, simple melody entering with the awakening.
for start,m in [(61.5,74),(63,77),(65.25,81),(68.25,79),(70.5,77),(74.25,74),(76.5,72),(79.5,69),(82.5,72),(85.5,76),(88.5,79),(91.5,77),(97.5,74),(100.5,77),(103.5,81),(108,79),(111,77),(114,72)]:
 pluck(m,start,.075,pan=-.1,dur=5)
# Low heartbeat and soft filtered noise add motion without overpowering the score.
for start in np.arange(36,106,1.5):
 t=np.arange(int(.65*SR),dtype=np.float32)/SR
 phase=2*np.pi*(42*t+30*(1-np.exp(-t*14))/14)
 add(np.sin(phase)*np.exp(-t*9)*.065,start)
for start in [25,28,31,59.5,60.25,61]:
 pluck(86 if start<40 else 81,start,.028,.55,dur=1.7)
for start in [70,82,94]:
 dur=5;t=np.arange(int(dur*SR),dtype=np.float32)/SR
 noise=rng.normal(0,1,len(t)).astype(np.float32);noise=lfilter([.025],[1,-.975],noise).astype(np.float32)
 env=np.sin(np.pi*t/dur)**2
 add(noise*env*.12,start,-.2)
# Short diffuse stereo tail. No external recordings or copyrighted music.
base=mix.copy()
for delay,atten,flip in [(.113,.16,True),(.229,.12,False),(.421,.085,True),(.683,.06,False),(1.013,.035,True)]:
 d=int(delay*SR);src=base[:-d,::-1] if flip else base[:-d];mix[d:]+=src*atten
fadein=np.minimum(np.arange(n)/(SR*3),1).astype(np.float32)
fadeout=np.minimum((n-1-np.arange(n))/(SR*6),1).astype(np.float32)
mix*=fadein[:,None]*fadeout[:,None]
peak=np.max(np.abs(mix));mix*=.86/peak
wavfile.write(os.path.join(ROOT,'output','The_Last_Signal_Original_Score.wav'),SR,(mix*32767).astype(np.int16))
print('Score:',DURATION,'seconds, stereo, peak',float(np.max(np.abs(mix))),'RMS',float(np.sqrt(np.mean(mix**2))))
