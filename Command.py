import asyncio
import datetime
from typing import Callable

class Command():
    DEFAULT_PERIOD = 0.02

    def __init__():
        self.interrupt_event = None

    #def requires(self):
    #def _acquire_resources(self):
    #def _release_resources(self):

    def interrupt(self):
        """Called by other Commands or CommandGroups"""
        self.interrupt_event.set()

    async def _run(self):
        """Coroutine run on the event loop"""
        self.initialize()

        while not self.isFinished() or self.interrupt_event.is_set():
            interval_start = datetime.now()
            self.execute()
            interval_elapsed = min(Command.DEFAULT_PERIOD, (datetime.now() - start).seconds)
            await asyncio.sleep(Command.DEFAULT_PERIOD - interval_elapsed)
        
        if self.interrupt.is_set():
            self.task.cancel()
        else:
            self.end()
            return
    
    def _setup_interrupt(self, interrupt_event) -> None:
        self.interrupt_event = interrupt_event

    def start(self) -> None:
        if self.interrupt_event is None:
            self.interrupt_event = asyncio.Event()
        
        self.task = asyncio.ensure_future(self._run)
        
        try:
            asyncio.get_event_loop().run_until_complete(self.task)
        except asyncio.CancelledError:
            self.interrupted()

    # These methods should be implemented by command creator
    def end(self) -> None:
        print("Default end() function - Overload me!")

    def execute(self) -> None:
        print("Default execute() function - Overload me!")

    def initialize(self) -> None:
        print("Default initialize() function - Overload me!")
    
    def interrupted(self) -> None:
        print("Default interrupted() function - Overload me!")

    def isFinished(self) -> bool:
        print("Default isFinished() function - Overload me!")


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