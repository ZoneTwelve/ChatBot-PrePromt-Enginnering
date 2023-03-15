# Define:
# Operation black: START_DELIM TOKEN END_DELIM
#  - READ: read data from user
#  - R: response to the user
# Code block: CODE_DELIM [^CODE_DELIM] CODE_DELIM

class Lexical:
    def __init__(self, start_delim, end_delim):
        self.start_delim = start_delim
        self.end_delim = end_delim
        self.buffer = ''
        self.in_block = False

    def put(self, token):
        if not self.in_block:
            if token == self.start_delim[0]:
                self.in_block = True
                self.buffer = token
        else:
            self.buffer += token
            if token == self.end_delim[-1]:
                if self.buffer.startswith(self.start_delim) and self.buffer.endswith(self.end_delim):
                    op_block = self.buffer[len(self.start_delim):-len(self.end_delim)].strip()
                    self.buffer = ''
                    self.in_block = False
                    return op_block
                else:
                    self.buffer = ''
                    self.in_block = False
        return None
