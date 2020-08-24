'''
Edits the postgres conf file
'''
import platform
import os
from subprocess import check_output

def find_kw_in_lines(kw, lines):
    '''
    Returns the index of a list of strings that had a kw in it

    Args:
        kw: Keyword to find in a line
        lines: List of strings to search for the keyword
    Return:
        i: Integer of the index of a line containing a kw. -1 otherwise
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
            print('\tUpdating {}...'.format(k))
            info = lines[i].split('=')
            name = info[0].replace('#','').strip()
            data = info[1].lstrip().split('\t')

            # We don't care about the value, skip over it
            # value = data[0]
            comment = '\t'.join(data[1:]).rstrip()
            lines[i] = '{} = {}{}\n'.format(k, v, comment)

        else:
            # Append the options at the end
            print('\tWriting new option {} with value {}...'.format(k, v))
            lines.append('{} = {}\n'.format(k, v))

    # Now write out the modified lines
    temp = 'temp.conf'
    with open(temp,'w+') as fp:
        fp.write(''.join(lines))
        fp.close()

    # Move the file using sudo so we dont have to execute this script with sudo
    check_output(['sudo', 'cp', os.path.abspath(temp), conf_file])



if __name__ == '__main__':
    # Modify and output the conf file to its original location
    conf_updates = {'work_mem':"2000MB",
                    'postgis.enable_outdb_rasters': 1,
                    'postgis.gdal_enabled_drivers' :"'ENABLE_ALL'"
                    }


    this_os = platform.system().lower()

    # Names of databases to make
    db_names = ['snowex','test']

    # Manage the os
    if this_os == 'linux':
        modify_postgres_conf('/etc/postgresql/12/main/postgresql.conf', conf_updates)
    elif this_os == 'darwin':
        modify_postgres_conf('placeholder.conf', conf_updates)
    else:
        raise ValueError('{} is not a platform this script was written for!')
