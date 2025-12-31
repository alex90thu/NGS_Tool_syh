# WORF-Seq Analysis Dependencies

## Required System Tools
- fastp (for quality control)
- minimap2 (for sequence alignment)
- samtools (for BAM file processing)

## Required Python Packages
- pysam (for BAM file reading)
- matplotlib (for plotting)
- numpy (for data processing)

## Installation

### System Tools (Ubuntu/Debian)
```bash
# Install fastp
wget http://opengene.org/fastp/fastp
chmod a+x ./fastp
sudo mv fastp /usr/local/bin/

# Install minimap2
wget https://github.com/lh3/minimap2/releases/download/v2.24/minimap2-2.24_x64-linux.tar.bz2
tar -xvf minimap2-2.24_x64-linux.tar.bz2
sudo cp minimap2-2.24_x64-linux/minimap2 /usr/local/bin/

# Install samtools
sudo apt-get update
sudo apt-get install samtools
```

### Python Packages
```bash
pip install pysam matplotlib numpy pandas streamlit
```

## Reference Genome
- hg38.fa file should be in the current directory or provide full path

## Usage Example
```bash
# Test with sample data
./worf_seq.bash -f sample_data -c chr6 -p 123456789 -s 100000 -b true
```

## Output Files
1. `{folder_name}_clean_1.fq.gz` - Cleaned forward reads
2. `{folder_name}_clean_2.fq.gz` - Cleaned reverse reads  
3. `{folder_name}_aligned_minimap.sorted.bam` - Sorted BAM file
4. `{folder_name}_aligned_minimap.sorted.bam.bai` - BAM index
5. `{chromosome}_{center_position}_target_region.png` - Target region plot
6. `{chromosome}_chromosome_wide_step{step_size}.png` - Chromosome-wide plot
7. `{chromosome}_{center_position}_analysis_report.txt` - Analysis summary