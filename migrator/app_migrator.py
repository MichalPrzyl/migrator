import os
from config import PROJECT_DIR
import logging

logger = logging.getLogger('migrator')

class AppMigrator:
    already_applied_files: list[str] = []
    all_migration_files: list[str] = []
    unapplied: list[str] = []
    fixed_migration_files: list[str] = []

    def __init__(self,
                 directory: str,  #eg. '../backend/main
                 already_applied_files: [str]):

        self.directory = directory
        self.already_applied_files = already_applied_files

        all_files: list[str] = os.listdir(f"{self.directory}/migrations/")
        self.app = self.directory.split('/')[-1]
        self.all_migration_files: list[str] = [file for file in all_files if file not in ['__init__.py', '__pycache__']]
        self.unapplied: list[str] = self.get_unapplied_files()
        logger.info("initialized AppMigrator")

    def check_and_fix_migration_order(self):
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
            new_name = f"{self.get_prefix_string_based_on_number(max_applied_prefix+(index+1))}_{self.get_postfix(unapplied_migration)}"
            self.rename_file(unapplied_migration, new_name)

    def check_and_fix_dependencies(self):
        files_to_check = [file for file in self.all_migration_files if file not in self.already_applied_files]
        logger.info(f"Files to check: {files_to_check}")
        for file in files_to_check:
            logger.info(f"Checking file: {file}")
            file_prefix_string = file[:4]
            file_prefix = int(file_prefix_string)
            # Get correct dependency - it's current migration number - 1
            correct_internal_dep_prefix = file_prefix - 1
            correct_internal_dep_prefix_string = self.get_prefix_string_based_on_number(correct_internal_dep_prefix)
            with open(f"{self.directory}/migrations/{file}", 'r') as mig_file:
                content = mig_file.read()
                lines = content.split('\n')
                logger.info(f"lines: {lines}")
                if not self.has_dependency(lines): continue
                # Get starting and ending lines with dependency
                starting_line, ending_line = self.get_starting_and_ending_lines(lines)
                logger.info(f"starting_line: {starting_line}")
                logger.info(f"ending_line: {ending_line}")
                for index, line in enumerate(lines):
                    logger.info(f"Enumerating line - index: {index}, line: {line}")
                    if index < starting_line or index > ending_line:
                        logger.info("Skipping the line")
                        continue

                    logger.info("check - 2")
                    if self.app in line:  
                        logger.info("self app in line - True")
                        if correct_internal_dep_prefix_string in line:
                            continue  # means main dependency is correct
                        else:
                            for root, dirs, files in os.walk(f'{self.directory}/migrations'):
                                if '__pycache__' in root: continue
                                found_migration_file = [m_file for m_file in files if m_file.startswith(correct_internal_dep_prefix_string)][0]
                                self.change_dependency(f'{self.directory}/migrations/{file}', self.app, found_migration_file[:-3])

                    else:  # check other deps
                        logger.info("self app in line - False")
                        try:
                            start_index = line.index('(')
                            end_index = line.index(')')
                        except ValueError:
                            # Bad migration formatting: There is no '(' char in line
                            # with word "dependencies". Just continue to next line.
                            continue
                        dependency_tuple = eval(line[start_index:end_index+1])
                        dep_app = dependency_tuple[0]
                        dep_file = dependency_tuple[1]
                        for root, dirs, files in os.walk(f'{PROJECT_DIR}/{dep_app}/migrations'):
                            if f'{dep_file}.py' in files:
                                continue  # external dependency is ok
                            else:
                                name_without_prefix = f'{dep_file[5:]}.py'
                                found_migration_file = [m_file for m_file in files if m_file.endswith(name_without_prefix)][0]
                                self.change_dependency(f'{self.directory}/migrations/{file}', dep_app, found_migration_file[:-3])

    @staticmethod
    def get_starting_and_ending_lines(lines):
        for index, line in enumerate(lines):
            if 'dependencies' in line:
                starting_line = index
            if ']' in line:
                ending_line = index
                break
        return starting_line, ending_line

    @staticmethod
    def has_dependency(lines):
        for line in lines:
            if 'dependencies' in line:
                return True
        return False

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
        os.rename(f"{self.directory}/migrations/{old_file_name}", f"{self.directory}/migrations/{new_file_name}")
        self.fixed_migration_files.append(new_file_name)

    def change_dependency(self, file_path, app, new_dependency):

        line_to_replace = self.get_dependency_string_to_replace(file_path, app)

        with open(f"{file_path}", 'r') as file:
            content = file.read()

        new_content = content.replace(f"{line_to_replace}", f"\t\t(\'{app}\', \'{new_dependency}\')")

        with open(f"{file_path}", 'w') as file:
            file.write(new_content)

    def get_dependency_string_to_replace(self, file_path, app):
        whole_path = f'{file_path}'
        with open(f"{file_path}", 'r') as file:
            content = file.read()
            lines = content.split('\n')
            for line in lines:
                if app in line:
                    return line

    def find_migration_file_with_its_index_minus_one(self, migration_file_name):
        this_index = int(migration_file_name[:4])  # e.g. 4
        new_index = this_index - 1
        new_index_string = self.get_prefix_string_based_on_number(new_index)  # e.g. '0004'
        all_migrations = os.listdir(f"{self.directory}/migrations")
        correct_migration_file = [filename for filename in all_migrations if filename.startswith(new_index_string)][0]
        return correct_migration_file
