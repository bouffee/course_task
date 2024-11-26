def getSequences(line):
    last_line = None
    if line[-1].isdigit():
        last_line = line[-1]
        line = line[:-1]
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
    if last_line:
        res.append(last_line)
    return res

def decodeRLE(message):
    lines = message.split("$")
    # print ("Splitted lines are: ", lines)
    answer_coordinates = []
    # print(answer_coordinates)
    x_ans = 5
    y_ans = 5
    for line in lines:
        enter_num = 1
        sequences = getSequences(line)
        # print("sequesnces are:", sequences)
        for seq in sequences:
            if seq[-1] == "o":
                for i in range(int(seq[:-1])):
                    answer_coordinates.append((x_ans + i, y_ans))
            elif seq.isdigit():
                enter_num = int(seq)
                continue
            x_ans += int(seq[:-1])
        x_ans = 5
        y_ans += enter_num
    return answer_coordinates
