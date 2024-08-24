# Migrator

<div align="center">
  <img src=".readme/app_logo.jpg" alt="App Logo" width="200"/>
</div>

<div align="center">
    <h2> 📦 Django Migration Renaming Tool</h2>
</div>

Migrator is a tool designed to automatically check and fix Django migrations by renaming them if there are conflicts in their naming (e.g., two migrations with the same number but different names) and resolving dependencies. This ensures that your migrations are correctly applied without conflicts, even after merging branches in your version control system.


## 🛠️ How Does It Work?
- First edit `migrator/config.py`. In variable `PROJECT_DIR` put path to your django app project.

- Before Merge:
    Run the provided `before.py` script. This script records the currently applied migrations in a JSON file, capturing the state of your migrations before merging changes from another branch.

- After Merge:
    If the merge introduces a migration conflict (e.g., two migrations named 0002_*.py), **Migrator** will automatically detect this.
    The conflicting migration will be renamed to the next available number (e.g., 0003_add_model.py instead of 0002_add_model.py).
    **Migrator will then adjust any dependencies between migrations to ensure everything points to the correct files.**
    <div align="center">
        <h3>EVEN BETWEEN APPLICATIONS</h3>
    </div>
## 📄 Example

Imagine you have the following migrations:

    0001_initial.py
    0002_create_model.py
    0002_add_field.py

After running the Migrator, the second 0002_*.py migration will be renamed to 0003_add_field.py, and any dependencies will be updated accordingly.

🚨 Important Notes

Ensure you run the before.py script before merging any changes to accurately record the state of your migrations.
Review any changes made by the Migrator, especially in complex projects, to ensure everything works as expected.


## 📬 Support

If you encounter any issues or have questions, feel free to open an issue in the repository or contact the maintainers.


## Testing

To run the tests jest enter the `test` directory, and run following command:

```bash
python3 -m pytest test.py -v
or
python -m pytest test.py -v
```
flag `-v` is optional and allow you to see nie lists of `PASSED` words (hopefully).

If any of the test fails, we have to manually run the `clean` command. Still in `test` directory.
```bash
./clean.sh
```

© 2024 Michał Przyłucki. All rights reserved.
This source code is not licensed for use, copying, or modification without prior written consent from the author.

