#!/bin/sh
#
# runai test script
# David Joffe
# ~2026-01

#reset
#clear

echo runai tests start

export RUNAI_MODEL="lmstudio/stable-code-3b"
export RUNAI_MODEL="ollama/llava:7b"
export RUNAI_MODEL="ollama/deepseek-r1:8b"

runai -p TESTOUT-local - t "hi" -m "$RUNAI_MODEL"
runai -p TESTOUT-local -t "hi lmstudio stable-code!" -m "$RUNAI_MODEL"
runai -p TESTOUT-local -t "write a small but useful powerful sample Python script" -m "$RUNAI_MODEL"

echo runai tests done
