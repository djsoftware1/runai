#!/bin/sh

runai -t "Write a Python script that implements a Lennard-Jones molecular simulation of 1000 molecules in a loop with simulation deltatime 0.002 seconds" create -o ljones.py

runai -m "gpt-5.2" -t "Write a C++ CUDA robot arm sample" --openai  create -o djrobot.cpp 

runai -m "gpt-5.2" -t "Come up with a nice list of cool ideas of things to create with runai tool from interesting technology like CUDA samples or robotics to things that make money or ideas to help cure diseases or aging .. just brainstorm" --openai

#runai --openai -t "Write #a Python script that implements a Lennard-Jones molecular simulation of 1000 molecules in a loop with simulation deltatime 0.002 seconds" create -o ljones.py

#runai -t "Writer an aider automation helper?"
#runai -t "Write a fun game"
#runai -t "Write a chtatbot"


# longevity tasks?
# 3d game? 
# 2d game?
# snake
# transformers?


