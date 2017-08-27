"""
Psedo crontab parser & calculator
"""

import datetime
import argparse

from collections import OrderedDict


class scheduleParser(object):
    """
    Use aritmetic to calculate possible dates from psedo cron format string   
    """
    # used as pointer to __schedule_counter
    __counter_idx = 0

    # used to track __schedule multi dimentions counter 
    __schedule_counter = [0, 0, 0, 0, 0, 0]
    
    
    # default schedule to overwrite
    # * * * * * * 
    __schedule = OrderedDict(
        [
            ("second", range(0, 60)),
            ("minute", range(0, 60)),
            ("hour", range(0, 24)),
            ("day", range(1, 31+1)),
            ("month", range(1, 12+1)),
            ("year", range(2017, 2020+1)),
            ("isoweekday", range(0, 7+1)), 
        ]
    )
    
    schedule = __schedule.copy()

    def __init__(self, cron_string, base_date = datetime.datetime.now()):
        self.base_date = base_date
        self.parse_string(cron_string)
    
    def __atoi(self, a):
        return int(a, 10)
    
    def __is_possible_value(self, value, idx):
        """
        check f a number is a possible value fot the schedule idx 
        """
        return value in self.__schedule.values()[idx]

    def parse_range(self, exp, idx):
        """
        read a-b expression
        
        it read only extarnals objects delimited by '-'
        'a-b-c-z' will retrun the range a-z
        '1-6-8-100-3' returns [1,2,3]
        all middle values are discared 
        """
        elements = exp.split("-")
        a = self.__atoi(elements[0])
        b = self.__atoi(elements[-1])
        if self.__is_possible_value(a, idx) and self.__is_possible_value(b, idx):
            if a < b:
                return range(a, b+1)
            else :
                return range(b, a+1)
        else :
            raise Exception("value out of range {}".format(exp))

    def parse_element(self, element_sring, idx):
        """
        build a sorted array from string
        """
        ret = []
        sub_element = element_sring.split(",")
        for sub in sub_element:
            # basic switch case 
            if '-' in sub :
                ret += self.parse_range(sub, idx)
            elif '/' in sub:
                raise Exception("/ is not inplemented yet")
            elif '*' == sub:
                return self.__schedule.values()[idx]
            else :
                # default case
                i = self.__atoi(sub)
                if self.__is_possible_value(i, idx):
                    ret.append(i)
                else :
                    raise Exception("value out of range {}".format(sub))
        return sorted(ret)


    def parse_string(self, psedo_cron):
        """/
        String parsing entrie point
        It split the global sring into small chunks of elements
        '0 1-6,9 * * * '
        """
        # I use simple(naive) parsing to ease translation in low level language  
        # maybe a future implementation based on C
        
        # split on space char 
        cron_array = psedo_cron.strip().split(" ")
        if len(cron_array) != 7:
            raise Exception("wrong nember of element provided {}".format(cron_array))
        for idx in range(0, len(cron_array)):
            values = self.parse_element(cron_array[idx], idx)
            key = self.schedule.keys()[idx]
            self.schedule[key] = values
        
        #print(self.schedule)

    def incr_counter(self, idx=0):
        """
        increment counter at index 
        this function is based on possible array len
        """
        # start at index 
        # remove last index
        s = self.schedule.copy()
        isoweekdays = s.pop("isoweekday")
        for key, val in s.items()[idx::]:
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
        s = self.schedule.copy()
        isoweekdays = s.pop("isoweekday")
        # read all schedule except isoweekday
        for key, val in s.items():
            v_idx = self.__schedule_counter[idx]
            tmp[key] = val[v_idx % len(val)]
            idx += 1
        #self.incr_counter()
        # force microsecond to 0 
        tmp['microsecond'] = 0
        try :
            ret = self.base_date.replace(**tmp)
            if ret.isoweekday() not in isoweekdays:
                self.incr_counter(idx=3)
                return self.get_next()
            else :
                self.incr_counter()
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



def dummy_run(schedule):
    t = scheduleParser(schedule)
    c = 0
    a = []
    while True:
        d = t.get_next()
        if d not in a:
            print(d.strftime("%A, %d. %B %Y %I:%M%p"))
            a.append(d)
        else :
            # print("Duplicated date detected, global count {}".format(c))
            break

        c+=1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('schedule', nargs=1, help="Psedo cron format string")
    args = parser.parse_args()
    for s in args.schedule:
        dummy_run(s)

if __name__ == "__main__":
    main()    
