class LexingError(Exception):
    def __init__(self, ex: Exception = None, index: int = 0, msg=''):
        self.original = ex
        self.index = index
        self.msg = f'LexingError ({repr(ex) + ": " + msg if ex else msg}) at position: {self.index}'
        super().__init__(self.msg)


class ParsingError(Exception):
    pass
