class AssetExistsError(Exception):

    def __init__(self, location, file_path):
        self.location = location
        self.file_path = file_path


class ParserError(RuntimeError):

    pass
