#!/usr/bin/env python3
"""Generate local Turkish Pocket TTS narration and fit cues to their time slots."""
from pathlib import Path
import argparse, math, subprocess, tempfile, wave
import numpy as np
from pocket_tts_turkish import TurkishTTS, save_wav
import torch
RATE=48000
def read_tones(path,n):
 if path is None:return [('male_1','sakin',0)]*n
 vals=[]
 for line in path.read_text(encoding='utf8').splitlines():
  if not line.strip() or line.lstrip().startswith('#'):continue
  speaker,tone,seed=line.split(); vals.append((speaker,tone,int(seed)))
 if len(vals)!=n or any(not 0<=d<=2**31-2 for _,_,d in vals):
  raise ValueError('Provide a voice, tone and integer seed per line.')
 return vals
def read_wav(path):
 with wave.open(str(path),'rb') as w:return w.getnframes(),w.getframerate(),w.readframes(w.getnframes())
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('script',type=Path);p.add_argument('ends',type=Path);p.add_argument('output',type=Path)
 p.add_argument('--tones',type=Path);p.add_argument('--model',required=True,type=Path);p.add_argument('--threads',type=int,default=2)
 a=p.parse_args()
 text=[l.strip() for l in a.script.read_text(encoding='utf8').splitlines() if l.strip()]
 ends=[float(k)for k in a.ends.read_text().replace(',',' ').split()]
 prev=[0]+ends[:-1]
 if not text or len(text)!=len(ends) or any(not math.isfinite(y) or y-x<.5 for x,y in zip(prev,ends)):p.error('Need one increasing cue end per line.')
 if a.output.exists():p.error('Output already exists.')
 tones=read_tones(a.tones,len(text))
 torch.set_num_threads(a.threads)
 torch.set_num_interop_threads(1)
 model=TurkishTTS.from_pretrained(a.model,device='cpu')
 parts=[]
 with tempfile.TemporaryDirectory(prefix='seslen-preview-') as tmp:
  for i,(line,lo,hi,(voice,tone,strength)) in enumerate(zip(text,prev,ends,tones),1):
   raw=Path(tmp)/'raw.wav'; fitted=Path(tmp)/'fit.wav'
   def say(value,who=voice,how=tone):
    return np.asarray(model.generate(value,voice=who,emotion=None if how=='notr' else how,seed=int(strength)+i,sentence_gap_ms=175),dtype=np.float32)
   y=say(line)
   if len(y)/model.sample_rate > (hi-lo-.23)*1.32 and tone!='notr':
    n1=say(line,voice,'notr')
    if len(n1)<len(y):y=n1
   if not np.isfinite(y).all() or not np.any(np.abs(y)>.004):raise ValueError(f'No valid speech for cue {i}.')
   nz=np.flatnonzero(np.abs(y)>.003)
   y=y[max(0,nz[0]-300):min(len(y),nz[-1]+851)]
   save_wav(str(raw),y,model.sample_rate)
   frames,sr,_=read_wav(raw)
   cap=round(hi*RATE)-round(lo*RATE)
   intro=round(RATE*.075)
   speed=max(.97,frames/sr/(cap/RATE-.22))
   if speed>1.42:raise ValueError(f'Cue {i} speech needs {speed:.2f}x; revise the cue timing or choose another tone.')
   gain=-1.8 if voice=='female_2' else 0.
   af=f'atempo={speed:.6f},highpass=f=72,loudnorm=I=-17:TP=-2:LRA=9,volume={gain}dB'
   subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(raw),'-af',af,'-ar','48000','-ac','1','-c:a','pcm_s16le',str(fitted)],check=True)
   n,rate,pcm=read_wav(fitted)
   if n+intro>cap or rate!=RATE:raise ValueError(f'Cue {i} overflow ({n+intro} vs {cap} samples).')
   parts.append(bytes(2*intro)+pcm+bytes(2*(cap-intro-n)))
   print(f'{i}: {lo:.2f}–{hi:.2f}, {voice}/{tone}, speech {n/RATE:.2f}s, {speed:.2f}x',flush=True)
 with a.output.open('xb') as dst,wave.open(dst,'wb') as w:
  w.setparams((1,2,RATE,0,'NONE','not compressed'));w.writeframes(b''.join(parts))
if __name__=='__main__':main()
