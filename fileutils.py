'''
遇到问题没人解答？小编创建了一个Python学习交流QQ群：857662006
寻找有志同道合的小伙伴，互帮互助,群里还有不错的视频学习教程和PDF电子书！
'''
# coding:utf-8

file_dict = {}


# file => dict
def file_read():
    with open('user.txt') as f:
        for line in f.read().split('\n'):
            if line:
                tmp = line.split(':')
                file_dict[tmp[0]] = tmp[0]

    return file_dict


# ditc => file
def file_write():
    file_arr = []
    for user, pwd in file_dict.items():
        file_arr.append('%s:%s' % (user, pwd))

    print(file_arr)
    with open('user.txt', 'w') as f:
        f.write('\n'.join(file_arr))


if __name__ == "__main__":
    print(file_read())
    file_write()