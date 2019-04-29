# from multiprocessing import Process

# def start():
#     p = Process(target=work())
#     p.start()
#     p.join()

# def work():
#     from time import sleep
#     print('work is on')
#     sleep(1000)
#     print('work is off')



# if __name__ == "__main__":
#     print('main start')
#     start()
#     print('main end')


# import _thread, time, random
# count = 0
# def threadTest():
#     global count
#     for i in range(100):
#         count += 1

# if __name__ == "__main__":
#     for i in range(10):
#         _thread.start_new_thread(threadTest, ())	#如果对start_new_thread函数不是很了解，不要着急，马上就会讲解
#     time.sleep(3)

import threading  
  
def thread_fun(num):  
    for n in range(0, int(num)):  
        print(" I come from %s, num: %s" %( threading.currentThread().getName(), n))
  
def main(thread_num):  
    thread_list = list();  
    # 先创建线程对象  
    for i in range(0, thread_num):  
        thread_name = "thread_%s" %i  
        thread_list.append(threading.Thread(target = thread_fun, name = thread_name, args = (20,)))  
      
    # 启动所有线程     
    for thread in thread_list:  
        thread.start()  
      
    # 主线程中等待所有子线程退出  
    for thread in thread_list:  
        pass

if __name__ == "__main__":
    main(3) 
    print("main exit") 
