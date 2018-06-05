import asyncio
import datetime
from typing import Callable

class Command():
    DEFAULT_PERIOD = 0.02

    def __init__(self, persistent=False: bool):
        self.components = []
        self.elapsed_time = 0.0
        self.interrupt_event = None
        self.persistent = persistent
        self.task = None
    
    
    # Coroutines
    async def _run(self):
        """Coroutine run on the event loop"""
        
        self._initialize()

        while True:
            if self.isFinished():
                self._end()
                break
            elif self.interrupt_event.is_set():
                self.interrupted()
                self._release_resources()

                if self.persistent:
                    await self._suspend()
                else:
                    self._terminate()
                    break
            
            self._execute()
            await asyncio.sleep(Command.DEFAULT_PERIOD - self.elapsed_time)
        
        return
    
    async def _suspend(self):
        await asyncio.sleep(0)
        while self._check_resources():
            await asyncio.wait([component.wait() for component in self.components])
        
        self._acquire_resources()
        self.interrupt_event.clear()
        return


    # Private Methods
    def _check_resources(self) -> bool:
        return any([component.locked() for component in self.components])

    def _acquire_resources(self) -> None:
        for component in self.components:
            component.acquire()

    def _release_resources(self):
        for component in self.components:
            component.release()

            # Notify in case some Teleop commands were suspended.
            component.notify()
    
    def _set_interrupt(self, event) -> None:
        """Assign global interrupt from CommandGroup to Command"""
        self.interrupt_event = event
    
    def _terminate(self):
        self.task.cancel()

    
    # Public Methods
    def cancel(self):
        """Called by other Commands or CommandGroups"""
        self.interrupt_event.set()
    
    def requires(self, component):
        """Specifies what subsystems will be used in the command."""
        self.components.append(component._get_lock())
    
    def start(self) -> None:
        if self.interrupt_event is None:
            self.interrupt_event = asyncio.Event()
        
        self.task = asyncio.ensure_future(self._run)
        
        try:
            asyncio.get_event_loop().run_until_complete(self.task)
        except asyncio.CancelledError:
            print("INFO: Command "+ self.__class__.__name__ +" interrupted.")
    
    def _end(self):
        self.end()
        self._release_resources()

    def _execute(self):
        # Keep a constant interval.
        start_time = datetime.now()
        self.execute()
        self.elapsed_time = min(Command.DEFAULT_PERIOD, (datetime.now() - start).seconds)
    
    def _initialize(self):
        if self._check_resources():
            print('Subsystem in use by another command')
        else:
            self._acquire_resources()
            self.initialize()
            

    # User-Defined Methods
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