class UserNotFoundException(Exception):

    def __init__(self, id:str):
        self.id = id
        super().__init__(
            f"User with id: {id} not found"
        )

class ExceptionHandler(Exception):

    def __init__(self, *args):
        super().__init__(*args)