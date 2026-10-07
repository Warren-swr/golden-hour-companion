"""Readable proof sheets from actual rendered frames, without changing the art."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('output')
    parser.add_argument('--columns', type=int, default=4)
    parser.add_argument('--tile', type=int, default=440)
    args = parser.parse_args()
    files = sorted(Path(args.directory).glob('*.png'))
    if not files:
        raise SystemExit('No rendered PNG images yet')
    rows = (len(files) + args.columns - 1) // args.columns
    image = Image.new('RGB', (args.columns * args.tile, rows * (args.tile + 30)), '#191c1b')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    for i, file in enumerate(files):
        x, y = (i % args.columns) * args.tile, (i // args.columns) * (args.tile + 30)
        draw.text((x + 8, y + 6), file.stem, font=font, fill='#ddd4bf')
        with Image.open(file) as im:
            image.paste(im.convert('RGB').resize((args.tile, args.tile), Image.Resampling.LANCZOS), (x, y + 30))
    image.save(args.output, quality=94)
    print(args.output)


if __name__ == '__main__':
    main()
