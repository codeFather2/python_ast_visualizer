from parser_ import Parser
from lexer import Tokenizer
from termcolor import colored
from logging import getLogger, log
from visualizer import Visualizer, VisualizingMode as vis_mode
from logger import create_logger

def main():
    print('AST builder/visualizer is currently under development...')
    filename = 'testdata/parser_test_example.py'
    test_file = open(filename, 'r').read()
    logger =  create_logger()
    tokenizer = Tokenizer(test_file, logger)
    tokens, error = tokenizer.tokenize()
    if error :
        logger.error(error.__repr__)
    logger.info('Tokenization is finished.')
    parser = Parser(tokens, logger)
    result = parser.parse()
    logger.info('Parsing is finished.')
    Visualizer(result, filename, test_file).visualize(vis_mode.AST)    
    logger.info('Visualization is finished.')

if __name__ == "__main__":
    main()