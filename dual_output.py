# Copyright (C) 2023-2024 David Joffe / DJ Software
import sys
import io

from helper_functions import create_files_from_ai_output

class DualOutput:
    def __init__(self, outfiles_directory):
        self.console = sys.stdout
        self.capture = io.StringIO()
        self.str_total = ''
        self.str_building = ''
        self.outfiles_directory = outfiles_directory
        self.pause_capture = 0 # Whilst echo-ing our input prompt which might contain code blocks to send to the AI we don't want it auto-saving files from the code .. use this to temporarily pause optionally

    def PauseSaveFiles(self):
        self.pause_capture = 1#self.pause_capture + 1

    def UnpauseSaveFiles(self):
        #if (self.pause_capture > 0):
        self.pause_capture = 0#self.pause_capture - 1

    def write(self, message):
        self.console.write(message)
        self.capture.write(message)
        with open('log_capture_output_dj_full.txt', 'a', encoding='utf-8') as log_file_capture_output_dj:
            log_file_capture_output_dj.write(message)
        with open(self.outfiles_directory+'/dj_log_capture_output.txt', 'a', encoding='utf-8') as log2:
            log2.write(message)

        # full log string of all output from AI
        self.str_total = self.str_total + message

        # Try already save code blocks returned 'so far', to files, and then clear the string
        # so we can see and maybe use or evaluate the files as quick as possible already
        # notwithstanding they may be non-final from AI agents hence maybe still have errors while task runs

        # Here we check if we see start of ``` and end ``` blocks and then write to a file
        # by using create_files_from_ai_output() which returns whether it saved code blocks
        # as it returns an array of filenames it created

        # Compile partial string so far, to check for code blocks ..
        # if we parse out code blocks to files then clear the already done saved code blocks by clearing string
        # str_building meaning we are building up a string of code blocks to save to files
        if self.pause_capture == 0:
            self.str_building = self.str_building + message
            ret_created_files = create_files_from_ai_output(self.str_building, self.outfiles_directory)
            # if we saved code blocks to files then clear the already done saved code blocks by clearing string
            if len(ret_created_files) > 0:
                self.str_building = ''


    def getvalue(self):
        return self.capture.getvalue()

    def flush(self):
        self.console.flush()
        self.capture.flush()

# Usage
#if __name__ == "__main__":
#    # Redirect output to both console and StringIO
#    dual_output = DualOutput()
#    sys.stdout = dual_output
#
#    # Example: Print statements to demonstrate real-time output and capturing
#    print("This will be printed to console and captured.")
#    print("Another line for demonstration.")
#
#    # Reset stdout to original and get captured output
#    sys.stdout = dual_output.console
#    captured_output = dual_output.getvalue()
#
#    print("\nCaptured Output:")
#    print(captured_output)
