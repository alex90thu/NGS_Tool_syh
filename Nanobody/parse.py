#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASTA序列统计工具
统计FASTA文件中不同序列的数量，并生成包含序列、条数和百分比的表格
"""
import sys
import argparse
import gzip
import time
from collections import defaultdict
from typing import Dict, List, Tuple
import csv

def detect_file_type(filename: str) -> str:
    """检测文件类型"""
    if filename.endswith('.gz'):
        return 'gzip'
    elif filename.endswith('.fasta') or filename.endswith('.fa') or filename.endswith('.fna'):
        return 'fasta'
    elif filename.endswith('.fastq') or filename.endswith('.fq'):
        return 'fastq'
    else:
        # 尝试通过文件内容判断
        with open(filename, 'rb') as f:
            magic = f.read(2)
        if magic == b'\x1f\x8b':  # gzip magic number
            return 'gzip'
        else:
            return 'fasta'  # 默认按FASTA处理

def read_fasta_sequences(filepath: str) -> Tuple[List[str], int]:
    """
    高效读取FASTA文件中的所有序列
    
    参数:
        filepath: FASTA文件路径
    返回:
        (序列列表, 序列总数)
    """
    sequences = []
    current_sequence = []
    total_sequences = 0
    
    # 检测文件类型并选择合适的打开方式
    file_type = detect_file_type(filepath)
    
    if file_type == 'gzip':
        open_func = gzip.open
        mode = 'rt'
    else:
        open_func = open
        mode = 'r'
    
    with open_func(filepath, mode) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('>'):
                # 保存上一条序列
                if current_sequence:
                    sequences.append(''.join(current_sequence))
                    total_sequences += 1
                    current_sequence = []
            else:
                # 移除序列中的空白字符和数字（可选，根据需求调整）
                seq_line = ''.join(c for c in line if c.isalpha())
                if seq_line:  # 只添加非空的行
                    current_sequence.append(seq_line.upper())  # 统一转为大写
    
    # 添加最后一条序列
    if current_sequence:
        sequences.append(''.join(current_sequence))
        total_sequences += 1
    
    return sequences, total_sequences

def count_sequences_fast(sequences: List[str]) -> Dict[str, int]:
    """
    快速统计序列出现的次数
    
    参数:
        sequences: 序列列表
    返回:
        序列到计数的字典映射
    """
    sequence_counts = defaultdict(int)
    
    for seq in sequences:
        sequence_counts[seq] += 1
    
    return sequence_counts

def calculate_statistics(sequence_counts: Dict[str, int], total_sequences: int) -> List[Tuple[str, int, float]]:
    """
    计算序列统计信息
    
    参数:
        sequence_counts: 序列计数字典
        total_sequences: 总序列数
    返回:
        包含(序列, 条数, 百分比)的列表，按条数降序排序
    """
    stats = []
    
    for seq, count in sequence_counts.items():
        percentage = (count / total_sequences) * 100 if total_sequences > 0 else 0
        stats.append((seq, count, percentage))
    
    # 按条数降序排序
    stats.sort(key=lambda x: x[1], reverse=True)
    
    return stats

def write_statistics_table(stats: List[Tuple[str, int, float]], output_file: str, 
                          format: str = 'csv', min_percentage: float = 0.0) -> None:
    """
    将统计结果写入表格文件
    
    参数:
        stats: 统计信息列表
        output_file: 输出文件路径
        format: 输出格式 ('csv', 'tsv', 'txt')
        min_percentage: 最小百分比阈值，低于此值的序列将被过滤
    """
    # 过滤低于阈值的序列
    if min_percentage > 0:
        stats = [(seq, count, perc) for seq, count, perc in stats if perc >= min_percentage]
    
    if format == 'csv':
        delimiter = ','
    elif format == 'tsv':
        delimiter = '\t'
    else:  # txt
        delimiter = '\t'
    
    with open(output_file, 'w', newline='') as f:
        if format == 'csv':
            writer = csv.writer(f)
        elif format == 'tsv':
            writer = csv.writer(f, delimiter='\t')
        else:  # txt
            writer = csv.writer(f, delimiter='\t')
        
        # 写入表头
        writer.writerow(['Sequence', 'Count', 'Percentage(%)'])
        
        # 写入数据
        for seq, count, percentage in stats:
            writer.writerow([seq, count, f"{percentage:.4f}"])

def process_fasta_file(input_file: str, output_file: str, format: str = 'csv', 
                      min_percentage: float = 0.0, verbose: bool = False) -> Dict:
    """
    处理FASTA文件并生成统计表格
    
    参数:
        input_file: 输入FASTA文件路径
        output_file: 输出表格文件路径
        format: 输出格式 ('csv', 'tsv', 'txt')
        min_percentage: 最小百分比阈值
        verbose: 是否显示详细处理信息
    返回:
        包含统计信息的字典
    """
    start_time = time.time()
    
    if verbose:
        print(f"开始处理文件: {input_file}")
        print("正在读取序列...")
    
    # 1. 读取序列
    read_start = time.time()
    sequences, total_sequences = read_fasta_sequences(input_file)
    read_time = time.time() - read_start
    
    if verbose:
        print(f"读取完成: 共 {total_sequences} 条序列，耗时 {read_time:.2f} 秒")
        print("正在统计序列出现次数...")
    
    # 2. 统计序列
    count_start = time.time()
    sequence_counts = count_sequences_fast(sequences)
    count_time = time.time() - count_start
    
    unique_sequences = len(sequence_counts)
    
    if verbose:
        print(f"统计完成: 共 {unique_sequences} 种不同序列，耗时 {count_time:.2f} 秒")
        print("正在计算百分比并排序...")
    
    # 3. 计算统计信息
    calc_start = time.time()
    stats = calculate_statistics(sequence_counts, total_sequences)
    calc_time = time.time() - calc_start
    
    if verbose:
        print(f"计算完成: 耗时 {calc_time:.2f} 秒")
        print(f"正在写入统计表格 ({format.upper()}格式)...")
    
    # 4. 写入输出文件
    write_start = time.time()
    write_statistics_table(stats, output_file, format, min_percentage)
    write_time = time.time() - write_start
    
    total_time = time.time() - start_time
    
    # 汇总统计信息
    summary = {
        'total_sequences': total_sequences,
        'unique_sequences': unique_sequences,
        'duplication_rate': (1 - unique_sequences / total_sequences) * 100 if total_sequences > 0 else 0,
        'top_sequence': stats[0][0][:50] + "..." if len(stats) > 0 and len(stats[0][0]) > 50 else stats[0][0] if stats else "",
        'top_count': stats[0][1] if stats else 0,
        'top_percentage': stats[0][2] if stats else 0,
        'read_time': read_time,
        'count_time': count_time,
        'calc_time': calc_time,
        'write_time': write_time,
        'total_time': total_time
    }
    
    if verbose:
        print(f"写入完成: 耗时 {write_time:.2f} 秒")
        print(f"总处理时间: {total_time:.2f} 秒")
    
    return summary

def create_test_fasta(filepath: str, num_sequences: int = 1000) -> None:
    """
    创建测试FASTA文件
    
    参数:
        filepath: 测试文件路径
        num_sequences: 序列数量
    """
    import random
    import string
    
    # 定义一些测试序列
    test_sequences = [
        "ATCG" * 10,  # 重复序列
        "GCTA" * 10,
        "AAAA" * 10,
        "CCCC" * 10,
        "GGGG" * 10,
        "TTTT" * 10,
        "ACGT" * 10,
        "TGCA" * 10,
    ]
    
    with open(filepath, 'w') as f:
        for i in range(num_sequences):
            # 从测试序列中随机选择一个，或者生成随机序列
            if random.random() < 0.7:  # 70%的概率使用预定义序列
                seq = random.choice(test_sequences)
            else:  # 30%的概率生成随机序列
                length = random.randint(20, 100)
                seq = ''.join(random.choices("ATCG", k=length))
            
            f.write(f">sequence_{i+1}_length_{len(seq)}\n")
            
            # 每行写入60个字符
            for j in range(0, len(seq), 60):
                f.write(seq[j:j+60] + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='统计FASTA文件中不同序列的数量并生成统计表格',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python fasta_sequence_stats.py input.fasta output.csv
  python fasta_sequence_stats.py input.fasta output.tsv --format tsv
  python fasta_sequence_stats.py input.fasta.gz output.csv --min_percentage 0.1
  python fasta_sequence_stats.py input.fa output.txt --format txt --verbose
  python fasta_sequence_stats.py --test  # 生成测试数据并运行示例
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='输入FASTA文件路径（支持.gz压缩格式）')
    parser.add_argument('output_file', nargs='?', help='输出表格文件路径')
    parser.add_argument('--format', choices=['csv', 'tsv', 'txt'], default='csv',
                       help='输出格式：csv(逗号分隔), tsv(制表符分隔), txt(制表符分隔) (默认: csv)')
    parser.add_argument('--min_percentage', type=float, default=0.0,
                       help='最小百分比阈值，低于此值的序列将被过滤 (默认: 0.0)')
    parser.add_argument('--verbose', action='store_true',
                       help='显示详细处理信息')
    parser.add_argument('--test', action='store_true',
                       help='生成测试数据并运行示例')
    
    args = parser.parse_args()
    
    # 测试模式
    if args.test:
        print("生成测试数据...")
        test_input = "test_sequences.fasta"
        test_output = "test_output.csv"
        
        # 创建测试FASTA文件
        create_test_fasta(test_input, num_sequences=1000)
        print(f"已创建测试文件: {test_input}")
        
        # 使用测试数据运行
        print("\n开始处理测试文件...")
        summary = process_fasta_file(test_input, test_output, 'csv', 0.0, True)
        
        # 输出统计摘要
        print("\n" + "="*60)
        print("测试运行结果摘要")
        print("="*60)
        print(f"总序列条数: {summary['total_sequences']:,}")
        print(f"不同序列种类: {summary['unique_sequences']:,}")
        print(f"重复率: {summary['duplication_rate']:.2f}%")
        if summary['unique_sequences'] > 0:
            print(f"最频繁序列: {summary['top_sequence']}")
            print(f"  出现次数: {summary['top_count']:,}")
            print(f"  占比: {summary['top_percentage']:.4f}%")
        print(f"总处理时间: {summary['total_time']:.2f}秒")
        print(f"处理速度: {summary['total_sequences']/summary['total_time']:.0f} 条/秒" 
              if summary['total_time'] > 0 else "处理速度: N/A")
        print("="*60)
        print(f"结果已保存到: {test_output}")
        return
    
    # 正常模式
    if not args.input_file or not args.output_file:
        parser.print_help()
        sys.exit(1)
    
    try:
        summary = process_fasta_file(
            args.input_file, 
            args.output_file, 
            args.format, 
            args.min_percentage, 
            args.verbose
        )
        
        # 输出统计摘要
        print("\n" + "="*60)
        print("FASTA序列统计结果摘要")
        print("="*60)
        print(f"输入文件: {args.input_file}")
        print(f"输出文件: {args.output_file} ({args.format.upper()}格式)")
        print(f"总序列条数: {summary['total_sequences']:,}")
        print(f"不同序列种类: {summary['unique_sequences']:,}")
        print(f"重复率: {summary['duplication_rate']:.2f}%")
        if summary['unique_sequences'] > 0:
            print(f"最频繁序列: {summary['top_sequence']}")
            print(f"  出现次数: {summary['top_count']:,}")
            print(f"  占比: {summary['top_percentage']:.4f}%")
        print(f"读取时间: {summary['read_time']:.2f}秒")
        print(f"统计时间: {summary['count_time']:.2f}秒")
        print(f"计算时间: {summary['calc_time']:.2f}秒")
        print(f"写入时间: {summary['write_time']:.2f}秒")
        print(f"总处理时间: {summary['total_time']:.2f}秒")
        print(f"处理速度: {summary['total_sequences']/summary['total_time']:.0f} 条/秒" 
              if summary['total_time'] > 0 else "处理速度: N/A")
        print("="*60)
        
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{args.input_file}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"处理过程中发生错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

