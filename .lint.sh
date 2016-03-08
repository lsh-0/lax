#!/bin/bash
set -e
pylint -E ./src/publisher/** --load-plugins=pylint_django --disable=E1103
echo "* passed linting"
