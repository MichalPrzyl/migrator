import os


class Migrator:
    already_applied = ['0003_upie']
    migration_files = []
    repetitions = {}

    def __init__(self,
                 directory: str) -> None:
        self.directory = directory

    def inspect_directory(self):
        self.migration_files: list[str] = os.listdir(self.directory)
        self.repetitions: list[str] = self.__get_repetitions()

    def __get_repetitions(self):
        self.prefixes = self.get_prefixes()
        repetitions = set()
        if len(self.prefixes) != len(set(self.prefixes)):
            for prefix in self.prefixes:
                if self.prefixes.count(prefix) > 1:
                    repetitions.add(prefix)
        return repetitions

    def get_prefixes(self):
        return [file[:4] for file in self.migration_files]
    
    def fix_all_repetitions(self):
        for repetition in self.repetitions:
            self.fix_repetition(repetition)

    def fix_repetition(self, repetition):
        same_pref_reps = [file for file in self.migration_files if file.startswith(repetition)]
        wrong_one = [file for file in same_pref_reps if file not in Migrator.already_applied]
        assert len(wrong_one) == 1, ('More than 1 candidate to be correct migration: %s' % wrong_one) 
        correct_name = self.create_correct_name(wrong_one)
        self.rename_file(wrong_one, correct_name)
        
    def create_correct_name(self, wrong_name: str):
        prefixes_integers = [int(element) for element in self.prefixes]
        new_prefix = max(prefixes_integers) + 1
        postfix = wrong_name.split('_')[1]
        return f"{new_prefix}_{postfix}"

    def rename_file(self, old_file_name, new_file_name):
        os.rename(old_file_name, new_file_name, src_dir_fd=None, dst_dir_fd=None)
