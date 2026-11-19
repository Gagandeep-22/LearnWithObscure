# Zeno's Brief: Anthropic IPO

Research date: 20 November 2026 IST. IPO priced 18 November; Nasdaq debut 19 November.
Sources:
- https://www.reuters.com/business/finance/anthropics-historic-debut-put-ais-promise-peril-wall-st-test-2026-11-19/
- https://live.euronext.com/en/financial-news/anthropic-valued-15-trillion-ipo-raises-record-81-billion
- https://ipo.anthropic.com/documents/us/prospectus.pdf (preliminary prospectus, November 10; not final pricing)

Use $81.3B as gross offering size, not net proceeds or market cap. $83 is the IPO price, not the trading price. Recheck closing status before publication.

From repository root (PowerShell):
```powershell
$env:ZENO_EPISODE = "daily_brief/episodes/anthropic_ipo.json"
$env:ZENO_TTS_MODEL = "gemini-3.8-flash-tts"
$env:ZENO_TTS_VOICE = "Leda"
uv run --env-file .env python daily_brief/prepare_audio.py --max-new 7 --interval 65
Remove-Item Env:ZENO_PREVIEW, Env:ZENO_SILENT, Env:ZENO_AUDIO -ErrorAction SilentlyContinue
uv run manim --disable_caching -p daily_brief/anthropic_ipo.py ZenoAnthropicIPO
```
Uses original mascot and silent visual transitions, with 0.3 seconds extra per beat for separation. Generated audio may still contain unwanted artifacts; listen before publishing. No live audio or render tested. Silent timing estimate 55.1 seconds; final timing depends on WAV durations. The model override matches episode 2 and does not affect AI Universe. 
