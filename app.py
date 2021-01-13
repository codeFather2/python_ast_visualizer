from lexer import Tokenizer
from termcolor import colored

def main():
    print('AST builder/visualizer is currently under development...')
    test_file = open('testdata/lexer_test_file.py', 'r')
    tokenizer = Tokenizer(test_file.read())
    tokens, error = tokenizer.tokenize()
    if error :
        print(colored(error, 'red'))
    print(tokens)

if __name__ == "__main__":
    main()