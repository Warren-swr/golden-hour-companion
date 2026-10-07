"""Time-labelled contact sheets sampled from a frame directory (for editorial review)."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('output')
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int, default=1056)
    parser.add_argument('--step', type=int, default=12)
    parser.add_argument('--columns', type=int, default=6)
    parser.add_argument('--tile', type=int, default=288)
    args = parser.parse_args()
    frames = list(range(args.start, args.end + 1, args.step))
    if frames[-1] != args.end:
        frames.append(args.end)
    rows = (len(frames) + args.columns - 1) // args.columns
    sheet = Image.new('RGB', (args.columns * args.tile, rows * (args.tile + 26)), '#191c1b')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    for i, f in enumerate(frames):
        x, y = (i % args.columns) * args.tile, (i // args.columns) * (args.tile + 26)
        path = Path(args.directory) / ('frame_%04d.png' % (1 if f <= 48 else f))
        draw.text((x + 6, y + 4), '%05.2f s / frame %04d' % ((f - 1) / 24, f), font=font, fill='#ddd4bf')
        if path.exists():
            with Image.open(path) as im:
                sheet.paste(im.convert('RGB').resize((args.tile, args.tile), Image.Resampling.LANCZOS), (x, y + 26))
    sheet.save(args.output, quality=90)
    print(args.output)


if __name__ == '__main__':
    main()
