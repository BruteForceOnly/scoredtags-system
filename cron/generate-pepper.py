import os
import datetime
import sys

time_now = datetime.datetime.now()

# ensure that we always have a pepper for the current month
if not os.path.isfile(f"/ppprs/{time_now.year}_{time_now.month}"):
    f = open(f"/ppprs/{time_now.year}_{time_now.month}", "wb")
    f.write(os.urandom(16))
    f.close()
    print('new pepper generated', file=open('/proc/1/fd/1', 'w'))

# create next month's pepper when argument supplied
if len(sys.argv) > 1:
    next_month_flag = sys.argv[1]
else:
    next_month_flag = None
if next_month_flag == "-nm":
    date_next_month = datetime.date(time_now.year+int(time_now.month/12), 1+(time_now.month%12), 1)
    if not os.path.isfile(f"/ppprs/{date_next_month.year}_{date_next_month.month}"):
        f = open(f"/ppprs/{date_next_month.year}_{date_next_month.month}", "wb")
        f.write(os.urandom(16))
        f.close()
        print("next month's pepper generated", file=open('/proc/1/fd/1', 'w'))

print('generate pepper script ran', file=open('/proc/1/fd/1', 'w'))