import asyncio

class Subsystem():
    SUBSYSTEM_LOCK = None
    
    def __init__(self):
        type(self).SUBSYSTEM_LOCK = asyncio.Condition()
    
    def _get_lock(self) -> asyncio.Condition:
        return type(self).SUBSYSTEM_LOCK