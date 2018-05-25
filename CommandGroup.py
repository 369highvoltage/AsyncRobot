import asyncio
from Command import Command
from typing import List

class CommandGroup(Command):
    _command_list: List[List[Command]]

    def __init__(self):
        self.interrupt_event = asyncio.Event()
        self._command_list = []
        self.task = None

    def add_parallel(self, commands: List[Command]) -> CommandGroup
        """Takes in a list of commands."""
        # Assign global interrupt to each command.
        for command in commands:
            command._set_interrupt(self.interrupt_event)

        self._command_list.append(commands)
        return self

    def add_sequential(self, command: Command) -> CommandGroup:
        """Takes in a single command."""
        command._set_interrupt(self.interrupt_event)

        self._command_list.append([command])
        return self

    async def _run(self):
        for commands in self._command_list:
            try:
                await asyncio.wait([command._run() for command in commands])
            except asyncio.CancelledError:
                break
        
        return

    def start(self) -> None:
        self.task = asyncio.ensure_future(self._run)
        asyncio.get_event_loop().run_until_complete(self.task)