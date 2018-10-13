#filter
#只保留奇数
c=range(2,10)
def blj(para):
    return para%2==1    
print(list(filter(blj,c)))

def not_empty(s):
    return s and s.strip('')

print(list(filter(not_empty,['lkjlkj','   ','jlk', 'dasdasdkljl'])))


#求素数
def _odd_iter():
    n = 1
    while True:
        n = n + 2
        if n >1000:
            break
        yield n
#生成器 无限序列
g = _odd_iter()

def _not_divisible(n):
    return lambda x : x % n > 0

aas='abcdefghij'
print(aas[::-1])
def is_palindrome(n):
    s = str(n)
    return s == s[::-1]

print(list(filter(is_palindrome, range(1, 200))))
if list(filter(is_palindrome, range(1, 200))) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33, 44, 55, 66, 77, 88, 99, 101, 111, 121, 131, 141, 151, 161, 171, 181, 191]:
    print('测试成功!')
else:
    print('测试失败!')

