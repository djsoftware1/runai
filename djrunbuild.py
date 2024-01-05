# Copyright (C) 2023-2024 David Joffe
import os

# Configure build command and build folder
build_command = "your_build_command"
build_folder = "your_build_folder"

# Run build command
os.system(f"cd {build_folder} && {build_command}")

# Check build logs for errors
log_file = os.path.join(build_folder, "build.log")
with open(log_file, "r") as f:
    logs = f.read()

if "error" in logs.lower():
    print("Errors found in the build logs.")
else:
    print("No errors found in the build logs.")

import os

# Configure build command and build folder
build_command = "your_build_command"
build_folder = "your_build_folder"

# Run build command
os.system(f"cd {build_folder} && {build_command}")

# Check build logs for errors
log_file = os.path.join(build_folder, "build.log")
with open(log_file, "r") as f:
    logs = f.read()

# Hm this isn't right if the log says "0 errors" it will say there are errors:
# More importantly we want also AI to potentially check error logs
if "error" in logs.lower():
    print("Errors found in the build logs.")
else:
    print("No errors found in the build logs.")
