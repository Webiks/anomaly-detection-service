from threading import Timer


class Scheduler(object):
    def __init__(self, interval, function, *args, **kwargs):
        self.interval = 0
        self._timer = None
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start(interval)

    def _run(self):
        self.is_running = False
        self.start(self.interval)
        self.function(*self.args, **self.kwargs)

    def start(self, interval):
        self.interval = interval
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
