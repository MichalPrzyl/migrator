from migrator import Migrator


migrator = Migrator('example_application')
migrator.inspect_directory()

x = migrator.migration_files
y = migrator.repetitions

print(x)
print(y)