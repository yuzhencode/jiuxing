from functools import cmp_to_key

def abssort(arr):
    arr.sort(key=cmp_to_key(compare))
    return arr

def compare(a,b):
    if abs(a) < abs(b):
        return -1
    if abs(a) > abs(b):
        return 1
    if a < b:
        return -1
    if a < b:
        return 1
    return 0





if __name__ == '__main__':
    arr=[2, -7, -2, -2, 0]
    ar = abssort(arr)
    print(ar)