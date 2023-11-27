# x = 36, y = 9
# 24bo$22bobo$12b2o6b2o12b2o$11bo3bo4b2o12b2o$2o8bo5bo3b2o$2o8bo3bob2o4b
# obo$10bo5bo7bo$11bo3bo$12b2o!
def getSequences(line):
    res = []
    seq = ""
    for el in line:
        if el == "\n":
            continue
        seq += el
        if el == "b" or el == "o":
            if len(seq) == 1:
                seq = "1" + seq
            res.append(seq)
            seq = ""
    return res

def decodeRLE(message):
    lines = message.split("$")
    answer_coordinates = []
    # print(answer_coordinates)
    x_ans = 5
    y_ans = 5
    for line in lines:
        sequences = getSequences(line)
        # print(" seq is :", sequences)
        for seq in sequences:
            if seq[-1] == "o":
                for i in range(int(seq[:-1])):
                    # print(x_ans + i, y_ans)
                    answer_coordinates.append((x_ans + i, y_ans))
            x_ans += int(seq[:-1])
        x_ans = 5
        y_ans += 1
    return answer_coordinates
