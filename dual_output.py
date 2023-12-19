import sys
import io

class DualOutput:
    def __init__(self):
        self.console = sys.stdout
        self.capture = io.StringIO()

    def write(self, message):
        self.console.write(message)
        self.capture.write(message)
        # todo we want to check if we see start of ``` and end ``` blocks and then write to a file
        with open('log_capture_output_dj.txt', 'a') as log_file_capture_output_dj:
            log_file_capture_output_dj.write(message)

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
