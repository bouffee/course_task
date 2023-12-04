def getSequences(line):
    res = []
    seq = ""
    for el in line:
        # if el == "\n":
        #     continue
        seq += el
        if el == "b" or el == "o":
            if len(seq) == 1:
                seq = "1" + seq
            res.append(seq)
            seq = ""
    return res

def decodeRLE(message):
    lines = message.split("$")
    print ("Splitted lines are: ", lines)
    answer_coordinates = []
    # print(answer_coordinates)
    x_ans = 5
    y_ans = 5
    for line in lines:
        sequences = getSequences(line)
        for seq in sequences:
            if seq[-1] == "o":
                for i in range(int(seq[:-1])):
                    answer_coordinates.append((x_ans + i, y_ans))
            x_ans += int(seq[:-1])
        x_ans = 5
        y_ans += 1
    return answer_coordinates