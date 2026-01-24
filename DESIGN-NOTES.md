# runai Design Notes

## OpenAI-compatible backends

Note many models are OpenAI-compatible and these may be routed to the OpenAI backend if no backend specified (see OPENAI_COMPATIBLE var).

## Important for security:

All code relating to displaying model_spec should never 'print' it directly, if you must show it, use show_setting() helper so that it auto-hides sensitive keys.

In-progress thoughts on design

## SETTINGS

* NB: `show_setting()` helper may seem cosmetic, but it gives us not just things like coloring, but also critical things like hiding sensitive user API keys from the output! So when coding and displaying settings, use it, don't just dump settings to screen with e.g. print etc.

dj2026-01:
Several things to think about: re: "djUserSettings" should it exist vs "djSettings" and so on:
'user settings': Firstly what is a user anyway in this day and age? It could be an AI using this ...
So it's just 'settings' but different categories of settings .. some backend-specific like autogen settings .. some about tasks like files to send, task string, etc.
Some general settings but meant to go to in backend like say preferred model, maybe system prompt, some basic info like current date for the AI,
maybe some custom user info like the user has setup some info to prefix like their name and goals and what they want to achieve and info about their projects and so on.
Again that may or may not be a human. And some of these may be project-specific e.g. inside a ~/medical-longevity-simulator we want something differently configure to say a small local humor dictionary generator or a game project like Dave Gnukem or a game engine or someone's thesis or a commercial proposals folder or academic research project, or even runai source code itself ... we may want different default models, different styles of output (different register e.g. formal or informal, academic or business language for proposals, or specific high-quality models for say longevity research or coding tasks ... different custom prompts or system prompts specific to the project .. maybe some 'common prefix' or 'common suffix' to auto prepend or append to tasks.)

### Preferred model idea:

Want to expand on this but the model selection: I am still thinking about whether this should act like 'force model' or have a separate 'force model' option or something ... maybe sometimes user want or need to force a specific model ... but maybe sometimes it should just be a soft preference with fallbacks.

For example for certain demanding, commercial tasks one may want to force and make sure we are using high-quality particular models. But for other types we may prefer either certain local models or even a list of models in order of preference to fall back on, or something, or a way to specify or list or get available models like query ollama or LM studio etc. ...

One thing that feels odd is the idea of backend-specific settings design-wise a generic core 'settings' should it 'know about' things like highly-autogen-specific settings?


## BACKEND ARCHITECTURE

There is a generic backend class from which backend instances derive. That's all fine and well and good. And there is a 'selected backend' which 'for now is fine and well and good.

But in fact the idea and intention is to extend this to support multiple backends potentially. So for example, you might want to say "generate a dictionary" with these 3 backends or models and compare the output. Or ask say a question about physics to multiple backends at once, comparing the output. And so on.

With the current design, this may not even be too difficult ... the backend selector has an array of instantiated backends which at time of writing simply just has one, but could be expanded to allow a list of backends.


### "selected backend" vs preferred backends or multi backends etc.

settings_default_backend='openai'

Things like above could also become fallback lists? Say for a 'stress-testing' folder we might want it to be either 'dummy' or 'dummy,djchat,autogen,openai' (or whatever) but if some of those not available - either for multiple, or, cascading fallback preference. So if djchat and autogen not available we end up with two available in above case. For a real project it might be something like, hmm, 'openai,claude'

fix immediately aider
also could help batch test and or more :
printf "\n--dummy\n--echo\n--openai \ndjchat\nautogen\nollama(infuture)" | runai -t "test task "

printf "\
--dummy
--echo
--openai
djchat
autogen
ollama
" | runai -t "test task"

-----

Another idea for runai code tasks: "Scan this code for todo's that are maybe not implemenetd and make a list, turn them into task strings

i can even find my own old TODOs i forgot :) automate the task of turning them into task strings, creating feedback loops 
debug and verbosity are not the same thing. local-only dev config is a way i handled things in PHP where we had live, local etc.

ok, one more idea i thinking like --dummy and --echo ... the testing or stress-test should have a mode where the dummy raises exceptions to fake errors like 'no credits ' or 404 not found sitautions causing problems or other bad things? so we can test auto-recoverying from bad stuff 
what if we add a UI or would that be a separate package? probably .. a layer above .. ? i am busy refactoring with the idea that most the REAL functionality should be in re-usable "run_ai" layer, and main.py a more thin wrapper
