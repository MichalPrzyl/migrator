import os


class Migrator:
    already_applied = ['0003_upie']
    migration_files = []
    repetitions = []

    def __init__(self,
                 directory: str) -> None:
        self.directory = directory

    def inspect_directory(self):
        self.migration_files: list[str] = os.listdir(self.directory)
        self.repetitions: list[str] = self.__get_repetitions(self.files)

    def __get_repetitions(self):
        prefixes = [file[:4] for file in self.migration_files]
        repetitions = set()

        if len(prefixes) != len(set(prefixes)):
            for prefix in prefixes:
                if prefixes.count(prefix) > 1:
                    repetitions.add(prefix)

    def foo(self):
        for repetition in self.repetitions:
            same_pref_reps = [file for file in self.migration_files if file.startswith(repetition)]
            print(same_pref_reps)