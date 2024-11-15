import os
from config import PROJECT_DIR, IGNORE_FILES
import logging


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
        self.all_migration_files: list[str] = [file for file in all_files if file not in IGNORE_FILES]
        self.unapplied: list[str] = self.get_unapplied_files()

    def check_and_fix_migration_order(self):
        status, code = self.check_numbers()
        if status == False:
            self.fix_repetitions()

    def get_unapplied_files(self):
        return sorted([file for file in self.all_migration_files if file not in self.already_applied_files])

    def check_numbers(self):
        return_val = (True, 'ok')

        if not self.repetition_exist():
            pass
        else:
            return_val = False, 'repetition'

        # Get highest applied migration prefix.
        already_applied_prefixes = []
        for applied in self.already_applied_files:
            already_applied_prefixes.append(int(applied[:4]))

        if already_applied_prefixes:
            highest_applied_prefix = max(already_applied_prefixes)

        unapplied_prefixes = self.get_unapplied_prefixes()

        unapplied_prefixes = []
        for unapplied in self.unapplied:
            unapplied_prefixes.append(int(unapplied[:4]))
        if unapplied_prefixes:
            lowest_unapplied_prefix = min(unapplied_prefixes)
        if unapplied_prefixes and already_applied_prefixes:
            if highest_applied_prefix == lowest_unapplied_prefix + 1:
                pass
            else:
                return_val = False, 'ehh'
        return return_val

    def repetition_exist(self):
        for prefix in self.get_unapplied_prefixes():
            if prefix in self.get_applied_prefixes():
                return True
        return False

    def get_unapplied_prefixes(self):
        output = []
        for file in self.unapplied:
            output.append(int(file[:4]))
        return output

    def get_applied_prefixes(self):
        return [int(file[:4]) for file in self.already_applied_files]

    def get_prefixes(self):
        return [file[:4] for file in self.all_migration_files]
    
    def fix_repetitions(self):
        max_applied_prefix = max(self.get_applied_prefixes())
        for index, unapplied_migration in enumerate(self.unapplied):
            new_name = f"{self.get_prefix_string_based_on_number(max_applied_prefix+(index+1))}_{self.get_postfix(unapplied_migration)}"
            print(f"[INFO]App: {self.app}: Changing migration name \"{unapplied_migration}\" to \"{new_name}\"")
            self.rename_file(unapplied_migration, new_name)

    def check_and_fix_dependencies(self):
        files_to_check = [file for file in self.all_migration_files if file not in self.already_applied_files]
        for file in files_to_check:
            file_prefix_string = file[:4]
            file_prefix = int(file_prefix_string)
            # Get correct dependency - it's current migration number - 1
            correct_internal_dep_prefix = file_prefix - 1
            correct_internal_dep_prefix_string = self.get_prefix_string_based_on_number(correct_internal_dep_prefix)
            with open(f"{self.directory}/migrations/{file}", 'r') as mig_file:
                content = mig_file.read()
                lines = content.split('\n')
                if not self.has_dependency(lines): continue
                # Get starting and ending lines with dependency
                # GET DEPENDENCY LINES
                starting_line, ending_line = self.get_starting_and_ending_lines(lines)
                dependencies_lines = lines[starting_line:ending_line+1]

                # ITERATE THROUGH DEPENDENCY LINES
                for index, line in enumerate(dependencies_lines):
                    # We dont' check swappable_dependency.
                    if "swappable_dependency" in line:
                        continue
                    if '(' not in line or ')' not in line:
                        continue

                    # INTERNAL DEPENDENCY
                    if self._is_line_internal_dep(line):
                        if correct_internal_dep_prefix_string in line:
                            continue  # means main dependency is correct
                        # FIX INTERNAL DEPENDENCY
                        else:
                            for root, dirs, files in os.walk(f'{self.directory}/migrations'):
                                if '__pycache__' in root: continue
                                if 'custom' in root: continue
                                found_migration_file = [m_file for m_file in files if m_file.startswith(correct_internal_dep_prefix_string)][0]
                                new_dependency = f"'{self.app}', '{found_migration_file[:-3]}'"
                                right_part_dependency = f'{found_migration_file[:-3]}'
                                self.change_dependency(f'{self.directory}/migrations/{file}', self.app, right_part_dependency)

                    else:  # check other deps
                        try:
                            start_index = line.index('(')
                            end_index = line.index(')')
                        except ValueError:
                            # Bad migration formatting: There is no '(' char in line
                            # with word "dependencies". Just continue to next line.
                            continue

                        if "swappable_dependency" in line:
                            continue

                        dependency_tuple = eval(line[start_index:end_index+1])
                        dep_app = dependency_tuple[0]
                        dep_file = dependency_tuple[1]

                        # FINDING CORRECT EXTERNAL DEPENDENCY
                        dir_to_find_external_dependency = "{}/{}".format(os.path.dirname(self.directory), dep_app)
                        for root, dirs, files in os.walk(dir_to_find_external_dependency):
                            if f'{dep_file}.py' in files:
                                continue  # external dependency is ok
                            else:
                                name_without_prefix = f'{dep_file[5:]}.py'

                                try:
                                    found_migration_file_helper = [m_file for m_file in files if m_file.endswith(name_without_prefix)]
                                    found_migration_file= found_migration_file_helper[0]
                                    self.change_dependency(f'{self.directory}/migrations/{file}', dep_app, found_migration_file[:-3])

                                except Exception as e:
                                    pass

    def get_starting_and_ending_lines(self, lines):
        for index, line in enumerate(lines):
            if 'dependencies' in line and '[' in line:
                starting_line_index = index

        for index, line in enumerate(lines):
            if ']' in line and index >= starting_line_index:
                ending_line_index = index
                break
        return starting_line_index, ending_line_index

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
        string_to_replace = self.get_dependency_string_to_replace(file_path, app)

        with open(f"{file_path}", 'r') as file:
            content = file.read()

        new_content = content.replace(f"{string_to_replace}", f"(\'{app}\', \'{new_dependency}\')")

        with open(f"{file_path}", 'w') as file:
            file.write(new_content)

    def get_dependency_string_to_replace(self, file_path, app):
        whole_path = f'{file_path}'
        with open(f"{file_path}", 'r') as file:
            content = file.read()
            lines = content.split('\n')
            found_index = self.get_line_index_with_content(lines, app)
            line = lines[found_index]
            dependency_start_index = line.index('(')
            dependency_end_index = line.index(')')
            return line[dependency_start_index:dependency_end_index+1]

    def find_migration_file_with_its_index_minus_one(self, migration_file_name):
        this_index = int(migration_file_name[:4])  # e.g. 4
        new_index = this_index - 1
        new_index_string = self.get_prefix_string_based_on_number(new_index)  # e.g. '0004'
        all_migrations = os.listdir(f"{self.directory}/migrations")
        correct_migration_file = [filename for filename in all_migrations if filename.startswith(new_index_string)][0]
        return correct_migration_file

    def _is_line_internal_dep(self, line):
        if self.app in line:
            return True
        return False

    def get_line_index_with_content(self, lines, pattern):
        found = [(index, element) for index, element in enumerate(lines) if pattern in element]
        if len(found) == 0:
            return None
        elif len(found) == 1:
            return found[0][0]
        else:
            # TODO: Is it correct to return first occurence here?
            return found[0][0]
