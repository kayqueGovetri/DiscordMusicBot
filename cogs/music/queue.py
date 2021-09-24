from errors.exceptions import QueueIsEmpty


class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0

    def add(self, *args):
        self._queue.extend(args)

    @property
    def is_empty(self):
        return not self._queue

    @property
    def first_track(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[0]

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty
        try:
            return self._queue[self.position]
        except IndexError:
            return None

    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[self.position + 1:]

    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue)

    def empty(self):
        self._queue.clear()

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position > len(self._queue) - 1:
            return None

        return self._queue[self.position]

    def clean_queue(self):
        self._queue = []
