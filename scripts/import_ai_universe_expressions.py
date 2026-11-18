"""Split a reviewed 3-column x 2-row expression sheet into optional sprites.

Usage: uv run python scripts/import_ai_universe_expressions.py obscure sheet.png
       uv run python scripts/import_ai_universe_expressions.py zeno sheet.png
Cell order: speaking, thoughtful, surprised, blink, happy, neutral.
The neutral cell is ignored; the existing master artwork is never replaced.
"""
import argparse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "characters" / "expressions"
POSES = ("speaking", "thoughtful", "surprised", "blink", "happy")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character", choices=("obscure", "zeno"))
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    sheet = Image.open(args.sheet).convert("RGBA")
    if sheet.getchannel("A").getextrema()[0] == 255:
        parser.error("Expected a transparent PNG sheet. Do not use an opaque background.")
    tiles = []
    for i, pose in enumerate(POSES):
        col, row = i % 3, i // 3
        tile = sheet.crop((round(col * sheet.width / 3), round(row * sheet.height / 2),
                           round((col+1) * sheet.width / 3), round((row+1) * sheet.height / 2)))
        bounds = tile.getchannel("A").getbbox()
        if not bounds:
            parser.error(f"Empty cell: {pose}")
        if bounds[0] == 0 or bounds[1] == 0 or bounds[2] == tile.width or bounds[3] == tile.height:
            parser.error(f"{pose} touches the cell edge; crop or correct the sheet first.")
        path = DEST / f"{args.character}_{pose}.png"
        if path.exists() and not args.overwrite:
            parser.error(f"{path} already exists; use --overwrite only for reviewed replacement art.")
        tiles.append((tile.crop(bounds), path))
    DEST.mkdir(parents=True, exist_ok=True)
    for tile, path in tiles:
        tile.save(path)
        print(path)
    print("Review each sprite for character consistency before rendering.")

if __name__ == "__main__":
    main()
