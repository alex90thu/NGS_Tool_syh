#!/bin/bash

# 纳米抗体分析自动化pipeline
# 作者: 自动生成
# 描述: 自动化处理纳米抗体测序数据的分析流程

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
print_help() {
    echo -e "${BLUE}纳米抗体分析自动化pipeline${NC}"
    echo "用法: $0 -a 序列1路径 -b 序列2路径 -c 工作名称"
    echo ""
    echo "参数说明:"
    echo "  -a, --seq1       测序得到的序列1文件路径"
    echo "  -b, --seq2       测序得到的序列2文件路径"
    echo "  -c, --name       工作名称(用于输出文件命名)"
    echo "  -h, --help       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -a sample_R1.fastq.gz -b sample_R2.fastq.gz -c MyExperiment"
    echo ""
    echo "注意事项:"
    echo "  1. 确保已安装并配置好以下工具:"
    echo "     - gunzip"
    echo "     - flash"
    echo "     - seqkit"
    echo "     - python3"
    echo "  2. 脚本应在测序序列的文件夹下执行"
    echo "  3. 输出结果文件: C_result.csv"
}

# 错误处理函数
error_exit() {
    echo -e "${RED}错误: $1${NC}" >&2
    echo -e "${YELLOW}执行失败，清理临时文件...${NC}"
    
    # 清理可能的部分生成文件
    [ -f "${WORK_NAME}.extendedFrags.fastq" ] && rm -f "${WORK_NAME}.extendedFrags.fastq"
    [ -f "${WORK_NAME}.fa" ] && rm -f "${WORK_NAME}.fa"
    [ -f "${WORK_NAME}_trim.fa" ] && rm -f "${WORK_NAME}_trim.fa"
    
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
            -c|--name)
                WORK_NAME="$2"
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
    
    # 检查输入文件
    check_file "$SEQ1_PATH"
    check_file "$SEQ2_PATH"
}

# 主流程函数
main_pipeline() {
    print_info "开始纳米抗体分析流程"
    print_info "工作名称: $WORK_NAME"
    echo ""
    
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
    
    # 步骤1: FLASH拼接
    print_info "步骤1: 使用FLASH拼接序列"
    
    check_command "flash"
    print_info "执行: flash $SEQ1_FILE $SEQ2_FILE -o $WORK_NAME"
    flash "$SEQ1_FILE" "$SEQ2_FILE" -o "$WORK_NAME" -m 1 -M 100 || error_exit "FLASH拼接失败"
    
    if [ ! -f "${WORK_NAME}.extendedFrags.fastq" ]; then
        error_exit "FLASH输出文件未找到: ${WORK_NAME}.extendedFrags.fastq"
    fi
    print_success "FLASH拼接完成"
    echo ""
    
    # 步骤2: 转换fastq为fasta
    print_info "步骤2: 转换fastq为fasta格式"
    check_command "seqkit"
    print_info "执行: seqkit fq2fa ${WORK_NAME}.extendedFrags.fastq > ${WORK_NAME}.fa"
    seqkit fq2fa "${WORK_NAME}.extendedFrags.fastq" > "${WORK_NAME}.fa" || error_exit "seqkit转换失败"
    
    if [ ! -f "${WORK_NAME}.fa" ]; then
        error_exit "FASTA文件未生成: ${WORK_NAME}.fa"
    fi
    print_success "格式转换完成"
    echo ""
    
    # 步骤3: Trim序列
    print_info "步骤3: 使用指定标记trim序列"
    
    local TRIM_SCRIPT="/home/sunyuhong/software/NGS_Tool_syh/Nanobody/trim.py"
    if [ ! -f "$TRIM_SCRIPT" ]; then
        error_exit "未找到trim脚本: $TRIM_SCRIPT"
    fi
    
    print_info "执行: python $TRIM_SCRIPT --start_marker TGTACCTGCAGATGA --end_marker GTGACCGTGTCTTCT --min_length 100 --max_length 150 ${WORK_NAME}.fa ${WORK_NAME}_trim.fa"
    python "$TRIM_SCRIPT" --start_marker TGTACCTGCAGATGA --end_marker GTGACCGTGTCTTCT --min_length 100 --max_length 150 "${WORK_NAME}.fa" "${WORK_NAME}_trim.fa" || error_exit "trim序列失败"
    
    if [ ! -f "${WORK_NAME}_trim.fa" ]; then
        error_exit "trim后的文件未生成: ${WORK_NAME}_trim.fa"
    fi
    print_success "序列trim完成"
    echo ""
    
    # 步骤4: 解析序列并生成结果
    print_info "步骤4: 解析trim后的序列并生成结果表格"
    
    local PARSE_SCRIPT="/home/sunyuhong/software/NGS_Tool_syh/Nanobody/parse.py"
    if [ ! -f "$PARSE_SCRIPT" ]; then
        error_exit "未找到parse脚本: $PARSE_SCRIPT"
    fi
    
    print_info "执行: python $PARSE_SCRIPT ${WORK_NAME}_trim.fa ${WORK_NAME}_result.csv"
    python "$PARSE_SCRIPT" "${WORK_NAME}_trim.fa" "${WORK_NAME}_result.csv" || error_exit "解析序列失败"
    
    if [ ! -f "${WORK_NAME}_result.csv" ]; then
        error_exit "结果文件未生成: ${WORK_NAME}_result.csv"
    fi
    
    local result_size=$(du -h "${WORK_NAME}_result.csv" | cut -f1)
    print_success "结果分析完成: ${WORK_NAME}_result.csv (大小: $result_size)"
    echo ""
    
    # 清理临时文件
    print_info "清理临时文件"
    [ -f "${WORK_NAME}.notCombined_1.fastq" ] && rm -f "${WORK_NAME}.notCombined_1.fastq"
    [ -f "${WORK_NAME}.notCombined_2.fastq" ] && rm -f "${WORK_NAME}.notCombined_2.fastq"
    [ -f "${WORK_NAME}.hist" ] && rm -f "${WORK_NAME}.hist"
    [ -f "${WORK_NAME}.histogram" ] && rm -f "${WORK_NAME}.histogram"
    
    print_success "临时文件清理完成"
    echo ""
    
    # 步骤5: 生成摘要报告
    echo "[INFO] 步骤5: 生成分析摘要"
    echo "================================================"
    echo "            纳米抗体分析完成摘要"
    echo "================================================"
    echo "[INFO] 工作名称: $WORK_NAME"
    echo "[INFO] 分析时间: $(date)"
    echo ""
    echo "[INFO] 输入文件:"
    echo "  序列1: $SEQ1_PATH"
    echo "  序列2: $SEQ2_PATH"
    echo ""
    echo "[INFO] 输出文件:"
    echo "  FLASH输出: ${WORK_NAME}.extendedFrags.fastq"
    echo "  FASTA文件: ${WORK_NAME}.fa"
    echo "  Trim文件:  ${WORK_NAME}_trim.fa"
    echo "  结果文件:  ${WORK_NAME}_result.csv"
    echo ""
    echo "[SUCCESS] 分析完成！结果文件 ${WORK_NAME}_result.csv 已生成。"
    echo "================================================"
}

# 脚本入口
main() {
    # 显示欢迎信息
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}       纳米抗体分析自动化pipeline v1.0${NC}"
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
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}用户中断，正在清理...${NC}"; exit 1' INT TERM

# 执行主函数
main "$@"
