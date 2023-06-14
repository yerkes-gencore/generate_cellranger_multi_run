A helper script to generate cellranger multi config sheets and a shell script to use them.
Useful for large projects with many samples where making sheets manually is time-consuming or error prone.
Configuring the regex expressions may not be easy, consider using https://regex101.com/ to help.

The script should only require basic python3 packages, but in the event you do not have them 
installed, you can use the `python3_environment.yml` to create a relatively minimal conda environment similar to the one
I used to test this.

Example program call:
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

The program outputs a folder of `cellranger multi` config sheets to the `--outdir` folder, as well
as a bash script to call `cellranger multi` on all the samples.
