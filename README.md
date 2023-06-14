The script is stored at

`/yerkes-cifs/runs/tools/automation/generate_cellranger_multi_run/`

A helper script to generate cellranger multi config sheets and a shell script to use them.
Useful for large projects with many samples where making sheets manually is time-consuming or error prone.
Configuring the regex expressions may not be easy, consider using https://regex101.com/ to help.

The script should only require basic python3 packages, but in the event you do not have them 
installed, you can use the `python3_environment.yml` to create a relatively minimal conda environment similar to the one
I used to test this.

The program outputs a folder of `cellranger multi` config sheets to the `--outdir` folder, as well
as a bash script to call `cellranger multi` on all the samples.

## Example program call
```
python generate_multi_runsheets.py \
  -f <path_to_fastqs> \
  -o ./auto_generated_multi_sheets/ \
  -d '{"GEX": "Gene Expression", "ADT": "Antibody Capture", "TCR": "VDJ-T"}' \
  -g <path_to_cellranger_gex_reference> \
  -a ./ADT_feature_ref.csv \
  -c tools/cellranger/cellranger-6.1.2/cellranger \
  --grouping_pattern "(?:.+\/)?.+(Capture-\d+).*?(?:_S\d+)?(?:_L\d+_)?R\d(?:_\d+)?.fastq.+"
```

## Explaining parameters

the `-d` or `--dictionary` argument is a JSON style string of a python dictionary where the keys are strings that appear in 
files to identify them as a library type (the value). So if you have files `s001_GEX_R1/2.fastq.gz`, the program will recognize
the 'GEX' and identify the feature_type as 'Gene Expression'. Values of the dictionary should be acceptable feature_types
for cellranger multi ([see their website for more details](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/fastq-input-multi)).
Robust additions of all niche options have not been added yet, but accepted values so far are
* Gene Expression
* Antibody Capture
* VDJ-B
* VDJ-T

Pattern arguments should specify a single group to extract from filenames to identify 
* **grouping_pattern**: A shared label for multiple fastqs. E.g. if you have 3 sets of files for a sample, 's001_GEX_R1/2.fastq.gz', 's001_ADT_R1/2.fastq.gz, and 's001_TCR_R1/2.fastq.gz',
  the the grouping_pattern should isolate 's001'. This will be used to generate a single config file for all these libraries, and will be the `--id` argument to `cellranger multi`. 
  There is no default, this will be specific to the names of files in your study
* **parentPath_pattern**: Pattern to extract the path to the file. The default pattern should catch most use cases, where it will grab the path upto the filename itself. The program
  automatically expands relative paths to absolute paths, so the full path should be automatically detected. 
  
  Default: `(.+\/)[^\/]+.fastq.+`
* **fileID_pattern**: The sampleName portion of the read file ([see Illumina documentation for more details](https://support.illumina.com/help/BaseSpace_OLH_009008/Content/Source/Informatics/BS/NamingConvention_FASTQ-files-swBS.htm)). Assuming the files follow the Illumina naming conventions, the default should capture this
  
  Default: `(?:.+\/)?([^\/]+?)(?:_S\d+)?(?:_L\d+_)?R\d(?:_\d+)?.fastq.+` 

## Future goals
* Allow dictionary keys to be regex patterns rather than just strings
* Add support for other feature_types
