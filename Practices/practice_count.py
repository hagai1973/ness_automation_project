str = "aaabbbbbbbbbcccccccccddddddddddeeeeeeeeee"

counter = {}

for char in str:
    if char in counter:
        counter[char] += 1
    else:        
        counter[char] = 1
        
print(counter)