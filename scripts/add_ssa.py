'''
Added ssa measurements to the database

Download from https://osu.app.box.com/s/7yq08y1mqpl9evgz6rfw8hu771228ryn

Unzip to ~/Downloads
'''

from os.path import join, abspath, basename, relpath
from os import listdir
from snowxsql.batch import UploadProfileBatch


def main():

    # Obtain a list of Grand mesa pits
    directory = abspath(join('..', '..', 'SnowEx2020_SQLdata'))
    ssa_dir = join(directory, 'SSA')
    filenames = [join(directory, 'SSA', f) for f in listdir(ssa_dir) if f.split('.')[-1]=='csv']

    b = UploadProfileBatch(filenames=filenames, debug=False)
    b.push()
    return len(b.errors)

if __name__ == '__main__':
    main()
