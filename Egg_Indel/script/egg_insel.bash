#!/bin/bash

# 测序数据分析自动化pipeline
# 作者: 自动生成
# 描述: 自动化处理测序数据的CRISPResso分析流程

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
print_help() {
    echo -e "${BLUE}测序数据分析自动化pipeline${NC}"
    echo "用法: $0 -a 序列1路径 -b 序列2路径 -c barcode文件 -d 工作名称 -w 窗口大小"
    echo ""
    echo "参数说明:"
    echo "  -a, --seq1       测序得到的序列1文件路径"
    echo "  -b, --seq2       测序得到的序列2文件路径"
    echo "  -c, --barcode    barcode列表文件路径"
    echo "  -d, --name       工作名称(用于输出文件命名)"
    echo "  -w, --window     qualification window大小(整数, 默认: 15)"
    echo "  -h, --help       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -a sample_R1.fastq.gz -b sample_R2.fastq.gz -c barcodes.txt -d MyExperiment -w 20"
    echo ""
    echo "注意事项:"
    echo "  1. 确保已安装并配置好以下工具:"
    echo "     - conda (crispresso2_env环境)"
    echo "     - gunzip"
    echo "     - flash"
    echo "     - seqkit"
    echo "     - CRISPResso2"
    echo "  2. 脚本应在测序序列的文件夹下执行"
    echo "  3. barcode文件应为每行一个barcode的文本文件"
    exit 0
}

# 错误处理函数
error_exit() {
    echo -e "${RED}错误: $1${NC}" >&2
    echo -e "${YELLOW}执行失败，清理临时文件...${NC}"
    
    # 清理可能的部分生成文件
    [ -f "${WORK_NAME}.extendedFrags.fastq" ] && rm -f "${WORK_NAME}.extendedFrags.fastq"
    # 清理动态生成的barcode文件（如果存在）
    for barcode_file in temp_barcode_*.txt temp_barcode_*.txt.copy; do
        [ -f "$barcode_file" ] && rm -f "$barcode_file"
    done
    # 保留原有的barcode.txt清理逻辑（兼容性）
    [ -f "barcode.txt" ] && [ "${BARCODE_FILE}" != "barcode.txt" ] && rm -f barcode.txt
    [ -f "barcode.txt.copy" ] && rm -f barcode.txt.copy
    
    exit 1
}

# 进度信息函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查文件是否存在
check_file() {
    if [ ! -f "$1" ]; then
        error_exit "文件不存在: $1"
    fi
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        error_exit "未找到命令: $1，请确保已正确安装"
    fi
}

# 检查数字参数
check_number() {
    if ! [[ "$1" =~ ^[0-9]+$ ]]; then
        error_exit "参数必须为正整数: $2"
    fi
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--seq1)
                SEQ1_PATH="$2"
                shift 2
                ;;
            -b|--seq2)
                SEQ2_PATH="$2"
                shift 2
                ;;
            -c|--barcodes)
                # 以逗号分隔的barcode序号，如 "1,2,3,4,5"
                IFS=',' read -ra BARCODE_SELECTED <<< "$2"
                shift 2
                ;;
            -d|--name)
                WORK_NAME="$2"
                shift 2
                ;;
            -w|--window)
                WINDOW_SIZE="$2"
                shift 2
                ;;
            -h|--help)
                print_help
                ;;
            *)
                echo -e "${RED}未知参数: $1${NC}"
                print_help
                ;;
        esac
    done
    
    # 检查必需参数
    if [ -z "$SEQ1_PATH" ] || [ -z "$SEQ2_PATH" ] || [ -z "$WORK_NAME" ]; then
        echo -e "${RED}错误: 缺少必需参数${NC}"
        print_help
    fi
    
    # 设置默认的barcode选择（如果未指定）
    if [ ${#BARCODE_SELECTED[@]} -eq 0 ]; then
        BARCODE_SELECTED=(1 2 3 4 5 6 7 8)
        print_info "未指定barcode，使用默认值: ${BARCODE_SELECTED[*]}"
    else
        print_info "用户选择的barcode: ${BARCODE_SELECTED[*]}"
    fi
    
    # 设置默认值
    [ -z "$WINDOW_SIZE" ] && WINDOW_SIZE=15
    
    # 验证数字参数
    check_number "$WINDOW_SIZE" "窗口大小"
    
    # 检查输入文件
    check_file "$SEQ1_PATH"
    check_file "$SEQ2_PATH"
    
    # 设置样品数量为选择的barcode数量
    SAMPLE_COUNT=${#BARCODE_SELECTED[@]}
    print_info "样品数量: $SAMPLE_COUNT"
}

# 主流程函数
main_pipeline() {
    print_info "开始测序数据分析流程"
    print_info "工作名称: $WORK_NAME"
    print_info "样品数量: $SAMPLE_COUNT"
    print_info "窗口大小: $WINDOW_SIZE"
    
    # 切换到测序文件所在目录
    local SEQ_DIR=$(dirname "$(realpath "$SEQ1_PATH")")
    print_info "切换到工作目录: $SEQ_DIR"
    cd "$SEQ_DIR" || error_exit "无法切换到目录: $SEQ_DIR"
    
    # 获取测序文件的文件名（不含路径）
    SEQ1_FILE=$(basename "$SEQ1_PATH")
    SEQ2_FILE=$(basename "$SEQ2_PATH")
    print_info "序列1文件: $SEQ1_FILE"
    print_info "序列2文件: $SEQ2_FILE"
    echo ""
    
    # 步骤1: 激活conda环境
    print_info "步骤1: 激活conda环境 (crispresso2_env)"
    if command -v conda &> /dev/null; then
        source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true
        if conda activate crispresso2_env 2>/dev/null; then
            print_success "成功激活crispresso2_env环境"
        else
            print_warning "无法激活crispresso2_env环境，请确保环境已创建"
            print_warning "继续执行，但CRISPResso命令可能失败"
        fi
    else
        print_warning "未找到conda命令，跳过环境激活"
    fi
    echo ""
    
    # 步骤2: FLASH拼接
    print_info "步骤2: 使用FLASH拼接序列"
    
    # 使用第一个序列文件的基础名作为FLASH输出名
    local FLASH_OUTPUT_BASE="${SEQ1_FILE%_1*}"
    print_info "FLASH输出基础名: $FLASH_OUTPUT_BASE"
    
    check_command "flash"
    print_info "执行: flash $SEQ1_FILE $SEQ2_FILE -o $FLASH_OUTPUT_BASE"
    flash "$SEQ1_FILE" "$SEQ2_FILE" -o "$FLASH_OUTPUT_BASE" || error_exit "FLASH拼接失败"
    
    if [ ! -f "${FLASH_OUTPUT_BASE}.extendedFrags.fastq" ]; then
        error_exit "FLASH输出文件未找到: ${FLASH_OUTPUT_BASE}.extendedFrags.fastq"
    fi
    
    # 设置实际生成的文件名供后续步骤使用
    WORK_NAME="$FLASH_OUTPUT_BASE"
    print_info "实际工作名称: $WORK_NAME"
    print_success "FLASH拼接完成"
    echo ""
    
    # 步骤3: 生成barcode文件并拆分序列
    print_info "步骤3: 生成barcode文件并拆分序列"
    
    # 根据用户输入的barcode序号生成barcode文件
    local SELECTED_BARCODES=("${BARCODE_SELECTED[@]}")
    local BARCODE_COUNT=${#SELECTED_BARCODES[@]}
    
    print_info "用户选择了 $BARCODE_COUNT 个barcode: ${SELECTED_BARCODES[*]}"
    
    # 检查BARCODES字典文件是否存在
    local BARCODE_DICT="/home/sunyuhong/software/NGS_Tool_syh/app.py"
    if [ ! -f "$BARCODE_DICT" ]; then
        error_exit "未找到barcode字典文件: $BARCODE_DICT"
    fi
    
    # 创建临时Python脚本来生成barcode文件
    local GENERATE_SCRIPT="/tmp/generate_barcode_file.py"
    
    # 生成动态barcode文件名
    local BARCODE_FILENAME="temp_barcode_$(printf "%02d" ${SELECTED_BARCODES[0]})"
    for i in "${SELECTED_BARCODES[@]:1}"; do
        BARCODE_FILENAME="${BARCODE_FILENAME}_$(printf "%02d" $i)"
    done
    BARCODE_FILENAME="${BARCODE_FILENAME}.txt"
    
    cat > "$GENERATE_SCRIPT" << EOF
import sys
import ast

# 从app.py中提取BARCODES字典
with open('/home/sunyuhong/software/NGS_Tool_syh/app.py', 'r') as f:
    content = f.read()
    
# 找到BARCODES定义
start = content.find('BARCODES = {')
end = content.find('}', start) + 1
barcodes_str = content[start:end]

# 安全评估字典
exec(barcodes_str)

# 获取用户选择的barcode序号
selected = ast.literal_eval(sys.argv[1])

# 生成动态barcode文件名
barcode_filename = sys.argv[2]

# 生成barcode文件
with open(barcode_filename, 'w') as f:
    for num in sorted(selected):
        if str(num) in BARCODES:
            f.write(BARCODES[str(num)] + '\n')
        else:
            print(f"警告: 未找到barcode {num}")

print(f"生成了 {len(selected)} 个barcode到文件: {barcode_filename}")
EOF
    
    print_info "生成barcode文件: $BARCODE_FILENAME"
    python3 "$GENERATE_SCRIPT" "${SELECTED_BARCODES[*]}" "$BARCODE_FILENAME" || error_exit "生成barcode文件失败"
    
    # 检查生成的barcode文件
    if [ ! -f "$BARCODE_FILENAME" ]; then
        error_exit "barcode文件生成失败"
    fi
    
    local barcode_count=$(wc -l < "$BARCODE_FILENAME")
    print_info "生成的barcode数量: $barcode_count"
    
    # 备份原始barcode文件
    cp "$BARCODE_FILENAME" "$BARCODE_FILENAME.copy"
    
    # 检查Python拆分脚本是否存在
    local PYTHON_SCRIPT="/home/sunyuhong/software/NGS_Tool_syh/Egg_Indel/script/barcode_split_fastq.py"
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        error_exit "未找到Python脚本: $PYTHON_SCRIPT"
    fi
    
    print_info "执行: python $PYTHON_SCRIPT $BARCODE_FILENAME ${WORK_NAME}.extendedFrags.fastq"
    python3 "$PYTHON_SCRIPT" "$BARCODE_FILENAME" "${WORK_NAME}.extendedFrags.fastq" || error_exit "barcode拆分失败"
    
    # 检查拆分结果
    local split_count=$(ls barcode*.fastq 2>/dev/null | wc -l)
    if [ "$split_count" -eq 0 ]; then
        error_exit "barcode拆分未生成任何fastq文件"
    fi
    print_success "barcode拆分完成，生成 $split_count 个文件"
    echo ""
    
    # 步骤4: 运行CRISPResso分析
    print_info "步骤6: 运行CRISPResso分析"
    print_info "将分析 $SAMPLE_COUNT 个样品"
    
    # 定义固定的amplicon和guide序列
    local AMPLICON_SEQ="CATCTCCTCGCAGCGTCTCTGCGGGGCGGCCCCGGCTCCCTCCGCCATGGGGGCCGCGGCCCTCCGAGCCCTTCCCTGGGCTCTGCTGCTGCTGCTGGGCCCGCTGCTGCCCGGCCAGCGCTTGCAGGCCGACGCCACGCGTGTCTCCGAGCCCACCTGGGAGCAGCCGTGGGGAGAGCCCGGGGGTATCACCGCCGCCCCGCTGGCCACGGCCCAGGAGGTGCACCCGCTGAACAAACAGCACCACA"
    local GUIDE_SEQ="CCCCACGGCTGCTCCCAGGT"
    
    print_info "Amplicon序列长度: ${#AMPLICON_SEQ}"
    print_info "Guide序列: $GUIDE_SEQ"
    print_info "窗口大小: $WINDOW_SIZE"
    
    check_command "CRISPResso"
    
    for ((i=1; i<=SAMPLE_COUNT; i++)); do
        local barcode_file="barcode${i}.fastq"
        if [ ! -f "$barcode_file" ]; then
            print_warning "未找到文件: $barcode_file，跳过样品 $i"
            continue
        fi
        
        print_info "处理样品 $i/$SAMPLE_COUNT: $barcode_file"
        print_info "执行: CRISPResso --fastq_r1 $barcode_file --amplicon_seq $AMPLICON_SEQ -g $GUIDE_SEQ -n $i -w $WINDOW_SIZE"
        
        CRISPResso --fastq_r1 "$barcode_file" \
                  --amplicon_seq "$AMPLICON_SEQ" \
                  -g "$GUIDE_SEQ" \
                  -n "$i" \
                  -w "$WINDOW_SIZE" || print_warning "CRISPResso分析样品 $i 失败，继续处理下一个"
        
        echo ""
    done
    
    print_success "CRISPResso分析完成"
    echo ""
    
    # 步骤5: 打包结果
    print_info "步骤7: 打包分析结果"
    
    local result_files=$(ls -d CRISPResso_on_egg* 2>/dev/null | wc -l)
    if [ "$result_files" -eq 0 ]; then
        print_warning "未找到CRISPResso_on_egg开头的文件，无法打包"
    else
        print_info "找到 $result_files 个结果文件/目录"
        local tar_file="${WORK_NAME}_result.tar.gz"
        
        print_info "执行: tar -czf $tar_file CRISPResso_on_egg*"
        tar -czf "$tar_file" CRISPResso_on_egg* 2>/dev/null
        
        if [ -f "$tar_file" ]; then
            local tar_size=$(du -h "$tar_file" | cut -f1)
            print_success "打包完成: $tar_file (大小: $tar_size)"
        else
            print_warning "打包文件未生成"
        fi
    fi
    echo ""
    
    # 清理临时文件
    print_info "清理临时文件"
    # 清理动态生成的barcode文件
    for barcode_file in temp_barcode_*.txt temp_barcode_*.txt.copy; do
        [ -f "$barcode_file" ] && rm -f "$barcode_file"
    done
    # 保留原有的barcode.txt清理逻辑（兼容性）
    [ -f "barcode.txt.copy" ] && rm -f barcode.txt.copy
    [ -f "${WORK_NAME}.notCombined_1.fastq" ] && rm -f "${WORK_NAME}.notCombined_1.fastq"
    [ -f "${WORK_NAME}.notCombined_2.fastq" ] && rm -f "${WORK_NAME}.notCombined_2.fastq"
    [ -f "${WORK_NAME}.hist" ] && rm -f "${WORK_NAME}.hist"
    [ -f "${WORK_NAME}.histogram" ] && rm -f "${WORK_NAME}.histogram"
    
    print_success "临时文件清理完成"
    echo ""
    
    # 步骤6: 生成摘要报告
    print_info "步骤8: 生成分析摘要"
    echo "================================================"
    echo "            测序数据分析完成摘要"
    echo "================================================"
    echo "工作名称:        $WORK_NAME"
    echo "分析时间:        $(date)"
    echo "样品数量:        $SAMPLE_COUNT"
    echo "窗口大小:        $WINDOW_SIZE"
    echo ""
    echo "输入文件:"
    echo "  序列1:         $SEQ1_PATH"
    echo "  序列2:         $SEQ2_PATH"
    echo "  barcode文件:   $BARCODE_FILE"
    echo ""
    echo "输出文件:"
    echo "  FLASH输出:     ${WORK_NAME}.extendedFrags.fastq"
    echo "  barcode拆分:   共 $(ls barcode*.fastq 2>/dev/null | wc -l) 个文件"
    echo "  CRISPResso结果: 共 $result_files 个结果目录"
    
    if [ -f "${WORK_NAME}_result.tar.gz" ]; then
        echo "  打包文件:      ${WORK_NAME}_result.tar.gz"
        echo ""
        echo -e "${GREEN}分析完成！结果已打包，可供下载。${NC}"
    else
        echo ""
        echo -e "${YELLOW}分析完成！但未生成打包文件。${NC}"
    fi
    echo "================================================"
}

# 脚本入口
main() {
    # 显示欢迎信息
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}       测序数据分析自动化pipeline v1.0${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    
    # 解析参数
    parse_arguments "$@"
    
    # 记录开始时间
    local start_time=$(date +%s)
    
    # 执行主流程
    main_pipeline
    
    # 计算运行时间
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    echo ""
    print_info "总运行时间: ${minutes}分${seconds}秒"
    
    # 停用conda环境
    if command -v conda &> /dev/null; then
        conda deactivate 2>/dev/null || true
    fi
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}用户中断，正在清理...${NC}"; exit 1' INT TERM

# 执行主函数
main "$@"
