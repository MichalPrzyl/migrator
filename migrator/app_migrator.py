import os
from config import PROJECT_DIR, IGNORE_FILES
import logging

logging.basicConfig(filename='app_migrator.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='[%(levelname)s]:%(asctime)s:%(message)s',
    filemode='w'  # Reset log file after each run.
)

class AppMigrator:
    already_applied_files: list[str] = []
    all_migration_files: list[str] = []
    unapplied: list[str] = []
    fixed_migration_files: list[str] = []

    def __init__(self,
                 directory: str,  #eg. '../backend/main'
                 already_applied_files: [str]):

        self.logger = logging.getLogger('AppMigrator')
        self.logger.setLevel(logging.DEBUG)
        self.directory = directory
        self.already_applied_files = already_applied_files

        all_files: list[str] = os.listdir(f"{self.directory}/migrations/")
        self.app = self.directory.split('/')[-1]
        self.all_migration_files: list[str] = [file for file in all_files if file not in IGNORE_FILES]
        self.unapplied: list[str] = self.get_unapplied_files()

    def check_and_fix_migration_order(self):
        status, code = self.check_numbers()
        # Code actually doesn't matter ¯\_(ツ)_/¯
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
            return return_val

        if self.prefixes_are_in_order():
            pass
        else:
            return_val = False, 'wrong_order'

        return return_val

    def prefixes_are_in_order(self):
        unapplied_prefixes = self.get_unapplied_prefixes()
        applied_prefixes = self.get_applied_prefixes()
        all_migration_prefixes_as_integers = unapplied_prefixes + applied_prefixes
        if sorted(all_migration_prefixes_as_integers) == list(range(1, len(all_migration_prefixes_as_integers)+1)):
            return True
        else:
            return False

    def repetition_exist(self):
        unapplied_prefixes = set(self.get_unapplied_prefixes())
        applied_prefixes = set(self.get_applied_prefixes())

        if unapplied_prefixes.isdisjoint(applied_prefixes):
            return False
        else:
            return True

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
            self.logger.info(f"App: {self.app}: Changing migration name \"{unapplied_migration}\" to \"{new_name}\"")
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
                # GET DEPENDENCY LINES
                starting_line_index, ending_line_index = self.get_starting_and_ending_lines(lines)
                dependencies_lines = lines[starting_line_index:ending_line_index+1]

                # ITERATE THROUGH DEPENDENCY LINES
                for index, line in enumerate(dependencies_lines):
                    # We dont' check swappable_dependency.
                    if "swappable_dependency" in line:
                        continue
                    if '(' not in line or ')' not in line:
                        continue


                    dependency_app = self.get_app_from_line(line)

                    # INTERNAL DEPENDENCY
                    if dependency_app == self.app:
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

                    # EXTERNAL DEPENDENCY (with existing app (to which dependency points))
                    elif dependency_app in self.get_apps_list():
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
                    else:  # THERE IS NO APP IN THE PROJECT
                        # TODO: Handle that? Or at least print that as warning?
                        pass
                        # self.logger.warning("Application \"{dependency_app}\" is not present in the project")


    def get_app_from_line(self, line):
        line = line.strip()
        start_app_index = line.index("(\"")
        end_app_index = line.index("\",")
        app_name = line[start_app_index+2:end_app_index]
        return app_name

    def get_apps_list(self):
        subfolders = [ f.path for f in os.scandir(PROJECT_DIR) if f.is_dir() ]
        apps = []
        for subfolder in subfolders:
            app_name = os.path.basename(subfolder)
            # Don't list main project folder (where settings.py is) and
            # any of the ignored files.
            if app_name not in IGNORE_FILES + [os.path.basename(PROJECT_DIR)]:
                apps.append(app_name)

        return apps

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

        new_dependency_string = f"(\'{app}\', \'{new_dependency}\')"
        new_file_content = content.replace(f"{string_to_replace}", new_dependency_string)

        self.logger.info(f"Changing dependency from {string_to_replace} to {new_dependency_string} in migration: {file_path}")
        with open(f"{file_path}", 'w') as file:
            file.write(new_file_content)

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
