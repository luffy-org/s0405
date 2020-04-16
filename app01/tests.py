from django.test import TestCase

# Create your tests here.

# a = '\n'.join([' '.join(['%s * %s = %-2s' % (j, i, i*j) for j in range(1, i+1)])for i in range(1, 10)])
# # print(a)
def num():
    return [lambda x:i*x for i in range(4)]
print([m(2) for m in num()])