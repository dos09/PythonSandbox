
if __name__ == '__main__':
    arr = '20 7 8 2 5'.split()
    index = 0
    arr = sorted(
        [(index, int(value)) 
        for index, value in enumerate(arr)],
        key=lambda x: x[1],
        reverse=True
    )
    res = 999999999999
    arr_len = len(arr)
    for i in range(arr_len):
        index, value = arr[i]
        for j in range(i + 1, arr_len):
            inner_index, inner_value = arr[j]
            if index < inner_index:
                r = value - inner_value
                if r > 0 and r < res:
                    res = r

                break
    print(res)
