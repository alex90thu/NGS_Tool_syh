#!/usr/bin/env python3
import sys
import gzip

def process_fastq(fastq_path, barcode_dict, output_prefix):
    """处理FASTQ文件并拆分到对应barcode文件"""
    try:
        if fastq_path.endswith('.gz'):
            fastq = gzip.open(fastq_path, 'rt')
        else:
            fastq = open(fastq_path, 'r')
        
        while True:
            # 读取四行一组
            header = fastq.readline().strip()
            if not header: break  # 文件结束
            sequence = fastq.readline().strip()
            sep = fastq.readline().strip()
            quality = fastq.readline().strip()
            
            # 提取barcode（前8+后8）
            if len(sequence) < 16:
                continue  # 跳过不完整序列
            bc = sequence[:8] + sequence[-8:]
            
            # 查找对应输出文件
            if bc in barcode_dict:
                output_file = barcode_dict[bc]
                output_file.write(f"{header}\n{sequence}\n{sep}\n{quality}\n")
                
    finally:
        fastq.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python split_barcode.py <barcode.txt> <input.fastq>")
        sys.exit(1)
    
    # 读取barcode文件并建立映射
    barcode_dict = {}
    with open(sys.argv[1], 'r') as f:
        for idx, line in enumerate(f):
            bc = line.strip()
            if len(bc) != 16:
                print(f"警告: 第{idx+1}行barcode长度不为16，已跳过: {bc}")
                continue
            output_name = f"barcode{idx+1}.fastq"
            barcode_dict[bc] = open(output_name, 'w')
    
    # 处理FASTQ文件
    process_fastq(sys.argv[2], barcode_dict, None)
    
    # 关闭所有输出文件
    for f in barcode_dict.values():
        f.close()

if __name__ == "__main__":
    main()
