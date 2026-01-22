#!/bin/sh
#
# runai test script
# David Joffe
# ~2026-01

#reset
#clear

echo "test stdin" | runai -t hi --echo
# Specifically test with no parameters:
echo "test stdin" | runai

echo ==============================================
echo ==============================================
echo ==============================================
echo runai tests start
echo RUNAI_MODEL=$RUNAI_MODEL
echo RUNAI_TASK=$RUNAI_TASK
echo RUNAI_PROJECT=$RUNAI_PROJECT
echo RUNAI_TASKFILE=$RUNAI_TASKFILE
echo ==============================================

#python /mnt/c/runai/main.py -t test -m openai/g --echo
runai -p TESTOUT -t "hi"
runai -p TESTOUT-echo -t "hi" --echo
runai -p TESTOUT -t "hi"
runai -p TESTOUT-local -t "hi"
runai -p TESTOUT-local -t "hi" -m "ollama/deepseek-r1:8b"
runai -p TESTOUT -t "write a tiny sample Python script"
runai -p TESTOUT-local -t "write a tiny sample Python script" -m "ollama/deepseek-r1:8b"

echo runai tests done
echo DONE

#python /mnt/c/runai/main.py -t "Write a funny but cool tiny Python script" | batcat --language=python
#runai -t "Write a funny but cool useful tiny Python script" | batcat --language=python
