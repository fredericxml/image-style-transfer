"""Run repeated inference and save generated examples."""
import argparse
from pathlib import Path
import sys
from time import perf_counter

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from test_inference import app, decode_result, fixture_image, upload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeat', type=int, default=5)
    parser.add_argument('--output', type=Path, default=ROOT / 'verification-output')
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error('--repeat must be positive')
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'content.png').write_bytes(fixture_image())
    (args.output / 'style.png').write_bytes(fixture_image(style=True))
    client = app.test_client()
    process = psutil.Process()
    workflows = {
        'style-blender': lambda: {'image_0': upload(), 'image_1': upload(style=True)},
        'cartoonize': lambda: {'image_0': upload()},
        'pencil-sketch': lambda: {'image_0': upload(), 'sharpen_factor': '4'},
    }
    def rss():
        return process.memory_info().rss / 1024**2
    print(f'Baseline RSS: {rss():.1f} MiB')
    for run in range(1, args.repeat + 1):
        for name, fields in workflows.items():
            before, start = rss(), perf_counter()
            result = decode_result(client.post('/' + name, data=fields()))
            print(f'Round {run} {name}: {perf_counter()-start:.3f}s, RSS {before:.1f} -> {rss():.1f} MiB')
            if run == 1:
                (args.output / (name + '.png')).write_bytes(result)
    print(f'Outputs: {args.output.resolve()}')


if __name__ == '__main__':
    main()
