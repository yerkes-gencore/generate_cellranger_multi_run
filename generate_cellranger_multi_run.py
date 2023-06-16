#!/usr/bin/env python

import glob
import re
import argparse
import os
from pathlib import Path
from sys import exit

def get_args():
    parser = argparse.ArgumentParser(
        description=
        """
        Generates cellranger multi config sheets for samples based on a dictionary of identifiers
        to indicate library types. Uses regex expressions to extract information from file paths to
        populate the config files. All patterns should have the string of interest as the primary group.
        You can use "(?:....)" to ignore a section of your pattern for group matching.
        For help generating regex strings for your files, try using https://regex101.com/.
        The string of interest should show up as 'Group 1'.
        """
    )
    parser.add_argument('-f', '--fastq_dir', 
        help = 'top level directory containing all folders with fastqs of interest',
        required=True, metavar='')
    parser.add_argument('-o', '--outdir', 
        help = 'directory to write output from this program to', 
        required=True, metavar='')
    parser.add_argument('-c', '--cellranger', 
        help = 'path to cellranger executable of desired version', 
        required=True, metavar='')
    parser.add_argument('--grouping_pattern', 
        help = 'Regex pattern with to extract terms to group files on', 
        required=True, metavar='')
    parser.add_argument('--fileID_pattern',
        help = "Regex pattern for extracting fastq_id from filenames. Default: r'(?:.+\/)?([^\/]+?)(?:_S\d+)?(?:_L\d+_)?R\d(?:_\d+)?.fastq.+'", 
        default = r"(?:.+\/)?([^\/]+?)(?:_S\d+)?(?:_L\d+_)?R\d(?:_\d+)?.fastq.+",
        metavar='')
    parser.add_argument('--parentPath_pattern',
        help = """Regex pattern to extract the parent directory of a file (the 'fastqs' column of the cellranger multi config). 
            Default: r'(.+\/)[^\/]+.fastq.+'""",
        default = r"(.+\/)[^\/]+.fastq.+",
        metavar='')
    parser.add_argument('--GEX_pattern', help = 'Regex pattern to identify files for gene expression library')
    parser.add_argument('--ADT_pattern', help = 'Regex pattern to identify files for antibody capture library')
    parser.add_argument('--VDJ_pattern', help = 'Regex pattern to identify files for VDJ library')
    parser.add_argument('--GEX_reference', help = 'cellranger reference for gene expression libraries', metavar='')
    parser.add_argument('--ADT_reference', help = 'csv reference for ADT libraries', metavar='')
    parser.add_argument('--VDJ_reference', help = 'cellranger reference for VDJ libraries', metavar='')
    args = parser.parse_args()
    return args

def validate_args(args):
    # approved_libraries = ['Gene Expression', 'Antibody Capture','VDJ-B', 'VDJ-T']
    # for lib in args.dictionary.values():
    #     if lib == 'Gene Expression':
    #         if args.gex_reference is None:
    #             exit("You must pass an argument to '-g' to write files for Gene Expression libraries")
    #         else:
    #             args.gex_reference = Path(args.gex_reference).resolve()
    #     elif lib == 'Antibody Capture':
    #         if args.adt_reference is None:
    #             exit("You must pass an argument to '-a' to write files for Antibody Capture libraries")
    #         else:
    #             args.adt_reference = Path(args.adt_reference).resolve()
    #     elif lib not in approved_libraries:
    #         exit("This program can only handle the following libraries:\n" 
    #         + ', '.join(approved_libraries)
    #         + "Library '" + lib + "' not recognized")
    if args.VDJ_reference is None and args.VDJ_reference is None and args.VDJ_reference is None:
        exit('\nERROR:\nSpecify a library reference and pattern to use this program. Run the program with -h for more info.\nExiting')
    if (args.GEX_reference is None) ^ (args.GEX_pattern is None):
        exit('\nERROR:\n--GEX_pattern and --GEX_reference are mutually dependant: you need to specify both if using either.\nExiting')
    if (args.ADT_reference is None) ^ (args.ADT_pattern is None):
        exit('\nERROR:\n--ADT_pattern and --ADT_reference are mutually dependant: you need to specify both if using either.\nExiting')
    if (args.VDJ_reference is None) ^ (args.VDJ_pattern is None):
        exit('\nERROR:\n--VDJ_pattern and --VDJ_reference are mutually dependant: you need to specify both if using either.\nExiting')
    if not os.path.exists(args.outdir):
        print('Outdir not found, creating..\n')
        os.makedirs(args.outdir)
    # convert to absolute pathS
    args.fastq_dir = Path(args.fastq_dir).resolve()
    args.outdir = Path(args.outdir).resolve()
    args.cellranger = Path(args.cellranger).resolve()
    ## precompile not really necessary due to internal caching
    ## https://stackoverflow.com/questions/452104/is-it-worth-using-pythons-re-compile
    # args.grouping_pattern = re.compile(args.grouping_pattern)
    # args.fileID_pattern = re.compile(args.fileID_pattern)
    # args.parentPath_pattern = re.compile(args.parentPath_pattern)
    return args

args = get_args()
args = validate_args(args)

class FileObj:
    def __init__(self, path):
        fileID_match = re.search(args.fileID_pattern, path)
        if fileID_match:
            self.id = fileID_match.group(1)
        else:
            exit('Error with fileID_pattern, not able to extract group from file:\n' + path, '\nExiting')
        parent_path_match = re.search(args.parentPath_pattern, path)
        if parent_path_match:
            self.parent_path = parent_path_match.group(1)
        else:
            exit('Error with parentPath_pattern, not able to extract group from file:\n' + path, '\nExiting')
        group_match = re.search(args.grouping_pattern, path)
        if group_match:
            self.group = group_match.group(1)
        else:
            exit('Error with grouping_pattern, not able to extract group from file:\n' + path, '\nExiting')
        self.library = self.detect_library()

    def detect_library(self):
        library = ''
        for lib, pattern in {
            'Gene Expression': args.GEX_pattern,
            'Antibody Capture': args.ADT_pattern,
            'VDJ': args.VDJ_pattern
            }.items():
            if re.search(pattern, self.id):
                if library != '':
                    quit(
                    """
                    Library patterns not unique enough. File: 
                        {} 
                    matched for multiple libraries
                    Reconfigure the pattenrns argument and try rerunning.
                    """.format(self.id))
                library = lib
        if library == '':
            print('Library type not detected for sample:\n' 
            + self.id 
            + '\nYou may have to manually edit the config or check your dictionary argument\n')
        return library


class FileGroup:
    def __init__(self, name):
        self.name = name
        self.files = []
        self.libraries = set()
    def add_file(self, file):
        self.files.append(file)
        self.libraries.add(file.library)

def group_fastqs(fastqs):
    grouped_files = {}
    for fastq in fastqs:
        file = FileObj(fastq)
        if file.group not in grouped_files.keys():
            grouped_files[file.group] = FileGroup(file.group)
        grouped_files[file.group].add_file(file)
    return grouped_files

def write_sample_sheets(file_groups, gex_ref, adt_ref, vdj_ref, output_dir):
    sheets = {}
    for sample, file_group in file_groups.items():
        filename = Path(output_dir,str(sample + '_multi_config_auto.csv'))
        with open(filename, 'w') as fo:
            if 'Gene Expression' in file_group.libraries:
                fo.writelines([
                    '[gene-expression]\n',
                    'reference,', str(gex_ref), '\n',
                    'no-bam,true\n',
                    '\n',
                ])
            if 'Antibody Capture' in file_group.libraries:
                fo.writelines([
                    '[feature] # For Feature Barcode libraries only\n',
                    'reference,', str(adt_ref), '\n',
                    '\n'
                ])
            if 'VDJ-T' in file_group.libraries or 'VDJ-B' in file_group.libraries:
                fo.writelines([
                    '[vdj]\n',
                    'reference,', str(vdj_ref), '\n',
                    '\n'
                ])
            fo.writelines(['[libraries]\n', 'fastq_id,fastqs,feature_types\n'])
            ## Track written filegroups to avoid writing multiple lines for multiple lanes
            used_files = []
            for file in file_group.files:
                if file.id not in used_files:
                    fo.writelines(','.join([file.id, file.parent_path, file.library]) + '\n')
                used_files.append(file.id)
        sheets[sample] = filename
    return sheets

def write_shell_script(sheets, cellranger_path, filename = 'run_cellranger_auto.sh'):
    with open(Path(args.outdir, filename), 'w') as sh:
        sh.write('#!/usr/bin/bash\n\n')
        for sample, config in sheets.items():
            sh.writelines(str(cellranger_path) + ' multi --id ' + sample + ' --csv ' + str(config) + '\n')

## apparently a known issue that glob.glob with a pathlib.Path won't follow symlinks?
## casting as string
## https://bugs.python.org/issue33428
fastqs = glob.glob(str(Path(args.fastq_dir, '**/*R1*fastq*')), recursive=True)
grouped_files = group_fastqs(fastqs)   
config_sheets = write_sample_sheets(grouped_files, 
    gex_ref=args.gex_reference, 
    adt_ref=args.adt_reference, 
    output_dir = args.outdir,
    vdj_ref = args.vdj_reference)
write_shell_script(config_sheets, cellranger_path=args.cellranger)

print('\nProgram completed successfully')
