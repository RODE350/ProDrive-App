import itertools
with open('Main.py', encoding='utf-8', errors='ignore') as f:
    for i,line in itertools.islice(enumerate(f,1),359,375):
        print(i,repr(line))
