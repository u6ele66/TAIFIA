class WithCurrent(object):

    def __init__(self, generator):
        self.__gen = generator()

    def __iter__(self):
        return self

    def __next__(self):
        self.current = next(self.__gen)
        return self.current

    def __call__(self):
        return self


@WithCurrent
def get_id():
    x = 0
    while True:
        yield x
        x += 1


generator = get_id()
