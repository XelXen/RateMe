# Description: This file contains the core database code

""" Libraries """

import msgspec
import asyncio
import typing as t
from os import path


""" Schema """

class Database:
    def __init__(self, file_loc: str, load: bool = False):
        """
        Initialize the database.
        
        :param file_loc: The location of the database file.
        :param load: Whether to load the existing database file.
        """

        self.file_loc = file_loc
        self.lock = asyncio.Lock()

        if load and path.exists(file_loc):
            try:
                with open(file_loc, "rb") as file:
                    self.data = msgspec.json.decode(file.read())
            except Exception as e:
                print(
                    f"[Database] Warning: Exception occurred while loading existing database: {e}\n[Database] Creating new database..."
                )
                self.data = {}
        else:
            self.data = {}

    def __str__(self) -> str:
        """
        Return the string representation of the database.
        
        :return: The string representation of the database.
        """
        return f"Database(\n\tdata={self.data},\n\tfile_loc='{self.file_loc}'\n)"
    
    def __repr__(self) -> str:
        """
        Return the string representation of the database.
        
        :return: The string representation of the database.
        """
        return self.__str__()

    def commit(self, data: t.Any) -> None:
        """Commit the changes to the database."""
        with open(self.file_loc, "wb") as file:
            file.write(msgspec.json.encode(data))

    async def open(self) -> t.Any:
        """Aquire the lock for the database if it is not already aquired."""
        await self.lock.acquire()
        return self.data

    async def close(self) -> None:
        """Release the lock for the database."""
        self.lock.release()
