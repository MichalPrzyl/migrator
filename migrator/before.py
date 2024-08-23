from config import PROJECT_DIR
import os
import json


def main():

    # TODO: if there is already `migration_data.json` file then delete it

    apps_dirs = list_directories_with_migrations(PROJECT_DIR)

    migrations_data = []

    for app_dir in apps_dirs:
        name = app_dir.split('/')[-1]
        migrations = get_app_migrations(app_dir)

        app_data = {
            'name': name,
            'path': app_dir,
            'migrations': migrations
        }

        migrations_data.append(app_data)

    save_data_to_json_file(migrations_data)

def save_data_to_json_file(data):
    with open('migration_data.json', 'w') as json_file:
        json_file.write(json.dumps(data, indent=4))

def get_app_migrations(app_dir):
    reserved_names = ['__init__.py', '__pycache__']
    for root, dirs, files in os.walk(f'{app_dir}/migrations'):
        return [file for file in files if file not in reserved_names]

def list_directories_with_migrations(dir):
    directories_with_migrations = []
    for root, dirs, files in os.walk(dir):
        if "migrations" in dirs:
            directories_with_migrations.append(root)
    return directories_with_migrations


if __name__ == '__main__':
    main()
