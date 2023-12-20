import sys
import io

from helper_functions import create_files_from_ai_output

class DualOutput:
    def __init__(self):
        self.console = sys.stdout
        self.capture = io.StringIO()
        self.str_total = ''

    def write(self, message):
        self.console.write(message)
        self.capture.write(message)
        # todo we want to check if we see start of ``` and end ``` blocks and then write to a file
        with open('log_capture_output_dj_full.txt', 'a') as log_file_capture_output_dj:
            log_file_capture_output_dj.write(message)
        # create_files_from_ai_output
        self.str_total = self.str_total + message
        # create_files_from_ai_output
        #create_files_from_ai_output(self.str_total, output_directory='output_files/files')


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
