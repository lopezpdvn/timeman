"""Tools for management of time and tasks."""

import datetime
from threading import Timer as tTimer

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
