import os


class Migrator:
    already_applied = ['0003_upie']

    
    def __init__(self,
                 directory: str) -> None:
        self.directory = directory

    def inspect_directory(self):
        files: list[str] = os.listdir(self.directory)
        reps = self.__get_repetitions(files)

    def __get_repetitions(self, migration_files: list):
        prefixes = [file[:4] for file in migration_files]
        repetitions = set()

        if len(prefixes) != len(set(prefixes)):
            for prefix in prefixes:
                if prefixes.count(prefix) > 1:
                    repetitions.add(prefix)

        # print(prefixes)
        # print(repetitions)

        for repetition in repetitions:
            same_pref_reps = [file for file in migration_files if file.startswith(repetition)]
            print(same_pref_reps)