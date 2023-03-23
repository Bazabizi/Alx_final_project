import os
import sys
from uuid import uuid4
from model import db, File
from werkzeug.datastructures import FileStorage

sys.path.append("..")


class FileManager:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder

    def __generate_file_id(self) -> str:
        """Returns new unique uuid4 used in database for file"""

        id = uuid4()
        while File.get(id):
            id = uuid4()

        return str(id)

    def add_file_to_database(self, file_id: str, file_name: str, file_path: str, mime_type: str):
        """Adds reference to file to database

        Args:
            file_id (str): primary key for file on database
            file_path (str): path to file
            mime_type (str): MIME type of file
        """

        file = File(id=file_id, file_name=file_name,
                    file_path=file_path, mime_type=mime_type)
        db.session.add(file)
        db.session.commit()

    def save(self, file: FileStorage) -> str:
        """Saves file on specified upload folder and adds reference to database

        Args:
            file (FileStorage): `FileStorage` object representing file

        Returns:
            str: file id on database
        """
        path = os.path.join(self.upload_folder, file.filename)
        file.save(path)

        file_id = self.__generate_file_id()
        self.add_file_to_database(file_id, file.filename, path, file.mimetype)

        return file_id
