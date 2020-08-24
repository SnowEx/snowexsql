'''
This is an attempt at a cross platform installation script for install the
packages for the snowex database
'''

from subprocess import check_output
import platform
import time


this_os = platform.system().lower()

def find_kw_in_lines(kw, lines):
    '''
    Returns the index of a list of strings that had a kw in it
    '''
    for i,line in enumerate(lines):
        s = '{} = '.format(kw)
        uncommented = line.strip('#')
        if s in uncommented:
            if s[0] == uncommented[0]:
                break
    # No match
    if i == len(lines)-1:
        i = -1

    return i

def modify_postgres_conf(conf_file, entries):
    '''
    Opens, reads, and modifies the conf file with the dictionary provided,
    then writes it out

    Args:
        conf_file: path to a valid postgres.conf file
        entries: dictionary containing key value pairs for conf file, if keys
                 are not found they are appended at the end of the file
    '''
    with open(conf_file) as fp:
        lines = fp.readlines()
        fp.close()
    print("Updating options in {}...".format(conf_file))

    for k,v in entries.items():

        i = find_kw_in_lines(k, lines)

        if i != -1:
            # Found the option in the file, try to replace the value and keep the comment
            print('\tUpdating {} in {}...'.format(k, conf_file))
            info = lines[i].split('=')
            name = info[0].replace('#','').strip()
            data = info[1].lstrip().split('\t')

            # We don't care about the value, skip over it
            # value = data[0]
            comment = '\t'.join(data[1:])
            lines[i] = '{} = {}{}'.format(k, v, comment)

        else:
            # Append the options at the end
            print('\tWriting new option {} with value {}...'.format(k, v))
            lines.append('{} = {}\n'.format(k, v))

    # Now write out the modified lines
    with open(conf_file,'w+') as fp:
        fp.write(''.join(lines))
        fp.close()

def install_linux():
    '''
    Run the installation commands for linux
    '''

    # See  https://www.postgresql.org/download/linux/ubuntu/
    print('Installing postgresql and postgis...')

    #s = check_output(['sudo','apt-get', 'install', '-Y', 'postgresql-12', 'postgis'])
    conf_updates = {'work_mem':"2000 MB",
                    'postgis.enable_outdb_rasters': 1,
                    'postgis.gdal_enabled_drivers' :"'ENABLE_ALL'"
                    }

    modify_postgres_conf('/etc/postgresql/10/main/postgresql.conf', conf_updates)


def main():
    print('')
    print('Running Installation Script to Setup the SnowEx Database\n')

    start = time.time()

    # Manage the os
    if this_os == 'linux':
        install_linux()
    elif this_os == 'darwin':
        install_mac()
    else:
        raise ValueError('{} is not a platform this script was written for!')

    end = time.time()
    print('Installation complete! {:0.0f}s'.format((end - start) / 60.0))


if __name__ == '__main__':
    main()
