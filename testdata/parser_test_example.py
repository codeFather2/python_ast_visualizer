dict_ = {
    'key' : 1,
    5+2 : 'value',
    'nested' : {
        'nested1' : test_func(),
        nested2 : nested_value
    }
}

dict_2 = {key : value, key1: value,
key3 : value}

slice_ = list_[:1]
slice_1 = list_[::1]
slice_2 = list_[0:1]
slice_2 = list_[0:]
slice_2 = list_[0:]


def test_func(count_iters):

    sum_1 = 0
    sum_2 = 0

    while sum_1 <= count_iters:
        sum_2 += 1
        
        while sum_2 <= count_iters:
            sum_1 += 1

    return sum_1 + sum_2


def test_func_1(count_iters):

    sum_1 = 0

    for i in range(count_iters):
        for j in range(count_iters):
            sum += 1
    return sum

def main():
    print(1)

hex_ = 0x1f234
bin_ = 0b101011
oct_ = 0O11740
zero = 0000000
float_ = 0.1515
float_2 = 1.1010 
sum_ = 0
j = 0
while j < 10:
    j += 1
    for i in range(b):
        if i % 2 == 1:
            print(i)
        else:
            break
    sum = 1 + j

for i in range(100):
    for j in range(100):
        print(j)
        a = 2+2*2