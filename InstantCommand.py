class InstantCommand(Command):
    def __init__(self, method: Callable):
        Command.__init__(self)
        self._instant_method = method

    def initialize(self):
        self._instant_method()
        self.finished()

    def end(self):
        pass

    def execute(self):
        pass