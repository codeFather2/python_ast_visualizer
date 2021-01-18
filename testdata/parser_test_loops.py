sum1 = 0
sum2 = 0

while sum1 <= countiters:
    sum2 +=1

    if sum1 == 0:
        while sum2 <= countiters:
            sum1 += 1
    elif sum1 > 1:
        if sum1 == 1:
            test_func(sum1)

return sum1 + sum2