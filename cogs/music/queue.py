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

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position > len(self._queue) - 1:
            return None

        return self._queue[self.position]
