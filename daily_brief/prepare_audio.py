"""Generate only missing/changed narration clips using Gemini TTS."""
import argparse, hashlib, json, os, time, wave
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT.parent / '.env')
p=argparse.ArgumentParser(); p.add_argument('--max-new',type=int,default=8); p.add_argument('--interval',type=float,default=22); args=p.parse_args()
if args.interval<20 or args.max_new<1: p.error('Use interval >=20 and max-new >=1')
ep=json.loads(Path(os.getenv('ZENO_EPISODE',str(ROOT/'episode.json'))).read_text(encoding='utf-8'))
model=os.getenv('ZENO_TTS_MODEL','gemini-3.1-flash-tts-preview'); voice=os.getenv('ZENO_TTS_VOICE','Leda')
out=ROOT/'audio'/ep['id']; out.mkdir(parents=True,exist_ok=True)
client=None; generated=0; last=0
for i,s in enumerate(ep['segments']):
    wav=out/f'{i:02d}.wav'; stamp=wav.with_suffix('.sha256'); key=hashlib.sha256(f'{model}:{voice}:{s["speech"]}'.encode()).hexdigest()
    if wav.exists() and stamp.exists() and stamp.read_text()==key: print('Cached:',wav.name); continue
    # Invalidate stale audio before rendering or resuming.
    wav.unlink(missing_ok=True); stamp.unlink(missing_ok=True)
    if generated>=args.max_new: continue
    if client is None: client=genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    time.sleep(max(0,args.interval-(time.monotonic()-last))); last=time.monotonic()
    response=client.models.generate_content(model=model,contents=s['speech'],config=types.GenerateContentConfig(response_modalities=['AUDIO'],speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)))))
    data=next(part.inline_data.data for part in response.candidates[0].content.parts if part.inline_data and part.inline_data.data)
    temp=wav.with_suffix('.tmp')
    with wave.open(str(temp),'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(24000); f.writeframes(data)
    temp.replace(wav); stamp.write_text(key); generated+=1; print('Generated:',wav.name)
remaining=sum(not (out/f'{i:02d}.wav').exists() for i in range(len(ep['segments'])))
print(f'New clips: {generated}; remaining: {remaining}.')
