# Google Workspace MCP — Zeno's Brief (28 November 2026)

Source: https://workspaceupdates.googleblog.com/2026/11/mcp-servers-cli-standardized-usage-tiers-now-available.html

This episode uses the original `daily_brief/assets/zeno.png`, the existing Gemini WAV cache and Manim animation pipeline. It has five custom vertical shots, not the neutral fallback.

From the repository root, first run a silent preview without paid API calls:

```powershell
$env:ZENO_SILENT = "1"
$env:ZENO_PREVIEW = "1"
try {
    uv run manim --disable_caching -p daily_brief/google_workspace_mcp.py ZenoGoogleWorkspaceMCP
} finally {
    Remove-Item Env:ZENO_SILENT, Env:ZENO_PREVIEW -ErrorAction SilentlyContinue
}
```

Then prepare narration (requires `GEMINI_API_KEY` in ignored `.env`):

```powershell
$env:ZENO_EPISODE = "daily_brief/episodes/google_workspace_mcp.json"
try {
    uv run --env-file .env python daily_brief/prepare_audio.py
} finally {
    Remove-Item Env:ZENO_EPISODE -ErrorAction SilentlyContinue
}
```

Repeat the narration preparation if the per-run quota limits new clips. Finally, render after WAV validation:

```powershell
Remove-Item Env:ZENO_SILENT, Env:ZENO_PREVIEW -ErrorAction SilentlyContinue
uv run manim --disable_caching -p daily_brief/google_workspace_mcp.py ZenoGoogleWorkspaceMCP
```

Check the narration, visual layout and mobile safe area before uploading. No actual render or audio generation was executed as part of this commit.
