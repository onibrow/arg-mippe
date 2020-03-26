import sched
import time

global sch
sch = sched.scheduler(time.time, time.sleep)
global start
start = time.time()

def test1():
    print("test 1 : {}".format(time.time() - start))
    sch.enter(1, 1, test1)

def test2():
    print("test 2 : {}".format(time.time() - start))
    sch.enter(0.5, 1, test2)

def test3():
    print("test 3 : {}".format(time.time() - start))
    sch.enter(0.25, 1, test3)

def main():
    sch.enter(1, 1, test1)
    sch.enter(0.5, 1, test2)
    sch.enter(0.25, 1, test3)
    sch.run(blocking=True)

if __name__=='__main__':
    main()
