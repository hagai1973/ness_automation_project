li1 = [9, 1, 2,22, 3, 40, 5]

max_number = li1[0]

str = "ABCDEFG"
print(str[::-1])


for i in range(len(li1)-1):
    if max_number < li1[i+1]:
        max_number = li1[i+1]


print(max_number)