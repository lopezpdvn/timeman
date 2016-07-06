"""Tools for management of time and tasks."""

import datetime
from threading import Timer as tTimer

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
