"""
Psedo crontab parser & calculator
"""

import datetime
from collections import OrderedDict

class scheduleParser(object):
    """
    Use aritmetic to calculate possible dates from psedo cron format string   
    """
    # used as pointer to __schedule_counter
    __counter_idx = 0

    # used to track __schedule multi dimentions counter 
    __schedule_counter = [0, 0, 0, 0, 0, 0]
    
    
    # 0 50-57 6,12 1-3 3,4,6
    __schedule = OrderedDict(
        [
            ("second", range(0, 1)),
            ("minute", range(0, 1)),
            ("hour", range(0, 24)),
            ("day", range(1, 31+1)),
            ("month", range(1, 12+1)),
            ("year", range(2017, 2020+1)),
        ]
    )
    
    def __init__(self, base_date = datetime.datetime.now()):
        self.base_date = base_date

    def incr_counter(self, idx=0):
        """
        increment counter at index 
        this function is based on possible array len
        """
        for key, val in self.__schedule.items()[idx::]:
            current_count = self.__schedule_counter[idx] 
            current_count +=1
            # detect the end of array 
            if len(val) == 1 or ((current_count % len(val)) == 0 and (current_count // len(val)) > 0):
                # reset to 0 
                self.__schedule_counter[idx] = 0
                # carry one in the next loop 
            else:
                # carry one (or increment)
                self.__schedule_counter[idx] += 1
                # break the loop 
                return True
            idx += 1
    
    def get_next(self):
        tmp = {}
        idx = 0
        for key, val in self.__schedule.items() :
            v_idx = self.__schedule_counter[idx]
            tmp[key] = val[v_idx % len(val)]
            idx += 1
        self.incr_counter()
        # force microsecond to 0 
        tmp['microsecond'] = 0
        try :
            ret = self.base_date.replace(**tmp)
            # ValueError: day is out of range for month
        except ValueError as e:
            if str(e) == "day is out of range for month":
                # return next object 
                # TODO manage that case by calculation
                self.incr_counter(idx=3)
                return self.get_next()
            else :
                raise e
        #print(ret)
        #print(self.__schedule_counter, self.__counter_idx)
        return ret

t = scheduleParser()
c = 0
a = []
while True:
    c+=1
    d = t.get_next()
    print(d)
    if d not in a:
        a.append(d)
    else :
        print("Duplicated date detected, global count {}".format(c))
        exit(1)
    
