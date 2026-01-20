# [runai](https://github.com/djsoftware1/runai) Talking to your computer

## Custom shell commands/integration

A small shell function is enough to create new AI-based command-line interfaces with runai:

```sh
computer() {
    runai -q -t "$*"
}
```

You can now type:

```sh
$ computer "Give me a list of the 5 closest stars!"
```

While this example is humorous, this system is powerful and extendible to many fields. 

Some more interesting examples, for other fields and more serious uses:

```
computer() {
    export RUNAI_SYSTEMPROMPT="You are the Star Trek computer integrated in a spaceship. Play along. Computer!"
    runai -p shipslog -t "$RUNAI_SYSTEMPROMPT $*"
}

longevity() {
    # select more advanced model here
    export RUNAI_MODEL="gpt-5"
    export RUNAI_SYSTEMPROMPT="You are an expert assitant specializing in longevity research, biology and clinical trials."
    runai -p longevity_out -t "$RUNAI_SYSTEMPROMPT $*"
}

lexicographer() {
 export RUNAI_SYSTEMPROMPT="You are an expert lexicographer."
 runai -p lexicographer_out -t "$RUNAI_SYSTEMPROMPT $*"
}

legal() {
 export RUNAI_SYSTEMPROMPT="You are a cautious legal assistant. Do not speculate."
 runai -p legal_out -t "$RUNAI_SYSTEMPROMPT $*"
}
'''

Place scripts like these in your startup configuration, and you can now do commands like the following, from anywhere, with customized output folder:

```sh
$ computer "earl grey, hot"

$ legal "give me a simple template NDA"

$ longevity "List top 10 associated molecules"
```
