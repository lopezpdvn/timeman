"""Tools for management of time and tasks."""

import sys
import datetime
from calendar import isleap
from threading import Timer as tTimer

import pytaskcoach as tsk
import pyatt as att

timedelta = datetime.timedelta
DEFAULT_DATETIME_FMT = tsk.DEFAULT_DATETIME_FMT

SECS_PER_DAY = 86400
SECS_PER_HOUR = 3600
MICROSECS_PER_SEC = 1000000

EFFORT_KEYS_SORTED = ('category', 'start', 'end', 'effort', 'task')

DEFAULT_TIMEDELTA = timedelta(weeks=1)

class TimeDelta:
    """Counts time in process using datetime module.

    This class behaves like an in-process-stopwatch.  It is not
    intended for applications requiring very accurate results.  Value
    attribute returns the time as a datetime.timedelta object.  Useless
    order of method calls are valid, for example calling pause() or
    reset() just after construction, or calling run() two consecutive
    times.
    """
    # How many times __now() (datetime.datetime.now()) has been called.
    now_count = 0

    def __init__( self ):
        """No arguments needed. Note that instances do not run after
        construction.  Call run() for the first time after
        construction.
        """
        self.__state = 'new'
        self.__creation_time = self.__now
        self.__pause_mem = datetime.timedelta(0)

    def __str__( self ):
        # self.value is a datetime.timedelta object.
        return str(self.value)

    def __repr__( self ):
        # self.value is a datetime.timedelta object.
        """Same as __str__ because instances are expected to be used
        in an interactive interpreter.
        """
        return str(self.value)

    def __now( self ):
        self.__class__.now_count += 1
        return datetime.datetime.now()
    __now = property(__now)

    def run( self ):
        if self.__state == 'new':
            # First run() or run() after a paused reset().
            self.last_run_time = self.__now
            self.__state = 'running'
        elif self.__state == 'paused':
            self.last_run_time = self.__now
            self.__state = 'running'
        elif self.__state == 'running':
            pass

    def value( self ):
        """Return current time value.  Call periodically for displays.
        """
        if self.__state == 'new':
            return datetime.timedelta(0)
        elif self.__state == 'running':
            # self.__pause_mem contains a value if instance has been
            # paused before.  Otherwise is datetime.timedelta(0).
            return self.__now - self.last_run_time + self.__pause_mem
        elif self.__state == 'paused':
            return self.__pause_mem
    value = property(value)

    def pause( self ):
        if self.__state == 'new':
            pass
        elif self.__state == 'running':
            self.__pause_mem = self.value  # Update pause memory
            self.__state = 'paused'
        elif self.__state == 'paused':
            pass

    def reset( self ):
        if self.__state == 'new':
            pass
        elif self.__state == 'running':
            # Erase self.__pause_mem and continue running.
            self.__pause_mem = datetime.timedelta(0)
            self.last_run_time = self.__now
        elif self.__state == 'paused':
            # Behave as 'new' because instance must not automatically
            # run after reset since it was previously paused.
            self.__state = 'new'
            self.__pause_mem = datetime.timedelta(0)

class Timer:
    """Run an action in process after an interval of time.

    Essentially the same as threading.Timer class with a few
    enhancements.  The main callable object '__callable_obj' will be
    called after 'interval' units of time.
    """
    def __init__( self, interval, callable_obj, *args, **kwargs):
        """Timer constructor.

        Parameters:
            interval    :   datetime.timedelta object or seconds as int
                            or float.  Raise TypeError if other unit
                            supplied.  'mcall' will be called 'reps'
                            times each 'interval'
            callable_obj:   main callable object with or without
                            arguments.
            *args       :   optional positional arguments for
                            '__callable_obj' argument.
            *kwargs     :   optional keyword arguments for
                            '__callable_obj' argument.

        Instances are not automatically run after construction, user
        must call run().
        """
        self._state = 'new'

        # These are attached to the instance because pause() method
        # cancels self.timer (threading.Timer).  Running after being
        # paused reconstructs the threading.Timer instance.
        self.__callable_obj           = callable_obj
        self.__callable_obj_args      = args
        self.__callable_obj_kwargs    = kwargs

        # If 'interval' is seconds, it is first converted to
        # datetime.timedelta and then again to seconds.
        if isinstance(interval, int) or isinstance(interval, float):
            interval = datetime.timedelta(seconds=interval)
        elif isinstance(interval, datetime.timedelta):
            pass
        else:
            raise TypeError("Interval can only be a datetime.timedelta or "
                "int/float seconds")

        self.interval = interval
        self.interval_secs = (interval.seconds +
            (interval.days * float(SECS_PER_DAY)) +
            (interval.microseconds / float(MICROSECS_PER_SEC)))

        # threading.Timer instance.
        self.timer = tTimer(self.interval_secs, self.__callable_obj,
                            self.__callable_obj_args,
                            self.__callable_obj_kwargs)

        self.timedelta = TimeDelta()  # Keep time.

    def __str__( self ):
        return str(self.remains)

    def run(self):
        if self._state == 'new':
            # First run.
            self.timer.start()
            self.timedelta.run()
            self._state = 'running'
        elif self._state == 'running':
            pass
        elif self._state == 'paused':
            runned_for = (self.timedelta.value.seconds +
                (self.timedelta.value.days * float(SECS_PER_DAY)) +
                (self.timedelta.value.microseconds / float(MICROSECS_PER_SEC)))
            remains = self.interval_secs - runned_for  # Remains to run.

            # When paused, self.timer was cancelled, so this time is
            # being reconstructed with the time that remains.
            self.timer = tTimer(remains, self.__callable_obj,
                                self.__callable_obj_args,
                                self.__callable_obj_kwargs)
            self.timer.start()
            self.timedelta.run()
            self._state = 'running'

    def pause( self ):
        if self._state == 'new':
            pass
        elif self._state == 'running':
            self.timedelta.pause()
            self.timer.cancel()  # self.timer will be reconstructed
                                 # when instance is run again.
            self._state = 'paused'
        elif self._state == 'paused':
            pass

    @property
    def remains( self ):
        """Returns remaining time.

        Always return a datetime.timedelta, even if constructed with
        int or float seconds.
        """
        if self._state == 'new':
            return self.interval  # Original interval.
        elif self._state == 'running' or self._state == 'paused':
            value = self.timedelta.value
            if value >= self.interval:  # Timer is done.
                self._state = 'done'
                return datetime.timedelta(0)
            return self.interval - value
        elif self._state == 'done':
            # Timer is done.
            return datetime.timedelta(0)

    def cancel( self ):
        """Cancels Timer.

        Instance cannot be re-run (see pause()).  After cancelled,
        remaining time will be null timedelta (datetime.timedelta(0)).
        Use this method only if you are sure this instance will not be
        needed to run again.  Otherwise use pause().
        """
        self.timer.cancel()
        self.timedelta.pause()
        self._state = 'done'

    @property
    def elapsed( self ):
        """Returns elapsed time.

        If instance was cancelled, the value returned is the whole
        'interval'.
        """
        return self.interval - self.remains

def validate(taskcoach_cfgdirs, atimetracker_cfgdirs):
    return (tsk.validate(taskcoach_cfgdirs) and
            att.validate(atimetracker_cfgdirs))

def get_category_efforts_totals(categories=(), start=None, end=None, tskpaths=(),
        attpaths=()):
    for i in get_category_efforts(categories, start, end, tskpaths, attpaths):
        yield i;

def get_category_efforts(categories=(), start=None, end=None, tskpaths=(),
        attpaths=()):

    if start is None:
        start = datetime.now() - DEFAULT_TIMEDELTA

    efforts = {}

    for ctg, eff in tsk.get_category_efforts(categories, start, end,
            paths=tskpaths):
        efforts[ctg] = efforts.get(ctg, timedelta()) + eff

    for ctg, eff in att.get_category_efforts(categories, start, end, attpaths):
        efforts[ctg] = efforts.get(ctg, timedelta()) + eff

    for ctg, eff in efforts.items():
        yield (ctg, eff.total_seconds())

def get_category_efforts_details(categories=(), start=None, end=None,
        tskpaths=(), attpaths=()):
    if start is None:
        start = datetime.now() - DEFAULT_TIMEDELTA

    efforts = [effort for effort in tsk.get_category_efforts_details(
                                        categories, start, end, paths=tskpaths)]

    efforts.extend(effort for effort in att.get_category_efforts_details(
                                              categories, start, end, attpaths))

    return efforts

def plot_category_efforts(data, fnames=()):
    if not len(fnames):
        return
    import matplotlib.pyplot as plt
    categories = tuple(record[0] for record in data)
    effort = tuple(record[1] for record in data)
    plt.pie(effort, labels=categories, shadow=True)
    plt.axis('equal')
    for fname in fnames:
        plt.savefig(fname)

def get_year_progress(offset=datetime.timedelta(), year_start=None):
    now = datetime.datetime.now()
    year_delta_days = 366 if isleap(now.year) else 365
    year_delta = datetime.timedelta(days=year_delta_days)
    _year_start = (year_start if year_start
            else datetime.datetime(now.year, 1, 1))
    year_progress_delta = now - _year_start + offset
    return year_progress_delta / year_delta

def print_year_progress(fout=sys.stdout):
    now = datetime.datetime.now()
    x_start = datetime.datetime(2018, 12, 22)
    print('{:.2%}'.format(get_year_progress(year_start=x_start)), file=fout)
    print('{:.2%}'.format(get_year_progress()), file=fout)

def to_str_display(x):
    timedelta_methodname_check = 'total_seconds'

    # small duck typing test, is x a timedelta?
    if hasattr(x, timedelta_methodname_check):
        return '{0:,.2f}'.format(x.total_seconds() / SECS_PER_HOUR)
    else:
        return str(x)

def get_categories(tskpaths, attpaths):
    yield 'aaa'
    yield 'bbb'
