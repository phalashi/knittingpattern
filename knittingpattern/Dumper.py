"""Writing objects to files

This module offers a unified interface to serialize objects to strings
and save them to files.
"""
from io import StringIO
from tempfile import NamedTemporaryFile
import json


class ContentDumper(object):
    """This class is a unified interface for saving objects.

    The idea is to decouple the place to save to from the process used
    to dump the content.
    We are saving several objects such as patterns and SVGs.
    They should all have the same convinient interface.

    The process of saving something usally requires writing to some file.
    However, users may want to have the result as a string, an open file,
    a file on the hard drive on a fixed or temporary location,
    posted to some url or in a zip file.
    This class should provide for all those needs while providing a uniform
    interface for the dumping.
    """

    def __init__(self, on_dump):
        """Create a new dumper object with a function `on_dump(file)`

        The dumper calls `on_dump(file)` with a file-like object every time
        one of its save methods, `string`, `file`, ..., is called.
        The file-like object in the 'file' argument supports the method
        `write` to which the content should be written."""
        self.__dump_to_file = on_dump

    def string(self):
        """Returns the dump as a string."""
        file = StringIO()
        self.__dump_to_file(file)
        file.seek(0)
        return file.read()

    def file(self, file=None):
        """Saves the dump in a file-like object.

        If `file` is `None`, a new file-like object(StringIO) is returned.

        If `file` is not `None` it should be a file-like object.
        The content is written to the file. After writing, the file's
        read/write position points behind the dumped content."""
        if file is None:
            file = StringIO()
        self.__dump_to_file(file)
        return file

    def path(self, path):
        """Saves the dump in a file named `path`."""
        with open(path, "w") as file:
            self.__dump_to_file(file)

    def temporary_path(self):
        """Saves the dump in a temporary file and returns its path.

        The user of this method is responsible for deleting this file to
        save space on the hard drive. If you only need a file object for
        a short period of time you can use the method `temporary_file()`."""
        return self._temporary_file(False).name

    def temporary_file(self, delete_when_closed=True):
        """Saves the dump in a temporary file and returns the open file object.

        If `delete_when_closed` is `True` (default) the file on the hard drive
        will be deleted if it is closed or not referenced any more.

        If `delete_when_closed` is `False` the returned temporary file is not
        deleted when closed or unreferenced.
        The user of this method has then the responsibility to free the
        system space.

        The returned file-like object has an attribute `name` that holds
        the location of the file."""
        return self._temporary_file(delete_when_closed)

    def _temporary_file(self, delete=True):
        """The private interface to save to temporary files."""
        file = NamedTemporaryFile("w+", encoding="UTF8", delete=delete)
        self.__dump_to_file(file)
        return file


class JSONDumper(ContentDumper):

    def __init__(self, on_dump):
        """Create a new JSONDumper object with the callable `on_dump`.

        `on_dump` takes no aguments and returns the object that should be
        serialized to JSON."""
        super().__init__(self._dump_to_file)
        self.__dump_to_json = on_dump

    def object(self):
        """Return the object that should be dumped."""
        return self.__dump_to_json()

    def _dump_to_file(self, file):
        """dump to the file"""
        json.dump(self.object(), file)


__all__ = ["ContentDumper"]