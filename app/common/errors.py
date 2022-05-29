"""App exceptions modules."""

# pylint: disable=missing-class-docstring,multiple-statements


class SavingModelFailed(Exception): pass


class UnableToSaveModelInDB(Exception): pass


class InvalidModelId(Exception): pass


class UnknownModelId(Exception): pass


class FetchingModelFailed(Exception): pass


class InvalidModelAttribute(Exception): pass


class SelectingModelsFailed(Exception): pass


class UnableToFetchModelFromDB(Exception): pass


class UnableToSelectFromDB(Exception): pass


class UnableToDeleteModelFromDB(Exception): pass


class UnableToCreateModelFromJSON(Exception): pass
