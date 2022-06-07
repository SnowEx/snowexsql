'''
Edits the postgres conf file
'''
import os
import platform
from subprocess import check_output
import argparse

from snowexsql.utilities import find_kw_in_lines


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
    for k, v in entries.items():

        i = find_kw_in_lines(k, lines)

        if i != -1:
            # Found the option in the file, try to replace the value and keep
            # the comment
            print('\tUpdating {}...'.format(k))
            info = lines[i].split('=')
            name = info[0].replace('#', '').strip()
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
    with open(temp, 'w+') as fp:
        fp.write(''.join(lines))
        fp.close()

    # Move the file using sudo so we dont have to execute this script with sudo
    check_output(['sudo', 'mv', os.path.abspath(temp), conf_file])


if __name__ == '__main__':
    # Modify and output the conf file to its original location
    # Settings semi based on
    # https://postgis.net/workshops/postgis-intro/tuning.html

    parser = argparse.ArgumentParser(description='Modify postgres configuration')
    parser.add_argument(
        '-vsi', '--gdal_vsi_options', dest="vsi_opts", type=str, nargs="+",
        default=[], required=False,
        help='list of gdal_vsi_options for the config. \n'
             'Example: -vsi AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY=<key>'
    )

    args = parser.parse_args()
    vsi_opts = args.vsi_opts
    extra_opts = {}
    if vsi_opts:
        extra_opts["postgis.gdal_vsi_options"] = " ".join(vsi_opts)

    conf_updates = {'shared_buffers': '500MB',
                    'work_mem': "3000MB",
                    'maintenance_work_mem': '128MB',
                    'wal_buffers': '1MB',
                    'random_page_cost': '2.0',
                    'postgis.enable_outdb_rasters': 1,
                    'postgis.gdal_enabled_drivers': "'ENABLE_ALL'",
                    **extra_opts
                    }

    this_os = platform.system().lower()

    # Manage the os
    if this_os == 'linux':
        modify_postgres_conf(
            '/etc/postgresql/14/main/postgresql.conf',
            conf_updates)
    elif this_os == 'darwin':
        modify_postgres_conf(
            '/usr/local/var/postgres/postgresql.conf',
            conf_updates)
    else:
        raise ValueError('{} is not a platform this script was written for!')
