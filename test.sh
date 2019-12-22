#!/usr/bin/env bash

set -euo pipefail

set -x
black --check swole
mypy -p swole
python3 -m doctest swole/**/*.py
set +x
