import sched
import time

global sch
sch = sched.scheduler(time.time, time.sleep)
global start
start = time.time()

def main():
    offset = 0

    def test1():
        sch.enter(1-(time.time() - offset), 1, test1)
        print("test 1 : {}".format(time.time() - start))
        """
        print("======")
        print(time.time() - offset)
        print(offset)
        print("======")
        """

    def test2():
        sch.enter(2-(time.time() - offset), 1, test2)
        print("test 2 : {}".format(time.time() - start))

    def test3():
        sch.enter(3-(time.time() - offset), 1, test3)
        print("test 3 : {}".format(time.time() - start))

    sch.enter(1, 1, test1)
    sch.enter(2, 1, test2)
    sch.enter(3, 1, test3)
    #sch.run(blocking=False)
    while True:
        offset = time.time()
        next_ev = sch.run(False)
        if next_ev is not None:
            time.sleep(min(1, next_ev))
        else:
            pass

if __name__=='__main__':
    main()
