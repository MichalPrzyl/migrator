from migrator import Migrator


migrator = Migrator('example_application')
migrator.inspect_directory()

# migrator.fix_all_repetitions()