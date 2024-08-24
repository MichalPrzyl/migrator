import os

def main():
    os.makedirs('test_django_project/main_app/migrations')
    create_migration_for_application("main_app", '0001', 'start', [])
    create_migration_for_application("main_app", '0002', 'another_one', [('main_app', '0001_start')])
    create_migration_for_application("main_app", '0003', 'another_one_third', [('main_app', '0002_another_one'), ('main_app', '0069_hello_darkness_my_old_friend')])
    # os.system("python3 before.py")

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


if __name__ == '__main__':
    main()
