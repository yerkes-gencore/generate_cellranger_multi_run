A helper script to generate cellranger multi config sheets and a shell script to use them.
Useful for large projects with many samples where making sheets manually is time-consuming or error prone.
Configuring the regex expressions may not be easy, consider using https://regex101.com/ to help.

The script should only require basic python3 packages, but in the event you do not have them 
installed, you can use the `python3_environment.yml` to create a relatively minimal conda environment similar to the one
I used to test this.

The program outputs a folder of `cellranger multi` config sheets to the `--outdir` folder, as well
as a bash script to call `cellranger multi` on all the samples.

The script is stored at

`/yerkes-cifs/runs/tools/automation/generate_cellranger_multi_run/`

## Example program call
```
python generate_multi_runsheets.py \
  -f <path_to_fastqs> \
  -o ./auto_generated_multi_sheets/ \
  --GEX_reference /yerkes-cifs/runs/Genome_references/homo_sapiens/10X/refdata-gex-GRCh38-2020-A \
  --ADT_reference /yerkes-cifs/runs/Analysis/2023_Analyses/p23077_Julia/p23077_Julia_Processing/p23077_Julia_vdj_feature_ref.csv \
  --GEX_pattern 'GEX' \
  --ADT_pattern 'CITE \
  -c /yerkes-cifs/runs/tools/cellranger/cellranger-7.1.0/cellranger \
  --grouping_pattern "(?:.+\/)?.+(p23144-s\d+_MGUS-Rifax-\d+.).*?(?:_S\d+)?(?:_L\d+_)?R\d(?:_\d+)?.fastq.+" 
  
```

## Explaining parameters

The `GEX/ADT/VDJ_pattern` arguments specify regex patterns used to identify fastqs for those respective libraries. If a run doesn't have one of
those libraries, you don't need to specify a pattern argument. If you do specify a pattern for a library, you are also required to specify
a path to the reference used for that library, e.g. `--GEX_reference`

Pattern arguments should specify a single group to extract from filenames to identify the required information. Paths are converted to absolute paths within the program, so 
patterns should be conscious of possible matches in the full path. Only the `grouping_pattern` doesn't have a default. The others have defaults that should suffice in most cases.

* **grouping_pattern**: A shared label (sample ID) for multiple fastqs. E.g. if you have 3 sets of files for a sample, 's001_GEX_R1/2.fastq.gz', 's001_ADT_R1/2.fastq.gz, and 's001_TCR_R1/2.fastq.gz',
  the the grouping_pattern should isolate 's\d+'. This will be used to generate a single config file for all these libraries, and will be the `--id` argument to `cellranger multi`. 
  There is no default, this will be specific to the names of files in your study. The pattern shown in the example above is overly verbose, and you don't need to be that
  specific, but you can use it as a template. It is agnostic to relative/absolute paths and Illumina identifiers in the filename, so you only need to substitute the second group with
  the pattern for your files. 
* **parentPath_pattern**: Pattern to extract the path to the file. The default pattern should catch most use cases, where it will grab the path upto the filename itself. The program
  automatically expands relative paths to absolute paths, so the full path should be automatically detected. 
  
  Default: `(.+\/)[^\/]+.fastq.+`
* **fileID_pattern**: The sampleName portion of the read file ([see Illumina documentation for more details](https://support.illumina.com/help/BaseSpace_OLH_009008/Content/Source/Informatics/BS/NamingConvention_FASTQ-files-swBS.htm)). Assuming the files follow the Illumina naming conventions, the default should capture this
  
  Default: `(?:.+\/)?([^\/]+?)(?:_S\d+)?(?:_L\d+_)?R\d(?:_\d+)?.fastq.+` 

## Future goals
* Add support for other feature_types
