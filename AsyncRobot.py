import asyncio
import datetime
import hal
import logging

from wpilib.iterativerobotbase import IterativeRobotBase
from Command import Command

__all__ = ["AsyncRobot"]

class AsyncRobot(IterativeRobotBase):
    """AsyncRobot implements the IterativeRobotBase robot program framework.

    The AsyncRobot class is intended to be subclassed by a user creating a robot program.

    The asyncio Event loop schedules loopFunc() and periodic()
    functions, instead of being run directly.
    """
    DEFAULT_PERIOD = .02
    logger = logging.getLogger("robot")

    def __init__(self):
        super().__init__()
        hal.report(hal.UsageReporting.kResourceType_Framework, hal.UsageReporting.kFramework_Iterative)

        self._loop = asyncio.get_event_loop()

    def startCompetition(self) -> None:
        """Provide an alternate "main loop" via startCompetition()"""
        self.robotInit()
        hal.observeUserProgramStarting()

        # Loop forever, calling the appropriate mode-dependent function
        self._loop.run_until_complete(self._run_robot())

    async def _run_robot(self):
        while True:
            start = datetime.now()
            self.loopFunc()
            elapsed = min(AsyncRobot.DEFAULT_PERIOD, (datetime.now() - start).seconds)
            
            await asyncio.sleep(AsyncRobot.DEFAULT_PERIOD - elapsed)