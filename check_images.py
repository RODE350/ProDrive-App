import sqlite3, os
conn=sqlite3.connect('prodrive.db')
c=conn.cursor()
print("Checking vehicle image paths")
for name,image in c.execute('SELECT name,image FROM vehicles'):
    if not os.path.exists(image):
        print('missing file for', name, '->', image)
conn.close()