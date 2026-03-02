#!/usr/bin/env bash
# Run the reporter Docker image with your data and get HTML + PDF in ./output.
# Prereq: build once with:  docker build -t reporter .
#
# Usage:
#   ./run-with-data.sh                    # use example data from ./data/example-licensing.json
#   ./run-with-data.sh /path/to/data.json # use your own JSON file
#   DATA_PATH=/data/foo.json ./run-with-data.sh  # same, via env
#
# Demo data (no file):  docker run --rm -v "$(pwd)/output:/output" reporter

set -e

IMAGE_NAME="${IMAGE_NAME:-reporter}"
OUTPUT_DIR="${OUTPUT_DIR:-./output}"
DATA_DIR="${DATA_DIR:-./data}"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$DATA_DIR"

# Data file: argv, or env DATA_PATH, or default example
if [[ -n "$1" ]]; then
  DATA_FILE="$1"
  if [[ -f "$DATA_FILE" ]]; then
    DATA_FILE_ABS="$(cd "$(dirname "$DATA_FILE")" && pwd)/$(basename "$DATA_FILE")"
  else
    echo "Data file not found: $DATA_FILE"
    exit 1
  fi
  MOUNT_DATA_DIR="$(dirname "$DATA_FILE_ABS")"
  DATA_PATH="/data/$(basename "$DATA_FILE_ABS")"
elif [[ -n "$DATA_PATH" ]]; then
  # Already set (e.g. /data/licensing.json); mount ./data
  MOUNT_DATA_DIR="$(cd "$DATA_DIR" && pwd)"
else
  # Default: use example file
  EXAMPLE="$DATA_DIR/example-licensing.json"
  if [[ ! -f "$EXAMPLE" ]]; then
    echo "No data file given and $EXAMPLE not found. Create it or run: ./run-with-data.sh /path/to/your.json"
    exit 1
  fi
  MOUNT_DATA_DIR="$(cd "$DATA_DIR" && pwd)"
  DATA_PATH="/data/example-licensing.json"
fi

echo "Data: $DATA_PATH (mounted from $MOUNT_DATA_DIR)"
echo "Output: $OUTPUT_DIR"

docker run --rm \
  -v "$(cd "$MOUNT_DATA_DIR" && pwd):/data:ro" \
  -v "$(cd "$OUTPUT_DIR" && pwd):/output" \
  -e "DATA_PATH=$DATA_PATH" \
  "$IMAGE_NAME"

echo "Done. Report: $OUTPUT_DIR/report.html and $OUTPUT_DIR/report.pdf"
