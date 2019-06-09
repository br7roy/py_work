#dic 相当于map
dic = {"jack":23,"tom":25}
print(dic["jack"])
#要避免key不存在的错误，有两种办法，一是通过in判断key是否存在：
flg = "jack"in dic;
if flg:
    print("ok",flg)
else:
    print("bad",flg)
    pass

#二是通过dict提供的get()方法，如果key不存在，可以返回None，或者自己指定的value：
flg = dic.get("jack1")
if flg:
    print("ok",flg)
else:
    print("bad",flg)
    pass

#注意：返回None的时候Python的交互环境不显示结果。
#要删除一个key，用pop(key)方法，对应的value也会从dict中删除：
print(dic)
dic.pop("jack")
print(dic)
#dict可以用在需要高速查找的很多地方，在Python代码中几乎无处不在，正确使用dict非常重要，
#需要牢记的第一条就是dict的key必须是不可变对象。
#要保证hash的正确性，作为key的对象就不能变。在Python中，字符串、整数等都是不可变的，
#因此，可以放心地作为key。
key=["haha","hehe"]
#dic[key]='a list'而list是可变的，就不能作为key
