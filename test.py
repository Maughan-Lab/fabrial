x = 1
proceed = True

while x < 10 and proceed:
    x += 1
    if x == 5:
        proceed = False
    if x % 2 == 0 or x == 5:
        continue
    print(x)
