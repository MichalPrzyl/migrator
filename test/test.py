import os


def test_find_and_change_external_dependency():
    os.makedirs('test_django_project/main_app/migrations')
    os.makedirs('test_django_project/user_app/migrations')
    create_migration_for_application("main_app", '0001', 'start', [])
    create_migration_for_application("user_app", '0001', 'first_user_app_migration', [])
    create_migration_for_application("main_app", '0002', 'another_one', [('main_app', '0001_start')])

    # Create json file with data about applied migrations.
    os.system("python3 ../migrator/before.py")

    create_migration_for_application("main_app", '0003', 'another_one_third', [('main_app', '0002_another_one'), ('user_app', '0069_first_user_app_migration')])

    # Fix project migrations and dependencies.
    os.system("python3 ../migrator/after.py")

    # Checking if the file exists and have proper dependencies
    assert check_file_for_patterns(
        "test_django_project/main_app/migrations/0003_another_one_third.py",
        "user_app",
        "0001_first_user_app_migration"
    ) == True

    os.system("./clean.sh")


def test_simple_internal_dependency():
    os.makedirs('test_django_project/main_app/migrations')

    create_migration_for_application("main_app", '0001', 'start', [])
    create_migration_for_application("main_app", '0002', 'another_one', [('main_app', '0001_start')])

    # Create json file with data about applied migrations.
    os.system("python3 ../migrator/before.py")

    create_migration_for_application("main_app", '0002', 'another_one_third', [('main_app', '0001_start')])


    # Fix project migrations and dependencies.
    os.system("python3 ../migrator/after.py")

    # Checking if the file exists and have proper dependencies
    assert check_file_for_patterns(
        "test_django_project/main_app/migrations/0003_another_one_third.py",
        "main_app",
        "0002_another_one"
    ) == True

    os.system("./clean.sh")


def test_lol2():
    assert 1==1
    assert 1==1




# UTILS

def create_migration_for_application(
        app: str, 
        migration_number: int,
        migration_file_name: str,
        dependencies: list[str]):
    dependencies_str = ",\n\t\t\t\t\t\t".join([f'("{dep[0]}", "{dep[1]}")' for dep in dependencies])

    migration_content = f"""class Migration(migrations.Migration):
        dependencies = [{dependencies_str}]

        operations = [
            migrations.DeleteModel("Tribble"),
            migrations.AddField("Author", "rating", models.IntegerField(default=0)),
    ]"""

    with open(f"test_django_project/{app}/migrations/{migration_number}_{migration_file_name}.py", "w") as file:
        file.write(migration_content)


def check_file_for_patterns(filepath, pattern1, pattern2):
    # Check if file exist
    if not os.path.isfile(filepath):
        return False, f"File doesn't exist: {filepath}"

    with open(filepath, 'r') as file:
        for line in file:
            if pattern1 in line and pattern2 in line:
                return True

    return False, f"No line with both patterns: {pattern1, pattern2}"
