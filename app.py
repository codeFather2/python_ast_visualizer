from parser_ import Parser
from lexer import Tokenizer
from termcolor import colored
from logging import getLogger
from visualizer import Visualizer
from logger import create_logger

def main():
    print('AST builder/visualizer is currently under development...')
    filename = 'testdata/parser_test_loops.py'
    test_file = open(filename, 'r')
    logger =  create_logger()
    tokenizer = Tokenizer(test_file.read(), logger)
    tokens, error = tokenizer.tokenize()
    if error :
        print(colored(error, 'red'))
    parser = Parser(tokens, logger)
    result = parser.parse()
    print(result)
    Visualizer(result, filename).visualize()

if __name__ == "__main__":
    main()