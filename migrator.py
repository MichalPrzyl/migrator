import os


class Migrator:
    already_applied_files: list[str] = ['0001_first.py', '0002_another.py', '0003_upie.py']
    all_migration_files: list[str] = []
    unapplied: list[str] = []

    def __init__(self,
                 directory: str) -> None:
        self.directory = directory

    def inspect_directory(self):
        self.migration_files: list[str] = os.listdir(self.directory)
        self.unapplied: list[str] = self.get_unapplied_files()
        status, code = self.check_numbers()
        print(f"status:\nis ok: %s" % status)
        print("code: %s" % code)
        if status == False:
            if code == 'repetition':
                self.fix_repetitions()


    def get_unapplied_files(self):
        return [file for file in self.migration_files if file not in self.already_applied_files]

    def check_numbers(self):
        if not self.repetition_exist():
            return True, 'ok'
        return False, 'repetition'

    # def difference_is_ok(self):
        # return bool(max(self.get_applied_prefixes()) - min(self.get_unapplied_prefixes()) == -1)

    def repetition_exist(self):
        for prefix in self.get_unapplied_prefixes():
            if prefix in self.get_applied_prefixes():
                return True
        return False
            

    def get_unapplied_prefixes(self):
        return [int(file[:4]) for file in self.unapplied]

    def get_applied_prefixes(self):
        return [int(file[:4]) for file in self.already_applied_files]

    def get_prefixes(self):
        return [file[:4] for file in self.all_migration_files]
    
    def fix_repetitions(self):
        max_applied_prefix = max(self.get_applied_prefixes())
        file_to_fix = [unapplied_migration for unapplied_migration in self.unapplied if int(unapplied_migration[:4]) == max_applied_prefix][0]
        new_name = f"{max_applied_prefix + 1}_{file_to_fix[4:]}"
        self.rename_file(file_to_fix, new_name)
        



    # def fix_repetition(self, repetition):
    #     same_pref_reps = [file for file in self.migration_files if file.startswith(repetition)]
    #     wrong_one_list = [file for file in same_pref_reps if file not in Migrator.already_applied]
    #     assert len(wrong_one_list) == 1, ('More than 1 candidate to be correct migration: %s' % wrong_one_list) 
    #     wrong_one = wrong_one_list[0]
    #     correct_name = self.create_correct_name(wrong_one)
    #     self.rename_file(wrong_one, correct_name)
    #     self.replace_dependency(correct_name, )
        
    # def create_correct_name(self, wrong_name: str):
    #     prefixes_integers = [int(element) for element in self.prefixes]
    #     max_prefix = max(prefixes_integers)
    #     new_prefix = max_prefix + 1

    #     if new_prefix > 10 and new_prefix < 100:
    #         new_prefix = f'00{new_prefix}'
    #     if new_prefix >= 100 and new_prefix < 1000:
    #         new_prefix = f'0{new_prefix}'
    #     if new_prefix >= 1000:
    #         new_prefix = f'{new_prefix}'
    #     else:
    #         new_prefix = f'000{new_prefix}'

    #     postfix = wrong_name.split('_')[1]
    #     return f"{new_prefix}_{postfix}"

    def rename_file(self, old_file_name, new_file_name):
        os.rename(f"{self.directory}/{old_file_name}", f"{self.directory}/{new_file_name}")


    # def replace_dependency(self, file, old_dependency, new_dependency):
    #     file_path = file

    #     with open(file_path, 'r') as file:
    #         content = file.read()

    #     new_content = content.replace(f"{old_dependency}", f"{new_dependency}")

    #     with open(file_path, 'w') as file:
    #         file.write(new_content)

    #     print(f'Zmieniono zawartość pliku {file_path}.')
