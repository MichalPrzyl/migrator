import os


class Migrator:
    already_applied_files: list[str] = ['0001_first.py', '0002_another.py', '0003_upie.py', '0004_lol.py']
    all_migration_files: list[str] = []
    unapplied: list[str] = []
    fixed_migration_files: list[str] = []

    def __init__(self,
                 directory: str) -> None:
        self.directory = directory

    def inspect_directory(self):
        self.all_migration_files: list[str] = os.listdir(self.directory)
        self.unapplied: list[str] = self.get_unapplied_files()
        status, code = self.check_numbers()
        print(f"status:\nis ok: %s" % status)
        print("code: %s" % code)
        if status == False:
            if code == 'repetition':
                self.fix_repetitions()


    def get_unapplied_files(self):
        return sorted([file for file in self.all_migration_files if file not in self.already_applied_files])

    def check_numbers(self):
        if not self.repetition_exist():
            return True, 'ok'
        return False, 'repetition'

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
        # fixing name
        max_applied_prefix = max(self.get_applied_prefixes())
        print(f"fixing repetitions")
        for index, unapplied_migration in enumerate(self.unapplied):
            print(f"fixing: {unapplied_migration}")
            new_name = f"{self.get_prefix_string_based_on_number(max_applied_prefix+(index+1))}_{self.get_postfix(unapplied_migration)}"
            print(f"new_name: {new_name}")
            self.rename_file(unapplied_migration, new_name)
            # self.change_dependency(new_name)

        # fix dependencies on migrations that we renamed    
        all_fixed_migration_files_names = os.listdir(self.directory)
        for index, unapplied_migration in enumerate(self.fixed_migration_files):
            new_dependency = self.find_migration_file_with_its_index_minus_one(unapplied_migration)



    @staticmethod
    def get_string_prefix_from_name(name):
        return name[:4]
        
    @staticmethod    
    def get_postfix(name):
        return name[5:]

    @staticmethod    
    def get_prefix_string_based_on_number(number):
        if number < 10:
            return f"000{number}"
        elif number >= 10 and number < 100:
            return f"00{number}"
        elif number >= 100 and number < 1000:
            return f"0{number}"
        else:
            return f"{number}"

    def rename_file(self, old_file_name, new_file_name):
        os.rename(f"{self.directory}/{old_file_name}", f"{self.directory}/{new_file_name}")
        self.fixed_migration_files.append(new_file_name)


    def change_dependency(self, file_path, new_dependency):
       
        line_to_replace = self.get_dependency_string_to_replace(file)

        with open(f"{self.directory}/{file_path}", 'r') as file:
            content = file.read()
        
        new_content = content.replace(f"{line_to_replace}", f"\t(\'{self.directory}\', \'{new_dependency}\')")

        with open(f"{self.directory}/{file_path}", 'w') as file:
            file.write(new_content)

        print(f'Zmieniono zawartość pliku {file_path}.')

    def get_dependency_string_to_replace(self, file_path):
        with open(f"{self.directory}/{file_path}", 'r') as file:
            content = file.read()
            lines = content.split('\n')
            for line in lines:
                if self.directory in line:
                    return line

    def find_migration_file_with_its_index_minus_one(self, migration_file_name):
        this_index = int(migration_file_name[:4])  # e.g. 4
        new_index = this_index - 1
        new_index_string = self.get_prefix_string_based_on_number(new_index)  # e.g. '0004'
        all_migrations = os.listdir(self.directory)
        correct_migration_file = [filename for filename in all_migrations if filename.startswith(new_index_string)][0]
        return correct_migration_file
