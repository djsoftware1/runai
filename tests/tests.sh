#!/bin/sh
#
# runai test script
# David Joffe
# ~2026-01

#reset
#clear

echo runai tests start

#python /mnt/c/runai/main.py -t test -m openai/g --echo
runai -p TESTOUT -t "hi"
runai -p TESTOUT-echo -t "hi" --echo
runai -p TESTOUT -t "hi"
runai -p TESTOUT-local -t "hi" -m "ollama/deepseek-r1:8b"
runai -p TESTOUT -t "write a tiny sample Python script"
runai -p TESTOUT-local -t "write a tiny sample Python script" -m "ollama/deepseek-r1:8b"

echo runai tests done
