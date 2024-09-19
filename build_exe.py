import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name=LeetCodeReview',
    '--onefile',
    '-i=favicon.ico',
    '--add-data=config.py:.',
    '--add-data=database.py:.',
    '--add-data=generate_config.py:.',
    '--hidden-import=mysql.connector',
    '--hidden-import=ttkbootstrap'
])