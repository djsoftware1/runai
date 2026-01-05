# runai Design Notes

In-progress thoughts on design

dj2026-01:
Several things to think about: re: "djUserSettings" should it exist vs "djSettings" and so on:
'user settings': Firstly what is a user anyway in this day and age? It could be an AI using this ...
So it's just 'settings' but different categories of settings .. some backend-specific like autogen settings .. some about tasks like files to send, task string, etc.
Some general settings but meant to go to in backend like say preferred model, maybe system prompt, some basic info like current date for the AI,
maybe some custom user info like the user has setup some info to prefix like their name and goals and what they want to achieve and info about their projects and so on.
Again that may or may not be a human. And some of these may be project-specific e.g. inside a ~/medical-longevity-simulator we want something differently configure to say a small local humor dictionary generator or a game project like Dave Gnukem or a game engine or someone's thesis or a commercial proposals folder or academic research project, or even runai source code itself ... we may want different default models, different styles of output (different register e.g. formal or informal, academic or business language for proposals, or specific high-quality models for say longevity research or coding tasks ... different custom prompts or system prompts specific to the project .. maybe some 'common prefix' or 'common suffix' to auto prepend or append to tasks.)
