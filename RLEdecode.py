# x = 36, y = 9
# 24bo$22bobo$12b2o6b2o12b2o$11bo3bo4b2o12b2o$2o8bo5bo3b2o$2o8bo3bob2o4b
# obo$10bo5bo7bo$11bo3bo$12b2o!
from collections import namedtuple


x_ans = 5
y_ans = 5
answer_coordinates = []

def decodeRLE(message):
    global x_ans, y_ans
    for i in range(len(message)):
        if message[i] == "$":
            y_ans += 1
            x_ans = 5
            continue
        elif message[i].isdigit() and message[i+1].isdigit():
            x_ans += int(message[i] + message[i+1])
            continue
        elif message[i].isdigit():
            x_ans += int(message[i])
            continue
        elif message[i] == 'b' and message[i-1].isalpha():
            x_ans += 1
            continue
        elif message[i] == 'b' and message[i-1].isdigit():
            continue
        elif message[i] == 'o':
            if message[i-1].isdigit() and message[i-2].isdigit():
                for j in range(x_ans, x_ans - int(message[i-2] + message[i-1]) + 1, -1):
                    answer_coordinates.append((j, y_ans))
                    continue
            elif message[i-1].isdigit():
                answer_coordinates.append((x_ans-int(message[i-1]), y_ans))
                continue
            elif message[i-1].isalpha():
                x_ans += 1
                answer_coordinates.append((x_ans, y_ans))
                continue

decodeRLE("5b$3bob$bobob$2b2ob$5b!") 
with open("converted_pattern.txt", "w") as f:
    for x, y in answer_coordinates:
        f.write(f"{x},{y}\n")
