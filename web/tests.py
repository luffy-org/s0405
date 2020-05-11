from django.test import TestCase


# Create your tests here.

# list1 = [2, 3, 5, 10, 15, 16, 18, 22, 26, 30, 32, 35, 41,
#      42, 43, 55, 56, 66, 67, 69, 72, 76, 82, 83, 88]
#
#
# def binary_search(l, aim, start=0, end=None):
#     end = len(l)-1
#     mid = int((start+end)/2)  # 求中间的数
#     if not end:
#         return '找的数不在列表里'
#     elif aim > l[mid]:
#         return binary_search(l, aim, mid+1, end)
#     elif aim < l[mid]:
#         print('aim小于l[mid]')
#         return binary_search(l, aim, start, mid-1)
#     elif aim == l[mid]:
#         print("bingo")
#         return mid
#
# ret = binary_search(list1,35)
# print(ret)







# import functools
#
# def wrapper(func):
#     @functools.wraps(func)
#     def inner(*args, **kwargs):
#         return func(*args, **kwargs)
#     return inner
#
# @wrapper
# def test():
#     pass
#
# list2 = [2, 3, 5, 10, 15, 16, 18, 22, 26, 30, 32, 35, 41,
#      42, 43, 55, 56, 66, 67, 69, 72, 76, 82, 83, 88]
#
# def binary_seach(li, val):
#     left = 0
#     right = len(li)+1
#     while left <= right:
#         mid = (left + right)//2
#         if li[mid] == val:
#             return mid
#         elif li[mid] > val:
#             right = mid -1
#
#         elif li[mid] < val:
#             left = mid + 1
#     else:
#         return None
#
# print(binary_seach(list2, 72))
# print(list2.index(72))




# print('\n'.join([' '.join(['%s * %s = %-2s' % (j, i , i*j) for j in range(1, i+1)])for i in range(1, 10)]))
















#
# l = [1,1,1,2,2,3,3,3,4,4]
#
# print(list(set(l)))
#

c = 'CN IN US'
print(c.split())
