# Description: This file contains the core database code

""" Libraries """

import msgspec
import asyncio
import typing as t
from os import path
from enum import Enum


""" Schema """

# Exclusive Types
class DT(Enum):
    INVALID_KEY = 0


# Database Object
class Database:
    def __init__(self, file_loc: str, load: bool = False):
        """Initialize the database."""
        if path.exists(file_loc) and load:
            try:
                with open(file_loc, "rb") as file:
                    self.data = msgspec.json.decode(file.read())
            except Exception as e:
                print(
                    f"Warning: Exception occurred while loading existing database: {e}\nCreating new database..."
                )
                self.data = {}
        else:
            self.data = {}

        self.file_loc = file_loc
        self.revert_data: t.List[t.Tuple[t.Any, t.Any]] = []
        self.lock = asyncio.Lock()
        self.read_lock = asyncio.Condition(self.lock)
        self.readers = 0

    async def to_string(self) -> str:
        """Return the string representation of the database."""
        async with self.read_lock:
            self.readers += 1
            await self.read_lock.wait_for(lambda: self.readers == 1)

            string = f"Database(\n\tdata={self.data},\n\tfile_loc='{self.file_loc}',\n\trevert_data={self.revert_data}\n)"

            self.readers -= 1
            self.read_lock.notify_all()

            return string

    async def commit(self) -> None:
        """Commit the changes to the database."""
        async with self.lock:
            with open(self.file_loc, "wb") as file:
                file.write(msgspec.json.encode(self.data))

            self.revert_data.clear()

    async def pop(self, key: t.Any, default: t.Any = None) -> t.Any:
        """Remove and return the value for the given key."""
        async with self.lock:
            self.revert_data.append((key, self.data.get(key, DT.INVALID_KEY)))
            return self.data.pop(key, default)

    async def revert(self, n: int = 1) -> None:
        """Revert the last n changes to the database."""
        async with self.lock:
            if n == 0 and len(self.revert_data) > 0:
                while len(self.revert_data) > 0:
                    key, value = self.revert_data.pop()
                    if value == DT.INVALID_KEY:
                        del self.data[key]
                    else:
                        self.data[key] = value
            elif n > 0 and n <= len(self.revert_data):
                for _ in range(n):
                    key, value = self.revert_data.pop()
                    if value == DT.INVALID_KEY:
                        del self.data[key]
                    else:
                        self.data[key] = value
            else:
                raise ValueError(
                    "n must be a non-negative integer less than or equal to the number of changes made to the database."
                )

    async def contains(self, key: t.Any) -> bool:
        """Check if the key exists in the database."""
        async with self.read_lock:
            self.readers += 1
            await self.read_lock.wait_for(lambda: self.readers == 1)

            result = key in self.data

            self.readers -= 1
            self.read_lock.notify_all()

            return result

    async def get(self, key: t.Any, default: t.Any = None) -> t.Any:
        """Get the value for the given key, or return the default if the key does not exist."""
        async with self.read_lock:
            self.readers += 1
            await self.read_lock.wait_for(lambda: self.readers == 1)

            result = self.data[key] if key in self.data else default

            self.readers -= 1
            self.read_lock.notify_all()

            return result

    async def keys(self) -> t.List[t.Any]:
        """Return a list of keys in the database."""
        async with self.read_lock:
            self.readers += 1
            await self.read_lock.wait_for(lambda: self.readers == 1)

            keys = list(self.data.keys())

            self.readers -= 1
            self.read_lock.notify_all()

            return keys

    async def values(self) -> t.List[t.Any]:
        """Return a list of values in the database."""
        async with self.read_lock:
            self.readers += 1
            await self.read_lock.wait_for(lambda: self.readers == 1)

            values = list(self.data.values())

            self.readers -= 1
            self.read_lock.notify_all()

            return values

    async def set(self, key, value):
        """Set the value for the given key."""
        async with self.lock:
            self.revert_data.append((key, self.data.get(key, DT.INVALID_KEY)))
            self.data[key] = value

    async def len(self) -> int:
        """Return the number of keys in the database."""
        async with self.read_lock:
            self.readers += 1
            await self.read_lock.wait_for(lambda: self.readers == 1)
            length = len(self.data)
            self.readers -= 1
            self.read_lock.notify_all()
            return length

    async def __aiter__(self) -> t.AsyncIterator[t.Any]:
        """Asynchronous iterator over the keys in the database."""
        async with self.read_lock:
            self.readers += 1
            await self.read_lock.wait_for(lambda: self.readers == 1)
            for key in self.data:
                yield key
            self.readers -= 1
            self.read_lock.notify_all()

    async def __aenter__(self) -> "Database":
        """Enter the runtime context related to this object."""
        await self.lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Exit the runtime context related to this object."""
        self.lock.release()
