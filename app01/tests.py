# from django.test import TestCase
#
# # Create your tests here.
# import sys
# for line in sys.stdin:
#     a = line.split()
#     print(int(a[0]) + int(a[1]))


import sys
def test1(temp):
    dic={}
    flag1=False
    flag2=False
    for index,val in enumerate(temp):
        dic[index]=len(val)
    lis=[v for v in dic.values()]
    print(lis)
    set1=set(lis[::2])
    set2=set(lis[1::2])
    print(set2,set1)
    if len(set1)!=len(set2):
        flag1=True
    if len(temp[0])==len(temp[-1]) and len(set(temp[1:len(temp)-1]))==1 and set(len(temp[0]))!=set(temp[1:len(temp)-1]):
        flag2=True

    return flag2 or flag1
if __name__ == "__main__":
    ret = []
    for item in range(100):
        lines = sys.stdin.readline().strip()
        if not lines:
            break
        temp = lines.split()
        if test1(temp):
            ret.append('true')
        else:
            ret.append('false')
    print(' '.join(ret))
        # lis = []
        # lis.append(item.split())
        # print(lis)



