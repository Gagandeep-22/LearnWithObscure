# Zeno Sensei's Brief — SWE-CoWork (24 November 2026)

**Hook/title:** AI Can Code… But Can't Finish the Job?! 🤯 #Shorts

**Source:** https://arxiv.org/abs/2611.20218 (preprint submitted 15 Nov 2026)

The research evaluates 11 AI models on 101 development assignments drawn from real repositories, within simulated engineering workplaces. The two leading models completed fewer than 8% of assignments in full. This does **not** imply every AI coding agent fails 92% of all programming tasks.

From the repository root in **PowerShell**, generate the five narration clips:

```powershell
$env:ZENO_EPISODE = "daily_brief/episodes/swe_cowork.json"
uv run --env-file .env python daily_brief/prepare_audio.py
```

Repeat only if the narration preparation reports remaining clips (successful cached clips are reused). Then render:

```powershell
Remove-Item Env:ZENO_SILENT, Env:ZENO_PREVIEW -ErrorAction SilentlyContinue
uv run --env-file .env manim --disable_caching -p daily_brief/swe_cowork.py ZenoSweCoWork
Remove-Item Env:ZENO_EPISODE -ErrorAction SilentlyContinue
```

Review final narration, timing, captions, pronunciation and safe areas before upload.

**Suggested hashtags:** #AIAgents #ArtificialIntelligence #Coding #SoftwareEngineering #TechNews #ZenoSensei #LearnWithObscure
