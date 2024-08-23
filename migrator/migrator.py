from app_migrator import AppMigrator
import json
import logging

logger = logging.getLogger('migrator')
logging.basicConfig(filename='migrator.log', encoding='utf-8', level=logging.DEBUG)
# logger.debug('This message should go to the log file')
# logger.info('So should this')
# logger.warning('And this, too')
# logger.error('And non-ASCII stuff, too, like Øresund and Malmö')

class Migrator:
    def __init__(self, fix_order=True, fix_dependencies=True):
        self.fix_order=fix_order
        self.fix_dependencies=fix_dependencies

    def fix_project(self):
        logger.info("Starting up")
        apps = self.__get_apps_info_from_json()
        logger.info(f"apps: {apps}")

        if self.fix_order:
            for app in apps:
                logger.info(f"Fixing order in app: {app['name']}")
                app_migrator = AppMigrator(app.get('path'),
                                           app.get('migrations'))
                app_migrator.check_and_fix_migration_order()

        if self.fix_dependencies:            
            for app in apps:
                logger.info(f"Fixing dependency in app: {app['name']}")
                app_migrator = AppMigrator(app.get('path'),
                                           app.get('migrations'))
                app_migrator.check_and_fix_dependencies()

    def __get_apps_info_from_json(self):
        with open('migration_data.json', 'r') as json_file:
            apps = json.load(json_file)
            return apps

