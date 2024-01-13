from app_migrator import AppMigrator
import json


class Migrator:
    def __init__(self, fix_order=True, fix_dependencies=True):
        self.fix_order=fix_order
        self.fix_dependencies=fix_dependencies

    def fix_project(self):
        apps = self.__get_apps_info_from_json()
        if self.fix_order:
            for app in apps:
                app_migrator = AppMigrator(app.get('path'),
                                           app.get('migrations'))
                app_migrator.check_and_fix_migration_order()

        if self.fix_dependencies:            
            for app in apps:
                app_migrator = AppMigrator(app.get('path'),
                                           app.get('migrations'))
                app_migrator.check_and_fix_dependencies()

    def __get_apps_info_from_json(self):
        with open('migration_data.json', 'r') as json_file:
            apps = json.load(json_file)
            return apps

