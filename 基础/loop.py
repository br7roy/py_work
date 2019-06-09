#Python的循环有两种
#一种是for...in循环，依次把list或tuple中的每个元素迭代出来，看例子：
names = ['Michael', 'Bob', 'Tracy']
for name in names:
    print(name)
#计算1-10的整数之和
sums = [1,2,3,4,5,6,7,8,9,10]
total = 0;
for sum in sums:
    total +=sum;
    pass;
print(total)
#如果要计算1-100的整数之和，从1写到100有点困难，
#幸好Python提供一个range()函数，可以生成一个整数序列，
#再通过list()函数可以转换为list。比如range(5)生成的序列是从0开始小于5的整数：
bugList = list(range(101));
total = 0 ;
for bigList in bugList:
    total+=bigList
    pass;
print(total)

#第二种循环是while循环，只要条件满足，就不断循环，条件不满足时退出循环。
#比如我们要计算100以内所有奇数之和，可以用while循环实现
sum = 0
n = 99
while n > 0:
    sum = sum + n
    n = n - 2
print(sum)
#用for
list2 = list(range(100))
top=100
total = 0
print(list2)
for list in list2:
    if list%2!=0:
        total +=list;
        pass
print(total)
#break
#在循环中，break语句可以提前退出循环。例如，本来要循环打印1～100的数字：
n = 1;
while n<100:
    if n==10:
        break
    n+=1;
    print(n);
print('end')

#continue 打印所有的奇数
n = 0;
flg = True;
while n<100:
    n+=1;
    if n%2==0:
        continue
    print(n);
print('end')
