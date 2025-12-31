#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import argparse
from typing import Iterator, Tuple, Optional
import gzip
import time

def fasta_reader(filepath: str) -> Iterator[Tuple[str, str]]:
    """
    高效读取FASTA文件的生成器函数，支持普通文本和gzip压缩格式
    
    参数:
        filepath: FASTA文件路径（支持.txt, .fasta, .fa, .gz格式）
    返回:
        生成器，每次产生(header, sequence)元组
    """
    open_func = gzip.open if filepath.endswith('.gz') else open
    mode = 'rt' if filepath.endswith('.gz') else 'r'
    
    with open_func(filepath, mode) as f:
        header = ''
        sequence_lines = []
        
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
                
            if line.startswith('>'):
                if header:
                    yield header, ''.join(sequence_lines)
                header = line
                sequence_lines = []
            else:
                sequence_lines.append(line)
        
        if header:
            yield header, ''.join(sequence_lines)

def extract_fragment(sequence: str, start_marker: str, end_marker: str, 
                     allow_overlap: bool = False) -> Optional[str]:
    """
    从序列中提取从start_marker到end_marker的片段
    
    参数:
        sequence: 输入序列
        start_marker: 起始标记序列
        end_marker: 结束标记序列
        allow_overlap: 是否允许起始和结束标记重叠
    返回:
        提取的片段，如果未找到则返回None
    """
    start_len = len(start_marker)
    end_len = len(end_marker)
    
    # 搜索起始标记的所有出现位置
    start_pos = 0
    while True:
        start_idx = sequence.find(start_marker, start_pos)
        if start_idx == -1:
            break
        
        # 搜索结束标记
        search_start = start_idx + (0 if allow_overlap else start_len)
        end_idx = sequence.find(end_marker, search_start)
        
        if end_idx != -1:
            # 返回从起始标记开始到结束标记结束的完整片段
            fragment_end = end_idx + end_len
            return sequence[start_idx:fragment_end]
        
        # 继续搜索下一个起始标记
        start_pos = start_idx + 1
    
    return None

def process_fasta(input_file: str, output_file: str, 
                  start_marker: str = "TGTACCTGCAGATGA", 
                  end_marker: str = "GTGACCGTGTCTTCT",
                  min_length: int = 0,
                  max_length: int = 0,
                  allow_overlap: bool = False,
                  verbose: bool = False) -> Tuple[int, int, float]:
    """
    处理FASTA文件，提取指定标记间的序列
    
    参数:
        input_file: 输入FASTA文件路径
        output_file: 输出FASTA文件路径
        start_marker: 起始标记序列
        end_marker: 结束标记序列
        min_length: 最小片段长度，0表示不限制
        max_length: 最大片段长度，0表示不限制
        allow_overlap: 是否允许起始和结束标记重叠
        verbose: 是否显示处理进度
    返回:
        (处理的序列总数, 提取的片段数, 处理时间)
    """
    start_time = time.time()
    total_sequences = 0
    extracted_fragments = 0
    
    with open(output_file, 'w') as fout:
        for header, sequence in fasta_reader(input_file):
            total_sequences += 1
            
            fragment = extract_fragment(sequence, start_marker, end_marker, allow_overlap)
            
            if fragment:
                # 检查长度限制
                frag_len = len(fragment)
                if (min_length == 0 or frag_len >= min_length) and \
                   (max_length == 0 or frag_len <= max_length):
                    
                    # 写入结果
                    fout.write(f"{header} | extracted_{frag_len}bp_fragment\n")
                    
                    # 每行80个字符写入序列
                    for i in range(0, frag_len, 80):
                        fout.write(fragment[i:i+80] + "\n")
                    
                    extracted_fragments += 1
                    
                    if verbose and extracted_fragments % 1000 == 0:
                        elapsed = time.time() - start_time
                        print(f"已处理 {total_sequences} 条序列，提取 {extracted_fragments} 个片段 "
                              f"({elapsed:.2f} 秒)", file=sys.stderr)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    return total_sequences, extracted_fragments, processing_time

def main():
    parser = argparse.ArgumentParser(
        description="从FASTA文件中提取从起始标记到结束标记的序列片段",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.fasta output.fasta
  %(prog)s input.fasta output.fasta --start_marker TGTACCTGCAGATGA --end_marker GTGACCGTGTCTTCT
  %(prog)s input.fasta.gz output.fasta --min_length 50 --max_length 200 --verbose
        """
    )
    
    parser.add_argument("input_file", help="输入FASTA文件（支持.gz压缩格式）")
    parser.add_argument("output_file", help="输出FASTA文件")
    parser.add_argument("--start_marker", default="TGTACCTGCAGATGA",
                       help=f"起始标记序列（默认：TGTACCTGCAGATGA）")
    parser.add_argument("--end_marker", default="GTGACCGTGTCTTCT",
                       help=f"结束标记序列（默认：GTGACCGTGTCTTCT）")
    parser.add_argument("--min_length", type=int, default=0,
                       help="最小片段长度，0表示不限制（默认：0）")
    parser.add_argument("--max_length", type=int, default=0,
                       help="最大片段长度，0表示不限制（默认：0）")
    parser.add_argument("--allow_overlap", action="store_true",
                       help="允许起始和结束标记重叠（默认：不允许）")
    parser.add_argument("--verbose", action="store_true",
                       help="显示处理进度信息")
    
    args = parser.parse_args()
    
    print(f"处理文件: {args.input_file}", file=sys.stderr)
    print(f"起始标记: {args.start_marker}", file=sys.stderr)
    print(f"结束标记: {args.end_marker}", file=sys.stderr)
    print(f"最小长度: {'不限制' if args.min_length == 0 else args.min_length}", file=sys.stderr)
    print(f"最大长度: {'不限制' if args.max_length == 0 else args.max_length}", file=sys.stderr)
    print(f"允许重叠: {'是' if args.allow_overlap else '否'}", file=sys.stderr)
    print("-" * 50, file=sys.stderr)
    
    try:
        total, extracted, processing_time = process_fasta(
            args.input_file, 
            args.output_file,
            args.start_marker,
            args.end_marker,
            args.min_length,
            args.max_length,
            args.allow_overlap,
            args.verbose
        )
        
        print(f"\n处理完成！", file=sys.stderr)
        print(f"处理序列总数: {total}", file=sys.stderr)
        print(f"提取片段数量: {extracted}", file=sys.stderr)
        print(f"提取成功率: {extracted/total*100:.2f}%" if total > 0 else "0.00%", file=sys.stderr)
        print(f"处理时间: {processing_time:.2f} 秒", file=sys.stderr)
        print(f"平均速度: {total/processing_time:.2f} 条序列/秒" if processing_time > 0 else "0.00 条序列/秒", file=sys.stderr)
        print(f"结果保存至: {args.output_file}", file=sys.stderr)
        
    except FileNotFoundError:
        print(f"错误：找不到输入文件 '{args.input_file}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"处理过程中发生错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

