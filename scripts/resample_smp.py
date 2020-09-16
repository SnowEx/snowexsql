'''
Resample the SMP profiles to every 100 value

Download from https://osu.app.box.com/s/7yq08y1mqpl9evgz6rfw8hu771228ryn

Unzip to ~/Downloads

usage:
    python resample_smp.py
'''
from os.path import join, abspath, expanduser, isdir, dirname, basename
from os import listdir, mkdir
from snowxsql.batch import UploadProfileBatch
from snowxsql.utilities import get_logger
import pandas as pd
import shutil
import matplotlib.pyplot as plt
from snowxsql.utilities import read_n_lines

def open_df(smp_f, header_pos=6):
    '''
    reads in dataframe with skipping the header

    Args:
        smp_f: CSV of an SMP profile
        header_pos: Integer representing the number of lines the header info is
    Returns:
        df: Pandas dataframe containing the SMP profile
    '''
    df = pd.read_csv(smp_f, header=header_pos)
    return df


def subsample(df, ith):
    '''
    Returns a dataframe resampled to every ith point of the original

    Args:
        df: Pandas Dataframe containing a SMP profile
        ith: The number to grab a sample, e.g. every 100 samples
    Returns:
        new_df: Pandas dataframe subsampled to every ith sample of the original. The original index is include for each value
    '''

    idx = df.groupby(df.index//ith).idxmax()['Depth (mm)']
    new_df = df.loc[idx]

    return new_df

def make_comparison(f):
    '''
    Plots the differences in resampling and precision cutting

    Args:
        f: csv with 6 lines of header for an SMP profile
    '''
    df = open_df(f)

    depth_precision = [0, 1, 3]
    force_precision = [1, 3, 5]
    downsample = 100

    fig, axes = plt.subplots(1, len(depth_precision) + 1)
    i = 0

    new = subsample(df, downsample)

    for d_p, f_p in zip(depth_precision, force_precision):
        ax = axes[i]

        # Deal with precision
        new_df = new.round({'Depth (mm)':d_p, 'Force (N)':f_p})

        ax.plot(df['Force (N)'], df['Depth (mm)'], label='Raw')
        ax.plot(new_df['Force (N)'], new_df['Depth (mm)'], label='Resampled + precision cut')
        ax.set_title('Depth precision = {}, Force precision = {}'.format(d_p, f_p))
        ax.legend()
        i += 1

    ax = axes[i]
    ax.plot(df['Force (N)'], df['Depth (mm)'], label='Raw')
    ax.plot(new['Force (N)'], new_df['Depth (mm)'], label='Resampled + No Precision cut')
    ax.legend()
    ax.set_title('Original Precision'.format(d_p, f_p))
    plt.show()


def resample_batch(filenames, output, downsample, header_pos=6, clean_on_start=True):
    '''
    Resample all the file names and save to the output dir

    Args:
        filenames: List of smp csv files needed to be subsampled
        output: directory to output files to
        downsample: Number of samples to subsample at (e.g. downsample=100 is subsampled to every 100th sample)
        clean_on_start: Remove the output folder at the start when running
    '''

    log = get_logger('SMP Resample')

    if clean_on_start:
        shutil.rmtree(output)

    if not isdir(output):
        log.info('Making output folder {}'.format(output))
        mkdir(output)

    log.info('Resampling {} SMP profiles...'.format(len(filenames)))

    # Loop over all the files, name them using the same name just using a different folder
    for f in filenames:
        base_f = basename(f)

        log.info('Resampling {}'.format(base_f))

        # Open the file for the header and grab it as a list
        header = read_n_lines(f, header_pos)

        # Open the file as a dataframe excluding the header
        df = open_df(f, header_pos=header_pos)

        # Grab every 100th sample
        new_df = subsample(df, downsample)

        # Reduce the precision of the original data without much effect
        new_df = new_df.round({'Depth (mm)':1, 'Force (N)':3})
        out_f = join(output, base_f)

        # Write out the original header add some information
        with open(out_f,'w') as fp:

            # Rename the original total samples
            original_samples = header[-1].split(":")[-1]
            header[-1] = '# Original Total Samples: {}'.format(original_samples)

            # Add a header for the fact this data is subsampled
            header.append('# Data Subsampled To: Every {:d}th\n'.format(downsample))
            lines = ''.join(header)
            fp.write(lines)
            fp.close()

        new_df.to_csv(out_f, index_label='Original Index', mode='a')


def main():

    # comparison flag produces the figures to show the impact of the resampling
    making_comparison = False
    downsample = 100
    header_pos = 6
    log = get_logger('SMP Resample')
    log.info('Preparing to resample smp profiles for uploading...')

    # Obtain a list of Grand mesa smp files
    directory = abspath(expanduser('~/Downloads/NSIDC-upload/'))
    smp_data = join(directory,'level_1_data', 'csv')
    filenames = [join(smp_data, f) for f in listdir(smp_data) if f.split('.')[-1]=='CSV']

    # Are we making the plot to show the comparison of the effects?
    if making_comparison:
        make_comparison(filenames[0])

    else:
        # output location
        output = join(dirname(smp_data),'csv_resampled')

        if isdir(output):
            ans = input('\nWARNING! You are about overwrite {} previously resampled files '
                        'located at {}!\nPress Y to continue and any other '
                        'key to abort: '.format(len(filenames), output))

            if ans.lower() == 'y':
                resample_batch(filenames, output, downsample, header_pos=header_pos)
            else:
                log.warning('Skipping resample and overwriting of resampled files...')
        else:
            mkdir(output)
            resample_batch(filenames, output, downsample, header_pos=header_pos)


if __name__ == '__main__':
    main()
