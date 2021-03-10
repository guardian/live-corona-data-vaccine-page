def numberFormat(num):
    if num > 0:
        if num > 1000000000:
            return str(round(num/ 1000000000, 1) ) + "bn"
        if num > 1000000:
            return str(round(num/ 1000000, 1)) + "m"
        if num > 1000:
            return str(round(num/ 1000, 1)) + "k"
        if num % 1 != 0:
            return str(round(num, 2))
        else:
            return str(num)

    if num < 0:
        posNum = num * -1
        if posNum > 1000000000:
            return "-" + str(round(posNum / 1000000000, 1)) + "bn"
        if posNum > 1000000:
            return "-" + str(round(posNum / 1000000, 1)) + "m"
        if posNum > 1000:
            return "-" + str(round(posNum / 1000, 1)) + "k"
        if posNum % 1 != 0:
            return str(round(posNum, 1))
        else:
            return "-" + str(posNum)