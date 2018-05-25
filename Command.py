import asyncio
import datetime
from typing import Callable

class Command():
    DEFAULT_PERIOD = 0.02

    def __init__(self, persistent=False: bool):
        self.components = []
        self.interrupt_event = None
        self.persistent = persistent
        self.task = None
    
    # Private Methods
    def _acquire_resources(self) -> bool:

        # Attempt to lock all subsystems.
        if any([component.locked() for component in self.components])
            return False
        else:
            for component in self.components:
                component.acquire()
            
            return True

    def _release_resources(self):
        for component in self.components:
            component.release()

            # Notify in case some Teleop commands were suspended.
            component.notify()

    async def _run(self):
        """Coroutine run on the event loop"""
        
        # Check & lock all components else abort.
        if not self._acquire_resources():
            return
        
        self.initialize()

        while not self.isFinished():
            if self.interrupt_event.is_set():
                self.interrupted()

                if self.persistent:
                    self._release_resources()
                    await asyncio.wait([component.wait() for component in self.components])
                    self._acquire_resources()
                    self.interrupt_event.clear()
                else:
                    self.task.cancel()
            
            # Keep a constant interval.
            interval_start = datetime.now()
            self.execute()
            interval_elapsed = min(Command.DEFAULT_PERIOD, (datetime.now() - start).seconds)
            await asyncio.sleep(Command.DEFAULT_PERIOD - interval_elapsed)
        
        self.end()
        self._release_resources()
        return
    
    def _set_interrupt(self, event) -> None:
        """Assign global interrupt from CommandGroup to Command"""
        self.interrupt_event = event

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