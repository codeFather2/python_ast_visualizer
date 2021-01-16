class TextSpan:
    def __init__(self, begin: int, length : int) -> None:
        self.begin = begin
        self.length = length
        self.end = begin + length

    def __str__(self) -> str:
        return f'[{self.begin}..{self.end}]'

    def __repr__(self) -> str:
        return self.__str__()



def union_spans(s1: TextSpan, s2: TextSpan) -> TextSpan:
    begin = s1.begin if s1.begin < s2.begin else s2.begin
    end = s1.end if s1.end > s2.end else s2.end

    return TextSpan(begin, end - begin)