
a = [1,2,3]
b= [1, 2, 3]

for index, (a_i, b_i) in enumerate(zip(a, b)):
    print(index+10, a_i, b_i)