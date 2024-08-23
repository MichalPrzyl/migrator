cd test_django_project 

mkdir user_app
(cd user_app && mkdir migrations && cd migrations && touch 0001_migration_1.py)

mkdir test_app
(cd test_app && mkdir migrations && cd migrations && touch 0001_create_models.py)

mkdir music_app
(cd music_app && mkdir migrations && cd migrations && touch 0001_add_notes.py && touch 0002_add_more_notes.py)
