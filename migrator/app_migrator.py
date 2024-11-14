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
        # print(f"directory: {directory}")
        # print(f"already_applied_files: {already_applied_files}")

        self.directory = directory
        self.already_applied_files = already_applied_files

        all_files: list[str] = os.listdir(f"{self.directory}/migrations/")
        self.app = self.directory.split('/')[-1]
        self.all_migration_files: list[str] = [file for file in all_files if file not in ['__init__.py', '__pycache__', 'custom']]
        self.unapplied: list[str] = self.get_unapplied_files()
        logger.info("initialized AppMigrator")
        # self.file_debug = '0010_failed_login_attempts_2024_08_26_16_03.py'
        self.file_debug = '0042_custom_populate_sample_sampling_site.py'


        
        # print(f"self.app: {self.app}")
            # print(f"self.all_migration_files: {self.all_migration_files}")
            # print(f"self.unapplied: {self.unapplied}")

    def check_and_fix_migration_order(self):
        status, code = self.check_numbers()
        #     print(f"status:\nis ok: %s" % status)
        #     print("code: %s" % code)
        if status == False:
            # if code == 'repetition':
            self.fix_repetitions()

    def get_unapplied_files(self):
        return sorted([file for file in self.all_migration_files if file not in self.already_applied_files])

    def check_numbers(self):
        return_val = (True, 'ok')

        if not self.repetition_exist():
            pass
        else:
            return_val = False, 'repetition'

        # get highest applied migration prefix
        already_applied_prefixes = []
        for applied in self.already_applied_files:
            already_applied_prefixes.append(int(applied[:4]))

        if already_applied_prefixes:
            highest_applied_prefix = max(already_applied_prefixes)

        unapplied_prefixes = self.get_unapplied_prefixes()
        # print(f"unapplied_prefixes: {unapplied_prefixes}")

        unapplied_prefixes = []
        for unapplied in self.unapplied:
            unapplied_prefixes.append(int(unapplied[:4]))
        # print(f"unapplied_prefixes: {unapplied_prefixes}")
        if unapplied_prefixes:
            lowest_unapplied_prefix = min(unapplied_prefixes)
        if unapplied_prefixes and already_applied_prefixes:
            if highest_applied_prefix == lowest_unapplied_prefix + 1:
                pass
            else:
                return_val = False, 'ehh'

        # return False, 'repetition'
        return return_val

    def repetition_exist(self):
        for prefix in self.get_unapplied_prefixes():
            if prefix in self.get_applied_prefixes():
                return True
        return False

    def get_unapplied_prefixes(self):
        output = []
        # print(f"self.unapplied: {self.unapplied}")
        for file in self.unapplied:
            # print(f"trying file :{file}")
            output.append(int(file[:4]))
        return output
        # return [int(file[:4]) for file in self.unapplied]

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
            # print(f"self.app: {self.app}")
            # print(f"file_prefix: {file_prefix}")
            # Get correct dependency - it's current migration number - 1
            correct_internal_dep_prefix = file_prefix - 1
            correct_internal_dep_prefix_string = self.get_prefix_string_based_on_number(correct_internal_dep_prefix)
            # print(f"correct_internal_dep_prefix_string: {correct_internal_dep_prefix_string}")
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
                    if '(' not in line or ')' not in line:
                        continue
                    logger.info(f"Enumerating line - index: {index}, line: {line}")
                    if index < starting_line or index > ending_line:
                        logger.info("Skipping the line")
                        continue

                    if file == self.file_debug:
                        print(f"line: {line}")
                    logger.info("check - 2")

                    # INTERNAL DEPENDENCY

                    if self._is_line_internal_dep(line):
                        if file ==  self.file_debug:
                            print(f"file: {file}")
                            print(f"this internal: {line}")
                        logger.info("self app in line - True")
                        if correct_internal_dep_prefix_string in line:
                            continue  # means main dependency is correct
                        else:
                            # DEBUGGING THIS WAS AWESOME
                            if "swappable_dependency" in line:
                                continue
                            for root, dirs, files in os.walk(f'{self.directory}/migrations'):
                                if '__pycache__' in root: continue
                                if 'custom' in root: continue
                                found_migration_file = [m_file for m_file in files if m_file.startswith(correct_internal_dep_prefix_string)][0]
                                if file == self.file_debug:
                                    print(f"changing dep")
                                self.change_dependency(f'{self.directory}/migrations/{file}', self.app, found_migration_file[:-3])

                    else:  # check other deps
                        if file == self.file_debug:
                            print(f"line: {line}")
                            print(f"this external: {line}")
                        logger.info("self app in line - False")
                        try:
                            # print(f"trying to get ( char) in line: {line}")
                            start_index = line.index('(')
                            end_index = line.index(')')
                        except ValueError:
                            # Bad migration formatting: There is no '(' char in line
                            # with word "dependencies". Just continue to next line.
                            # print(f"continuing with ValueError")
                            print(f"continuing")
                            continue

                        if "swappable_dependency" in line:
                            continue
                        # print(f"line: {line}")
                        dependency_tuple = eval(line[start_index:end_index+1])
                        dep_app = dependency_tuple[0]
                        dep_file = dependency_tuple[1]
                        if file == self.file_debug:
                            print(f"dep_app: {dep_app}")
                            print(f"dep_file: {dep_file}")
                        logger.info(f"dep_app: {dep_app}")
                        logger.info(f"dep_file: {dep_file}")
                        # x = f'{PROJECT_DIR}/{dep_app}/migrations'
                        # print(f"x: {x}")
                        # print(f"PROJECT_DIR: {PROJECT_DIR}")
                        for root, dirs, files in os.walk(f'{PROJECT_DIR}/weblab_backend/{dep_app}/migrations'):
                            # print(f"lol")
                            # print(f"files: {files}")
                            if f'{dep_file}.py' in files:
                                logger.info("External dependency is OK")

                                if file == self.file_debug:
                                    print(f"external dep present for {line}")
                                continue  # external dependency is ok
                            else:
                                if file == self.file_debug:
                                    print(f"There is no external dep present for: {line}")
                                logger.info("External dependency is NOT OK")
                                name_without_prefix = f'{dep_file[5:]}.py'
                                logger.info(f"name_without_prefix: {name_without_prefix}")

                                try:
                                    found_migration_file_helper = [m_file for m_file in files if m_file.endswith(name_without_prefix)]
                                    logger.info(f"found_migration_file_helper: {found_migration_file_helper}")
                                    found_migration_file= found_migration_file_helper[0]
                                    logger.info(f"found_migration_file: {found_migration_file}")
                                    self.change_dependency(f'{self.directory}/migrations/{file}', dep_app, found_migration_file[:-3])

                                except Exception as e:
                                    # print(f"Cannot fix migrations dependency in app: {dep_app} - migration: {dep_file}")
                                    logger.error(f"MP ERROR: {e}")
                                    logger.info(f"files: {files}")


    def get_starting_and_ending_lines(self, lines):
        starting_line = None
        ending_line = None
        for index, line in enumerate(lines):
            if 'dependencies' in line:
                starting_line = index
            if ']' in line and starting_line and index > starting_line:
                ending_line = index
                break
        self.starting_line = starting_line
        self.ending_line = ending_line
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
        print(f"line_to_replace: {line_to_replace}")
        

        with open(f"{file_path}", 'r') as file:
            content = file.read()

        
        # print(f"new_dependency: {new_dependency}")
        new_content = content.replace(f"{line_to_replace}", f"\t\t(\'{app}\', \'{new_dependency}\'),")
        print(f"new_content: {new_content}")

        with open(f"{file_path}", 'w') as file:
            file.write(new_content)

    def get_dependency_string_to_replace(self, file_path, app):
        whole_path = f'{file_path}'
        with open(f"{file_path}", 'r') as file:
            content = file.read()
            lines = content.split('\n')
            for index, line in enumerate(lines):
                if index >= self.starting_line and index <= self.ending_line:
                    if 'migrations.swappable' in line: continue
                    if app in line:
                        return line

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

