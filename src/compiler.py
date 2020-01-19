from printer import Printer
from lexer import CompilerLexer
from parser import CompilerParser
import sys


class Compiler:
    lexer = None
    parser = None

    def run(self):
        self.lexer = CompilerLexer()
        self.parser = CompilerParser()
        with open(sys.argv[2], 'w') as output_file:
            Printer.init(output_file)
            with open(sys.argv[1], 'r') as input_file:
                data = input_file.read()
                self.parser.parse(self.lexer.tokenize(data))


if __name__ == '__main__':
    if len(sys.argv) == 3:
        compiler = Compiler()
        compiler.run()
