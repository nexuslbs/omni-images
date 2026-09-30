#!/usr/bin/env python3
"""Minimal faster-whisper transcription CLI: the image's `whisper` command.

faster-whisper ships no command line entry point, and openai-whisper would pull
torch (~2 GB) into this thin image. This wrapper uses the faster_whisper package
already installed in the image instead.

Usage:
  whisper --help
  whisper AUDIO [--model SIZE] [--language LANG]

The transcription text is written to stdout, one segment per line.
"""

import argparse
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="whisper",
        description=(
            "Transcribe an audio/video file with faster-whisper (CPU) and "
            "print the text to stdout."
        ),
    )
    parser.add_argument("audio", metavar="AUDIO", help="audio/video file to transcribe")
    parser.add_argument(
        "--model",
        default="tiny",
        metavar="SIZE",
        help="faster-whisper model size, e.g. tiny/base/small (default: tiny)",
    )
    parser.add_argument(
        "--language",
        default=None,
        metavar="LANG",
        help="optional ISO language code passed to the model",
    )
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    # Imported after argument parsing so `whisper --help` answers quickly and
    # does not need the model cache.
    from faster_whisper import WhisperModel

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(args.audio, language=args.language)
    for segment in segments:
        text = segment.text.strip()
        if text:
            print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
