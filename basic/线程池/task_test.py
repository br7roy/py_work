def t1(arg,*kwarg,**kwargs):
    print(*args,kwarg,kwargs)



if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor, as_completed
    pool = ThreadPoolExecutor(max_workers=2)
    pool.submit(t1,())

