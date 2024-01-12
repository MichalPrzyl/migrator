import os


class Migrator:
    already_applied = ['0003_upie.py']
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
        wrong_one_list = [file for file in same_pref_reps if file not in Migrator.already_applied]
        assert len(wrong_one_list) == 1, ('More than 1 candidate to be correct migration: %s' % wrong_one_list) 
        wrong_one = wrong_one_list[0]
        correct_name = self.create_correct_name(wrong_one)
        self.rename_file(wrong_one, correct_name)
        self.replace_dependency(correct_name, )
        
    def create_correct_name(self, wrong_name: str):
        prefixes_integers = [int(element) for element in self.prefixes]
        max_prefix = max(prefixes_integers)
        new_prefix = max_prefix + 1

        if new_prefix > 10 and new_prefix < 100:
            new_prefix = f'00{new_prefix}'
        if new_prefix >= 100 and new_prefix < 1000:
            new_prefix = f'0{new_prefix}'
        if new_prefix >= 1000:
            new_prefix = f'{new_prefix}'
        else:
            new_prefix = f'000{new_prefix}'

        postfix = wrong_name.split('_')[1]
        return f"{new_prefix}_{postfix}"

    def rename_file(self, old_file_name, new_file_name):
        os.rename(f"{self.directory}/{old_file_name}", f"{self.directory}/{new_file_name}")


    def replace_dependency(self, file, old_dependency, new_dependency):
        file_path = file

        with open(file_path, 'r') as file:
            content = file.read()

        new_content = content.replace(f"{old_dependency}", f"{new_dependency}")

        with open(file_path, 'w') as file:
            file.write(new_content)

        print(f'Zmieniono zawartość pliku {file_path}.')
