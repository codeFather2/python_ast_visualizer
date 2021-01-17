from parser_ import Parser
from lexer import Tokenizer
from visualizer import Visualizer, VisualizingMode as vis_mode
from logger import create_logger

class Parameters:
    def __init__(self, file_name : str, output : str, mode: vis_mode) -> None:
        self.file_name = file_name
        self.output = output
        self.mode = mode

help_message = '''\nWelcome to AST builder/visualizer\n
supported parameters:\n
-h - print help\n
-i - input file\n
-o - output file_name (output/output by default)\n
-m - visualization mode (AST or Execution)\n
'''

def prepare_params() -> Parameters:
    from sys import argv
    file_name = ''
    output = ''
    mode = vis_mode.AST

    for i in range(len(argv)):
        if argv[i][0] == '-':
            key = argv[i][1:]
            if key == 'h':
                print(help_message)
                exit()
            if key == 'o':
                i += 1
                output = argv[i]
            elif key == 'i':
                i += 1
                file_name = argv[i]
            elif key == 'm':
                i += 1
                mode = vis_mode.AST if argv[i].lower() == 'ast' else vis_mode.EXECUTION
    return Parameters(file_name, output, mode)



def main():
    print('AST builder/visualizer is currently under development...')
    logger =  create_logger()
    try:
        params = prepare_params()
    except Exception as ex:
        logger.error(f'Something went wrong while processing parameters : {repr(ex)}')
        exit()
    input_file = open(params.file_name, 'r').read()
    tokenizer = Tokenizer(input_file, logger)
    tokens, error = tokenizer.tokenize()
    if error :
        logger.error(repr(error))
    logger.info('Tokenization is finished.')
    parser = Parser(tokens, logger)
    result = parser.parse()
    logger.info('Parsing is finished.')
    Visualizer(result, params.file_name, input_file, params.output, logger).visualize(params.mode)
    logger.info('Visualization is finished.')


if __name__ == "__main__":
    main()