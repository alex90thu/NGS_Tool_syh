import streamlit as st
import subprocess
import os
import time
from datetime import datetime
import pandas as pd
import threading
import base64
from barcodes import BARCODES, get_barcode_sequence, generate_barcode_file, get_barcode_display_name
import json

# 设置页面配置
st.set_page_config(
    page_title="NGS Tool Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .project-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    .project-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #e1e5e9;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        cursor: pointer;
    }
    .project-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    .project-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .project-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .project-description {
        color: #7f8c8d;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .project-status {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    .status-available {
        background-color: #d4edda;
        color: #155724;
    }
    .status-coming-soon {
        background-color: #fff3cd;
        color: #856404;
    }
    .example-box {
        background: linear-gradient(135deg, #667eea05 0%, #764ba205 100%);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .example-title {
        font-weight: bold;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    .example-code {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 0.8rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        word-break: break-all;
    }
    .log-container {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #444;
        max-height: 500px;
        overflow-y: auto;
    }
    .log-text {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        line-height: 1.4;
        color: #f8f8f2;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .progress-container {
        background: linear-gradient(90deg, #667eea20 0%, #764ba220 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #667eea30;
    }
    .download-btn {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        color: white !important;
        text-decoration: none;
    }
    .file-missing {
        color: #dc3545;
        font-style: italic;
    }
        margin: 0.5rem 0;
    }
    .step-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 1rem 0;
        display: flex;
        align-items: center;
    }
    .step-number {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.5rem;
        font-size: 0.9rem;
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd, #ffeeba);
        border: 1px solid #ffeeba;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .file-check {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .file-exists {
        background-color: #d4edda;
        color: #155724;
    }
    .file-missing {
        background-color: #f8d7da;
        color: #721c24;
    }
    .log-container {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        max-height: 400px;
        overflow-y: auto;
    }
    .log-text {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        white-space: pre-wrap;
    }
    .download-btn {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .feedback-form {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 2rem;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .feedback-header {
        color: #495057;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .feedback-stats {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
        text-align: center;
    }
    .feedback-stat {
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 项目配置
PROJECTS = {
    "Egg_Indel": {
        "name": "🧬 Egg Indel Analysis",
        "description": "CRISPR基因编辑indel突变分析，自动处理双端测序数据并计算编辑效率",
        "status": "available",
        "script": "/home/sunyuhong/software/NGS_Tool_syh/Egg_Indel/script/egg_insel.bash",
        "example": {
            "seq1": "/data/sunyuhong/data/20250720_ShangHaiJiaoTongDaXue-sunyuhong-1_1/00.mergeRawFq/test/UDI001_raw_1.fq.gz",
            "seq2": "/data/sunyuhong/data/20250720_ShangHaiJiaoTongDaXue-sunyuhong-1_1/00.mergeRawFq/test/UDI001_raw_2.fq.gz", 
            "barcode": [1, 2, 3, 4, 5, 6],
            "name": "UDI001",
            "window": 15
        },
        "params": {
            "seq1": {"label": "📁 序列1文件路径 (R1)", "type": "file", "required": True},
            "seq2": {"label": "📁 序列2文件路径 (R2)", "type": "file", "required": True},
            "barcode": {"label": "🔢 选择 Barcode 序号", "type": "multiselect", "required": True, "options": list(BARCODES.keys())},
            "name": {"label": "📝 工作名称", "type": "text", "required": True},
            "window": {"label": "🔢 Indel窗口大小", "type": "number", "default": 15, "required": False}
        }
    },
    "Nanobody": {
        "name": "🔬 Nanobody Analysis",
        "description": "纳米抗体序列分析，包括序列拼接、trim和结果统计",
        "status": "available", 
        "script": "/home/sunyuhong/software/NGS_Tool_syh/Nanobody/nanobody.bash",
        "example": {
            "seq1": "/data/sunyuhong/data/20251214_ShangHaiJiaoTongDaXue-hanpeijin-1_1/00.mergeRawFq/NGS_TSLP1-HIGH/NGS_TSLP1-HIGH_raw_1.fq.gz",
            "seq2": "/data/sunyuhong/data/20251214_ShangHaiJiaoTongDaXue-hanpeijin-1_1/00.mergeRawFq/NGS_TSLP1-HIGH/NGS_TSLP1-HIGH_raw_2.fq.gz",
            "name": "test4"
        },
        "params": {
            "seq1": {"label": "📁 序列1文件路径 (R1)", "type": "file", "required": True},
            "seq2": {"label": "📁 序列2文件路径 (R2)", "type": "file", "required": True},
            "name": {"label": "📝 工作名称", "type": "text", "required": True}
        }
    },
    "WORF-Seq": {
        "name": "📊 WORF-Seq Analysis", 
        "description": "WORF序列高通量ORF筛选分析，包含质控、比对、可视化和全染色体背景分析",
        "status": "available",
        "script": "/home/sunyuhong/software/NGS_Tool_syh/WORF_Seq/worf_seq.bash",
        "example": {
            "folder_name": "/data/lulab_commonspace/sunyuhong/20251216_ShangHaiJiaoTongDaXue-yaozonglin-1_2/00.mergeRawFq/UDI002",
            "chromosome": "chr6",
            "center_position": 31236000,
            "step_size": 100000,
            "background_analysis": True
        },
        "params": {
            "folder_name": {"label": "📁 测序文件夹路径", "type": "text", "required": True, "help": "输入包含原始测序文件的文件夹绝对路径"},
            "chromosome": {"label": "🧬 目标染色体", "type": "select", "required": True, "options": ["chr1", "chr2", "chr3", "chr4", "chr5", "chr6", "chr7", "chr8", "chr9", "chr10", "chr11", "chr12", "chr13", "chr14", "chr15", "chr16", "chr17", "chr18", "chr19", "chr20", "chr21", "chr22", "chrX", "chrY", "chrM"]},
            "center_position": {"label": "📍 目标中心位置 (bp)", "type": "number", "required": True, "help": "基于参考基因组坐标的整数位置"},
            "step_size": {"label": "📏 全染色体绘图步长 (bp)", "type": "number", "default": 100000, "required": False, "help": "默认100000 bp"},
            "background_analysis": {"label": "🔬 全染色体背景分析", "type": "select", "required": False, "options": [True, False], "default": True, "help": "是否进行全染色体背景分析"}
        }
    }
}

def save_feedback(user_name, email, feedback_type, content):
    """保存用户反馈到文件"""
    try:
        feedback_file = "feedbacks.json"
        
        # 读取现有反馈
        feedbacks = []
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
            except:
                feedbacks = []
        
        # 添加新反馈
        new_feedback = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "user_name": user_name.strip() if user_name else "匿名用户",
            "email": email.strip() if email else "",
            "type": feedback_type,
            "content": content.strip(),
            "status": "new"
        }
        
        feedbacks.append(new_feedback)
        
        # 只保留最近50条反馈
        if len(feedbacks) > 50:
            feedbacks = feedbacks[-50:]
        
        # 保存到文件
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"保存反馈失败: {e}")
        return False

def display_recent_feedback():
    """显示最近的用户反馈"""
    feedback_file = "feedbacks.json"
    
    if not os.path.exists(feedback_file):
        st.info("📝 暂无用户留言，成为第一个留言的用户吧！")
        return
    
    try:
        with open(feedback_file, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
    except:
        st.error("❌ 无法读取反馈记录")
        return
    
    # 显示最近10条留言
    recent_feedbacks = feedbacks[-10:] if len(feedbacks) > 10 else feedbacks
    recent_feedbacks.reverse()  # 最新的在前
    
    if not recent_feedbacks:
        st.info("📝 暂无用户留言，成为第一个留言的用户吧！")
        return
    
    for i, feedback in enumerate(recent_feedbacks):
        # 留言卡片
        with st.expander(f"📝 {feedback['type']} - {feedback['timestamp']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**👤 用户：** {feedback['user_name']}")
                if feedback['email']:
                    st.markdown(f"**📧 联系：** {feedback['email']}")
                st.markdown(f"**📋 类型：** {feedback['type']}")
                st.markdown("---")
                st.markdown(feedback['content'])
            
            with col2:
                status_color = "🟢" if feedback['status'] == "resolved" else "🔵" if feedback['status'] == "reviewed" else "🆕"
                st.markdown(f"### {status_color}")
                st.markdown(f"**状态**\n{feedback['status']}")
        
        if i < len(recent_feedbacks) - 1:
            st.markdown("---")

def check_file_exists(file_path):
    """检查文件是否存在"""
    if not file_path:
        return False, "请输入文件路径"
    if os.path.exists(file_path):
        return True, "文件存在"
    else:
        return False, f"文件不存在: {file_path}"

def run_script(script_path, params):
    """运行pipeline脚本"""
    try:
        # 构建命令
        cmd = [script_path]
        
        if "Egg_Indel" in script_path:
            # 为 Egg Indel 传递选定的barcode序号（逗号分隔）
            barcode_nums = params["barcode"]
            
            # 将barcode序号转换为逗号分隔的字符串
            barcode_str = ','.join(str(b) for b in sorted(barcode_nums))
            
            cmd.extend([
                "-a", params["seq1"],
                "-b", params["seq2"], 
                "-c", barcode_str,  # 传递逗号分隔的barcode序号
                "-d", params["name"],
                "-w", str(params["window"])
            ])
        elif "Nanobody" in script_path:
            cmd.extend([
                "-a", params["seq1"],
                "-b", params["seq2"],
                "-c", params["name"]
            ])
        elif "worf_seq" in script_path:
            cmd.extend([
                "-f", params["folder_name"],
                "-c", params["chromosome"],
                "-p", str(params["center_position"]),
                "-s", str(params["step_size"]),
                "-b", str(params["background_analysis"])
            ])
        
        # 创建日志文件路径
        if "worf_seq" in script_path:
            # WORF-Seq项目使用folder_name作为工作目录
            work_dir = params.get("folder_name", "/tmp")
            folder_basename = os.path.basename(params.get('folder_name', 'worf_seq'))
            
            # 先尝试原始目录
            log_file = os.path.join(work_dir, f"{folder_basename}_worf_seq_pipeline.log")
            
            # 如果日志文件不存在，尝试查找临时目录
            if not os.path.exists(log_file):
                import glob
                # 查找临时目录中的日志文件
                temp_pattern = f"/tmp/worf_seq_{folder_basename}_*/{folder_basename}_worf_seq_pipeline.log"
                temp_logs = glob.glob(temp_pattern)
                if temp_logs:
                    log_file = temp_logs[0]
                    work_dir = os.path.dirname(log_file)
        else:
            # 其他项目使用第一个参数的目录
            work_dir = os.path.dirname(params[list(params.keys())[0]]) if params else "/tmp"
            log_file = os.path.join(work_dir, f"{params.get('name', 'pipeline')}_pipeline.log")
        
        # 运行脚本，同时输出到日志文件
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将stderr重定向到stdout
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 启动一个线程来实时读取输出并写入日志文件
        def write_output_to_log():
            with open(log_file, 'w') as log_f:
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        # 读取剩余输出
                        remaining = process.stdout.read()
                        if remaining:
                            log_f.write(remaining)
                        break
                    if line:
                        log_f.write(line)
                        log_f.flush()  # 立即写入文件
        
        import threading
        output_thread = threading.Thread(target=write_output_to_log)
        output_thread.daemon = True
        output_thread.start()
        
        return process, log_file
    except Exception as e:
        return None, str(e)

def create_barcode_grid(param_config, params, param_key, selected_project):
    """创建简洁的 barcode 序号选择器"""
    st.markdown(f"### {param_config['label']}")
    
    # 使用streamlit原生multiselect组件
    all_options = list(range(1, 97))  # 1-96
    
    # 初始化selected_barcodes，确保是正确的格式
    initial_value = params.get(param_key, [])
    if initial_value is None:
        initial_value = []
    
    # 如果从session state获取的值不是列表，则转换为空列表
    if not isinstance(initial_value, list):
        initial_value = []
    
    # 确保所有元素都是整数，支持字符串格式的barcode（如"#01"）
    selected_barcodes = []
    for item in initial_value:
        try:
            # 处理格式化字符串 "#01" -> 1 或直接整数 1
            if isinstance(item, str) and item.startswith('#'):
                barcode_int = int(item[1:])  # 去掉#前缀
            elif isinstance(item, str):
                barcode_int = int(item)  # 直接转换字符串数字
            else:
                barcode_int = int(item)  # 整数
            
            if 1 <= barcode_int <= 96:  # 确保在有效范围内
                selected_barcodes.append(barcode_int)
        except (ValueError, TypeError):
            continue
    
    # 自定义CSS样式
    st.markdown("""
    <style>
    div[data-testid="stMultiSelect"] > div > div {
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 15px;
    }
    div[data-testid="stMultiSelect"] > div > div > div {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
        gap: 8px;
        max-height: 300px;
        overflow-y: auto;
    }
    div[data-baseweb="true"] div[data-testid="stMultiSelect"] span {
        background: white;
        border: 2px solid #dee2e6;
        border-radius: 6px;
        padding: 8px 4px;
        margin: 2px;
        text-align: center;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    div[data-baseweb="true"] div[data-testid="stMultiSelect"] span:hover {
        border-color: #667eea;
        background: #f8f9ff;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.15);
    }
    div[data-baseweb="true"] div[data-testid="stMultiSelect"] span[data-selected="true"] {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 使用streamlit原生multiselect，自定义选项格式化
    formatted_options = [f"#{i:02d}" for i in all_options]
    
    # 映射关系：格式化字符串 -> 实际数字
    str_to_num = {f"#{i:02d}": i for i in all_options}
    num_to_str = {i: f"#{i:02d}" for i in all_options}
    
    # 转换已选择的数字为格式化字符串，确保类型正确
    default_selected = []
    if selected_barcodes:
        try:
            # 确保所有元素都是整数且在有效范围内
            valid_barcodes = []
            for i in selected_barcodes:
                try:
                    barcode_int = int(i)
                    if 1 <= barcode_int <= 96:  # 确保在有效范围内
                        valid_barcodes.append(barcode_int)
                except (ValueError, TypeError):
                    continue
            
            default_selected = [num_to_str[i] for i in valid_barcodes]
        except Exception:
            default_selected = []
    
    # 清理可能存在的无效session state数据
    widget_key = f"{selected_project}_{param_key}"
    if widget_key in st.session_state:
        current_value = st.session_state[widget_key]
        # 如果当前值不是有效的字符串列表，清除它
        if not isinstance(current_value, list) or not all(isinstance(x, str) for x in current_value):
            del st.session_state[widget_key]
    
    # 显示multiselect，确保default参数是有效的选项
    selected_str = st.multiselect(
        "选择序号（支持多选）",
        options=formatted_options,
        default=default_selected if default_selected else [],
        key=widget_key,
        help="选择1-96个barcode序号，支持多选"
    )
    
    # 转换回数字
    selected_barcodes = [str_to_num[s] for s in selected_str if s in str_to_num]
    
    # 更新参数
    params[param_key] = selected_barcodes
    
    # 简洁的选择提示
    if selected_barcodes:
        st.success(f"✅ 已选择 {len(selected_barcodes)} 个 Barcode")
    else:
        st.warning("⚠️ 请至少选择一个 Barcode")

def get_file_download_link(file_path, link_text):
    """生成文件下载链接"""
    try:
        with open(file_path, "rb") as f:
            contents = f.read()
        b64 = base64.b64encode(contents).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}" class="download-btn">{link_text}</a>'
        return href
    except Exception as e:
        return f'<span class="file-missing">无法读取文件: {str(e)}</span>'

def estimate_progress(log_content):
    """根据日志内容估算进度"""
    if not log_content:
        return 0.1
    
    # WORF-Seq pipeline 的步骤
    worf_steps = [
        "WORF-Seq Analysis Pipeline Started",
        "步骤1: 开始质控处理",
        "步骤2: 序列比对",
        "步骤3: SAM转BAM",
        "步骤4: 染色体比对图生成",
        "WORF-Seq Analysis Pipeline Completed Successfully"
    ]
    
    # Nanobody pipeline 的步骤
    nanobody_steps = [
        "开始纳米抗体分析流程",
        "步骤1: 使用FLASH拼接序列",
        "步骤2: 转换fastq为fasta格式", 
        "步骤3: 使用指定标记trim序列",
        "步骤4: 解析trim后的序列并生成结果表格",
        "分析完成"
    ]
    
    # 选择合适的步骤列表
    if "WORF-Seq Analysis Pipeline Started" in log_content:
        steps = worf_steps
    else:
        steps = nanobody_steps
    
    completed_steps = 0
    for step in steps:
        if step in log_content:
            completed_steps += 1
    
    return min(0.95, (completed_steps / len(steps)) * 0.9 + 0.05) / 100

def analyze_progress(log_content):
    """分析进度并返回详细信息"""
    if not log_content:
        return {"status": "未开始", "progress": 0, "current_step": "等待开始"}
    
    lines = log_content.split('\n')
    
    # 检查是否完成
    if "WORF-Seq Analysis Pipeline Completed Successfully" in log_content:
        return {"status": "已完成", "progress": 100, "current_step": "分析完成"}
    if "分析完成" in log_content or "nanobody分析完成摘要" in log_content:
        return {"status": "已完成", "progress": 100, "current_step": "分析完成"}
    
    # 检查当前步骤 - 支持多个项目的步骤
    current_step = "准备中"
    progress_value = 0
    
    # 首先检查是否是 WORF-Seq 项目
    if "WORF-Seq Analysis Pipeline Started" in log_content:
        # WORF-Seq 步骤
        if "步骤4: 染色体比对图生成" in log_content:
            current_step = "染色体比对图生成"
            progress_value = 85
        elif "步骤3: SAM转BAM" in log_content:
            current_step = "SAM转BAM处理"
            progress_value = 65
        elif "步骤2: 序列比对" in log_content:
            current_step = "序列比对中"
            progress_value = 45
        elif "步骤1: 开始质控处理" in log_content:
            current_step = "质控处理"
            progress_value = 25
        else:
            current_step = "开始分析"
            progress_value = 10
    # 检查是否是 Nanobody 项目
    elif "开始纳米抗体分析流程" in log_content:
        # Nanobody 步骤
        if "步骤4:" in log_content:
            current_step = "解析序列并生成结果"
            progress_value = 80
        elif "步骤3:" in log_content:
            current_step = "Trim序列处理"
            progress_value = 60
        elif "步骤2:" in log_content:
            current_step = "格式转换"
            progress_value = 40
        elif "步骤1:" in log_content:
            current_step = "FLASH拼接序列"
            progress_value = 20
        else:
            current_step = "开始分析"
            progress_value = 10
    # Egg Indel 步骤 - 增强版
    elif "Egg Indel Analysis Completed" in log_content:
        current_step = "分析完成"
        progress_value = 100
    elif "calculating indel efficiency" in log_content.lower():
        current_step = "计算编辑效率"
        progress_value = 90
    elif "aligning reads" in log_content.lower():
        current_step = "序列比对"
        progress_value = 75
    elif "Running egg_indel_analysis.py" in log_content:
        current_step = "Indel分析处理"
        progress_value = 60
    elif "processing barcode" in log_content.lower():
        current_step = "处理Barcode数据"
        progress_value = 45
    elif "splitting reads by barcode" in log_content.lower():
        current_step = "按Barcode分组"
        progress_value = 30
    elif "merging reads" in log_content.lower():
        current_step = "合并双端序列"
        progress_value = 15
    elif "Starting Egg Indel Analysis" in log_content:
        current_step = "开始分析"
        progress_value = 10
    
    # 检查是否有错误
    if "[ERROR]" in log_content or "错误:" in log_content or "ERROR" in log_content:
        current_step += " (检测到错误)"
    
    return {
        "status": "运行中" if progress_value < 100 else "已完成",
        "progress": progress_value,
        "current_step": current_step
    }

def get_current_step(log_content):
    """获取当前执行步骤的简短描述"""
    if not log_content:
        return "准备开始"
    
    if "步骤4:" in log_content and "解析" in log_content:
        return "🔍 解析序列"
    elif "步骤3:" in log_content and "trim" in log_content:
        return "✂️ Trim序列"
    elif "步骤2:" in log_content and "转换" in log_content:
        return "🔄 格式转换"
    elif "步骤1:" in log_content and "FLASH" in log_content:
        return "🔗 序列拼接"
    elif "开始纳米抗体分析流程" in log_content:
        return "🚀 开始分析"
    else:
        return "⏳ 准备中"

def display_results(project_name, params, work_dir):
    # 初始化变量，避免UnboundLocalError
    folder_name = work_dir
    folder_basename = os.path.basename(work_dir) if work_dir else "analysis"
    if project_name == "Nanobody" and params.get('name'):
        result_file = os.path.join(work_dir, f"{params['name']}_result.csv")
        
        st.markdown("## 📊 Nanobody 分析结果")
        st.markdown("---")
        
        if os.path.exists(result_file):
            try:
                df = pd.read_csv(result_file)
                
                # 显示文件状态
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📏 总行数", len(df))
                with col2:
                    st.metric("📋 总列数", len(df.columns))
                with col3:
                    file_size = os.path.getsize(result_file) / 1024
                    st.metric("💾 文件大小", f"{file_size:.1f} KB")
                with col4:
                    file_time = datetime.fromtimestamp(os.path.getmtime(result_file))
                    st.metric("🕐 修改时间", file_time.strftime('%m-%d %H:%M'))
                
                st.markdown("---")
                
                # 主要下载区域
                st.markdown("### 💾 结果文件下载")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Streamlit原生下载
                    try:
                        csv_content = df.to_csv(index=False)
                        st.download_button(
                            label="📥 下载完整CSV文件",
                            data=csv_content,
                            file_name=f"{params['name']}_result.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"生成下载失败: {e}")
                
                with col2:
                    # 备用下载方法
                    download_link = get_file_download_link(result_file, "📁 原始文件下载")
                    st.markdown(download_link, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # 数据预览控制
                st.markdown("### 📋 数据预览设置")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    preview_rows = st.slider(
                        "显示行数",
                        min_value=10,
                        max_value=min(1000, len(df)),
                        value=100,
                        key=f"preview_rows_{params['name']}"
                    )
                
                with col2:
                    show_all_columns = st.checkbox("显示所有列", value=True, key=f"show_all_cols_{params['name']}")
                    if not show_all_columns:
                        selected_columns = st.multiselect(
                            "选择显示的列",
                            options=df.columns.tolist(),
                            default=df.columns.tolist()[:5],
                            key=f"select_cols_{params['name']}"
                        )
                        df_display = df[selected_columns]
                    else:
                        df_display = df
                
                st.markdown("---")
                
                # 显示数据表格
                st.markdown(f"### 📊 数据预览 (前 {preview_rows} 行)")
                st.dataframe(
                    df_display.head(preview_rows),
                    use_container_width=True,
                    height=500
                )
                
                # 显示列详细信息
                with st.expander("📈 列详细信息"):
                    col_info = []
                    for col in df.columns:
                        dtype = str(df[col].dtype)
                        non_null = df[col].notna().sum()
                        null_count = df[col].isna().sum()
                        unique_count = df[col].nunique()
                        
                        col_info.append({
                            '列名': col,
                            '数据类型': dtype,
                            '非空值': non_null,
                            '空值': null_count,
                            '唯一值': unique_count
                        })
                    
                    col_info_df = pd.DataFrame(col_info)
                    st.dataframe(col_info_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ 读取CSV文件失败: {e}")
                st.markdown("### 📁 直接文件访问")
                st.info(f"文件路径: `{result_file}`")
                
                # 提供直接下载
                if os.path.exists(result_file):
                    download_link = get_file_download_link(result_file, f"📥 下载 {os.path.basename(result_file)}")
                    st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ 结果文件不存在: `{result_file}`")
            st.info("💡 请等待分析完成或检查工作目录是否正确")
    
    # 处理 Egg_Indel 项目的结果显示
    elif project_name == "Egg_Indel" and params.get('name'):
        # 添加CSV文件选择下载功能
        st.markdown("### 📥 CSV结果文件下载")
        
        # 定义结果文件夹路径
        result_dir = "/data/sunyuhong/data/20250720_ShangHaiJiaoTongDaXue-sunyuhong-1_1/00.mergeRawFq/UDI001/20250720_result"
        
        # 查找所有CSV文件
        csv_files = []
        if os.path.exists(result_dir):
            for file in os.listdir(result_dir):
                if file.endswith('.csv'):
                    csv_files.append(file)
        
        if csv_files:
            # 文件选择器
            st.markdown("#### 🔍 选择要下载的CSV文件")
            selected_csv = st.selectbox(
                "选择CSV文件:",
                csv_files,
                key="egg_indel_csv_selector"
            )
            
            if selected_csv:
                result_file = os.path.join(result_dir, selected_csv)
                
                if os.path.exists(result_file):
                    # 显示文件信息（简化版，不显示大小和时间）
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.info(f"📁 选中文件: `{selected_csv}`")
                    
                    with col2:
                        # 生成下载链接
                        download_link = get_file_download_link(result_file, "📥 下载选中文件")
                        st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ 文件不存在: `{result_file}`")
        else:
            st.warning("⚠️ 未找到任何CSV文件")
            st.info("💡 请检查结果文件夹路径是否正确，或等待文件生成")
        
        st.markdown("---")
        
        # 原有的分析结果显示（如果有的话）
        original_result_file = os.path.join(work_dir, f"{params['name']}_result.tar.gz")
        if os.path.exists(original_result_file):
            st.markdown("### 📦 分析结果")
            
            # 显示文件信息（简化版，不显示大小）
            st.info(f"📁 结果文件: {os.path.basename(original_result_file)}")
            
            # 下载按钮
            download_link = get_file_download_link(original_result_file, f"📥 下载 {os.path.basename(original_result_file)}")
            st.markdown(download_link, unsafe_allow_html=True)
            
            # 显示解压后的文件列表
            st.markdown("### 📋 包含文件")
            try:
                import tarfile
                with tarfile.open(original_result_file, 'r:gz') as tar:
                    file_list = tar.getnames()
                    for file in file_list:
                        st.write(f"- {file}")
            except Exception as e:
                st.warning(f"无法读取压缩包内容: {e}")
    
    # 处理 WORF-Seq 项目的结果显示
    elif project_name == "WORF-Seq" and params.get('folder_name'):
        folder_name = params['folder_name']
        folder_basename = os.path.basename(folder_name)
        chromosome = params.get('chromosome', 'chr6')
        center_position = params.get('center_position', 0)
        
        st.markdown("## 📊 WORF-Seq 分析结果")
        st.markdown("---")
        
        # 分析参数概览
        st.markdown("### 🔍 分析参数")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📁 文件夹", folder_basename)
        with col2:
            st.metric("🧬 染色体", chromosome)
        with col3:
            st.metric("📍 中心位置", f"{center_position:,}")
        with col4:
            step_size = params.get('step_size', 100000)
            st.metric("📏 步长", f"{step_size:,}")
        
        st.markdown("---")
        
        # 查找生成的图片文件
        st.markdown("### 📈 染色体比对图")
        
        # 调试信息：显示文件夹内容
        import glob
        if os.path.exists(folder_name):
            all_files = glob.glob(os.path.join(folder_name, "*"))
            png_files = glob.glob(os.path.join(folder_name, "*.png"))
            txt_files = glob.glob(os.path.join(folder_name, "*.txt"))
            
            with st.expander("🔍 调试信息 - 文件夹内容"):
                st.write(f"**文件夹路径:** `{folder_name}`")
                st.write(f"**所有文件数量:** {len(all_files)}")
                st.write(f"**PNG文件数量:** {len(png_files)}")
                st.write(f"**文本文件数量:** {len(txt_files)}")
                
                if png_files:
                    st.write("**PNG文件列表:**")
                    for png_file in png_files:
                        filename = os.path.basename(png_file)
                        filesize = os.path.getsize(png_file) / (1024 * 1024)  # MB
                        st.write(f"  - {filename} ({filesize:.2f} MB)")
                
                if txt_files:
                    st.write("**文本文件列表:**")
                    for txt_file in txt_files:
                        filename = os.path.basename(txt_file)
                        filesize = os.path.getsize(txt_file) / 1024  # KB
                        st.write(f"  - {filename} ({filesize:.2f} KB)")
        else:
            st.error(f"❌ 文件夹不存在: `{folder_name}`")
        
        # 可能的图片文件模式 (根据WGSmapping.py生成的实际文件名)
        image_patterns = [
            f"{folder_basename}_target_region_{chromosome}_{center_position}.png",
            f"{folder_basename}_target_region_{chromosome}_{center_position}.pdf",
            f"{folder_basename}_chromosome_{chromosome}_step{step_size}.png",
            f"{folder_basename}_chromosome_{chromosome}_step{step_size}.pdf"
        ]
        
        found_images = []
        
        # 先精确匹配
        for pattern in image_patterns:
            image_path = os.path.join(folder_name, pattern)
            if os.path.exists(image_path):
                found_images.append((image_path, pattern))
        
        # 如果没有找到，尝试模糊搜索
        if not found_images:
            import glob
            # 搜索目标区域图
            target_pattern = os.path.join(folder_name, f"*target_region_{chromosome}_{center_position}*.png")
            target_images = glob.glob(target_pattern)
            for img_path in target_images:
                filename = os.path.basename(img_path)
                found_images.append((img_path, filename))
            
            # 搜索全染色体图
            chrom_pattern = os.path.join(folder_name, f"*chromosome_{chromosome}_step{step_size}*.png")
            chrom_images = glob.glob(chrom_pattern)
            for img_path in chrom_images:
                filename = os.path.basename(img_path)
                found_images.append((img_path, filename))
            
            # 搜索所有PNG文件作为后备
            if not found_images:
                png_pattern = os.path.join(folder_name, "*.png")
                all_pngs = glob.glob(png_pattern)
                for img_path in all_pngs:
                    filename = os.path.basename(img_path)
                    found_images.append((img_path, filename))
        
        if found_images:
            # 显示找到的图片
            for image_path, filename in found_images:
                try:
                    st.markdown(f"#### 📊 {filename}")
                    
                    # 文件信息
                    file_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.info(f"📁 文件: {filename} ({file_size:.2f} MB)")
                    with col2:
                        # 下载按钮
                        download_link = get_file_download_link(image_path, f"📥 下载 {filename}")
                        st.markdown(download_link, unsafe_allow_html=True)
                    
                    # 显示图片
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        # 检查文件是否可读
                        if os.path.getsize(image_path) > 0:
                            try:
                                st.image(image_path, caption=f"{filename}", use_container_width=True)
                            except Exception as img_e:
                                st.error(f"❌ 图片加载失败: {img_e}")
                                st.code(f"文件路径: {image_path}")
                        else:
                            st.warning(f"⚠️ 图片文件为空: {filename}")
                    else:
                        st.warning(f"📄 {filename} (PDF格式，请下载后查看)")
                    
                    st.markdown("---")
                    
                except Exception as e:
                    st.error(f"❌ 无法显示图片 {filename}: {e}")
                    st.code(f"完整路径: {image_path}")
        else:
            st.warning("⚠️ 未找到染色体比对图")
            st.info("💡 请检查分析是否已完成，或查看日志文件获取更多信息")
        
        # 显示分析报告
        report_file = os.path.join(folder_name, f"{folder_basename}_worf_seq_summary.txt")
        if os.path.exists(report_file):
            st.markdown("### 📋 分析报告")
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                st.text_area("完整分析报告", value=report_content, height=200, disabled=True)
                
                # 下载报告
                download_link = get_file_download_link(report_file, f"📥 下载分析报告")
                st.markdown(download_link, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ 读取分析报告失败: {e}")
        
        # 显示BAM文件信息（如果存在）
        bam_file = os.path.join(folder_name, f"{folder_basename}_aligned_minimap.sorted.bam")
        if os.path.exists(bam_file):
            st.markdown("### 🧬 BAM文件信息")
            try:
                file_size = os.path.getsize(bam_file) / (1024 * 1024)  # MB
                index_file = f"{bam_file}.bai"
                index_exists = os.path.exists(index_file)
                index_size = os.path.getsize(index_file) / (1024 * 1024) if index_exists else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 BAM大小", f"{file_size:.2f} MB")
                with col2:
                    st.metric("📋 索引存在", "✅" if index_exists else "❌")
                with col3:
                    if index_exists:
                        st.metric("📁 索引大小", f"{index_size:.2f} MB")
                    else:
                        st.metric("📁 索引大小", "N/A")
                
                # 下载BAM文件
                download_link = get_file_download_link(bam_file, f"📥 下载 {os.path.basename(bam_file)}")
                st.markdown(download_link, unsafe_allow_html=True)
                
                if index_exists:
                    download_link = get_file_download_link(index_file, f"📥 下载 {os.path.basename(index_file)}")
                    st.markdown(download_link, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"❌ 读取BAM文件信息失败: {e}")
        
        # 显示所有生成的文件
        st.markdown("### 📁 所有生成文件")
        all_files = []
        if os.path.exists(folder_name):
            for file in os.listdir(folder_name):
                file_path = os.path.join(folder_name, file)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    all_files.append({
                        '文件名': file,
                        '大小 (MB)': f"{file_size:.2f}",
                        '修改时间': file_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        if all_files:
            df_files = pd.DataFrame(all_files)
            st.dataframe(df_files, use_container_width=True)
        else:
            st.info("未找到生成文件")

def display_log_files(work_dir, analysis_name):
    """显示和分析日志文件"""
    st.markdown("### 📜 日志文件管理")
    
    # 查找可能的日志文件
    log_files = []
    log_patterns = [
        f"{analysis_name}.log",
        f"{analysis_name}_pipeline.log", 
        f"{analysis_name}_analysis.log",
        "pipeline.log",
        "analysis.log",
        "egg_insel.log",
        "nanobody.log"
    ]
    
    # 查找匹配的日志文件
    for pattern in log_patterns:
        log_path = os.path.join(work_dir, pattern)
        if os.path.exists(log_path):
            log_files.append(log_path)
    
    # 查找所有.log文件
    for file in os.listdir(work_dir):
        if file.endswith('.log'):
            log_path = os.path.join(work_dir, file)
            if log_path not in log_files:
                log_files.append(log_path)
    
    if log_files:
        # 日志文件选择
        log_file = st.selectbox(
            "📁 选择日志文件:",
            options=log_files,
            format_func=lambda x: f"📄 {os.path.basename(x)} ({os.path.getsize(x)} 字节)",
            key="log_file_selector"
        )
        
        if log_file:
            # 文件基本信息
            col1, col2, col3 = st.columns(3)
            with col1:
                file_size = os.path.getsize(log_file) / 1024  # KB
                st.metric("📊 文件大小", f"{file_size:.1f} KB")
            with col2:
                file_stat = os.stat(log_file)
                modified_time = datetime.fromtimestamp(file_stat.st_mtime)
                st.metric("📅 修改时间", modified_time.strftime('%m-%d %H:%M'))
            with col3:
                st.metric("📁 路径", os.path.basename(log_file))
            
            st.markdown("---")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # 读取并显示日志内容
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    
                    lines = log_content.splitlines()
                    line_count = len(lines)
                    
                    st.markdown(f"#### 📝 日志内容 (共 {line_count} 行)")
                    
                    # 显示选项
                    col1, col2 = st.columns(2)
                    with col1:
                        show_all = st.checkbox("显示所有行", value=False, key="show_all_lines")
                    with col2:
                        if not show_all:
                            display_lines = st.slider("显示最后几行", 50, 1000, 500, key="display_lines")
                    
                    # 搜索功能
                    search_term = st.text_input("🔍 搜索日志内容", key="log_search")
                    
                    if search_term:
                        # 搜索高亮
                        st.markdown(f"🔍 搜索关键词: `{search_term}`")
                        highlighted_count = 0
                        for i, line in enumerate(lines, 1):
                            if search_term.lower() in line.lower():
                                highlighted_count += 1
                                if highlighted_count <= 50:  # 限制显示数量
                                    highlighted_line = line.replace(
                                        search_term, 
                                        f'<mark style="background-color: yellow; color: black; font-weight: bold;">{search_term}</mark>'
                                    )
                                    st.markdown(f"`{i:4d}`: {highlighted_line}", unsafe_allow_html=True)
                        
                        if highlighted_count > 50:
                            st.warning(f"找到 {highlighted_count} 个匹配项，仅显示前 50 个")
                        elif highlighted_count == 0:
                            st.warning("未找到匹配项")
                        else:
                            st.success(f"找到 {highlighted_count} 个匹配项")
                    else:
                        # 显示日志内容
                        if show_all:
                            display_content = lines
                        else:
                            display_content = lines[-display_lines:]
                        
                        st.markdown('<div class="log-container">', unsafe_allow_html=True)
                        for i, line in enumerate(display_content, len(lines) - len(display_content) + 1):
                            st.markdown(f'<div class="log-text">{i:5d}: {line}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        if not show_all and len(lines) > display_lines:
                            st.info(f"日志共 {len(lines)} 行，显示最后 {display_lines} 行")
                
                except UnicodeDecodeError:
                    st.error("❌ 无法读取日志文件（编码问题），尝试其他编码...")
                    try:
                        with open(log_file, 'r', encoding='gbk') as f:
                            log_content = f.read()
                        st.code(log_content, language='log', line_numbers=True)
                    except:
                        st.error("❌ 所有编码尝试失败")
                except Exception as e:
                    st.error(f"❌ 读取日志文件失败: {e}")
            
            with col2:
                st.markdown("#### 📁 文件信息")
                st.info(f"📁 日志位置: `{os.path.basename(log_file)}`")
                
                # 清理按钮
                st.markdown("---")
                if st.button("🗑️ 清理所有日志文件", key="clear_all_logs", help="删除此目录下所有.log文件"):
                    deleted_count = 0
                    for log in log_files:
                        try:
                            os.remove(log)
                            deleted_count += 1
                        except:
                            pass
                    if deleted_count > 0:
                        st.success(f"✅ 已删除 {deleted_count} 个日志文件")
                    else:
                        st.warning("⚠️ 没有文件被删除")
                    st.rerun()
    else:
        st.info("📂 未找到日志文件")
        st.markdown("""
        **提示:**
        - 执行Pipeline后会自动生成日志文件
        - 日志文件通常保存为: `{工作名称}_pipeline.log`
        - 检查工作目录中是否有 `.log` 文件
        """)

def main():
    # 标题
    st.markdown('<h1 class="main-header">🧬 NGS Tool Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 项目选择界面
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None
    
    if st.session_state.selected_project is None:
        st.markdown("## 🚀 选择分析项目")
        st.markdown("请选择您要使用的分析工具：")
        
        # 项目卡片网格 - 使用Streamlit原生组件
        projects_per_row = 2
        for i, (project_key, project_config) in enumerate(PROJECTS.items()):
            if i % projects_per_row == 0:
                cols = st.columns(projects_per_row)
            
            with cols[i % projects_per_row]:
                # 项目卡片样式
                status_class = "status-available" if project_config["status"] == "available" else "status-coming-soon"
                status_text = "✅ 可用" if project_config["status"] == "available" else "🚧 开发中"
                
                # 创建卡片容器
                with st.container():
                    st.markdown(f"""
                    <div class="project-card {'selected' if st.session_state.selected_project == project_key else ''}">
                        <div class="project-title">{project_config['name']}</div>
                        <div class="project-description">{project_config['description']}</div>
                        <div class="project-status {status_class}">{status_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 添加选择按钮
                    button_text = f"🚀 选择 {project_config['name']}" if project_config["status"] == "available" else f"🚧 {project_config['name']} (开发中)"
                    if st.button(
                        button_text,
                        key=f"select_{project_key}",
                        use_container_width=True,
                        disabled=project_config["status"] == "coming_soon",
                        type="primary" if project_config["status"] == "available" else "secondary"
                    ):
                        st.session_state.selected_project = project_key
                        if hasattr(st, 'experimental_rerun'):
                            st.experimental_rerun()
                        else:
                            st.rerun()
        
        # 留言板功能
        st.markdown("---")
        st.markdown("## 💬 意见建议箱")
        st.markdown("欢迎使用 NGS Tool Analyzer！如果您有任何意见、建议或遇到问题，请在这里留言，我们会持续改进工具。")
        
        # 留言表单
        with st.form("feedback_form"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                user_name = st.text_input("👤 您的称呼 (可选)", placeholder="例如：张博士、李同学等", key="user_name")
                user_email = st.text_input("📧 联系方式 (可选)", placeholder="邮箱或电话，方便我们回复您", key="user_email")
                
            with col2:
                feedback_type = st.selectbox(
                    "📋 留言类型",
                    options=["功能建议", "问题反馈", "使用体验", "其他意见", "技术咨询"],
                    key="feedback_type"
                )
            
            feedback_content = st.text_area(
                "💭 详细内容",
                placeholder="请详细描述您的意见或建议，我们会认真对待每一条反馈...",
                height=120,
                key="feedback_content",
                max_chars=1000
            )
            
            # 提交按钮
            submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 1])
            with submit_col2:
                submitted = st.form_submit_button("📤 提交留言", type="primary", use_container_width=True)
        
        # 处理留言提交
        if submitted:
            if feedback_content.strip():
                # 保存留言到文件
                save_feedback(user_name, user_email, feedback_type, feedback_content)
                st.success("✅ 感谢您的反馈！我们会认真考虑您的建议并尽快改进。")
                st.info("💡 如果您需要回复，请确保填写了联系方式。")
            else:
                st.warning("⚠️ 请填写留言内容后再提交")
        
        # 显示历史留言（只显示最近10条）
        st.markdown("### 📜 最近留言")
        display_recent_feedback()
        
        return
    
    # 项目详情界面
    selected_project = st.session_state.selected_project
    project_config = PROJECTS[selected_project]
    
    # 返回按钮
    if st.button("⬅️ 返回项目选择"):
        st.session_state.selected_project = None
        if hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
        else:
            st.rerun()
    
    st.markdown("---")
    
    # 项目标题和状态
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## {project_config['name']}")
        st.markdown(f"*{project_config['description']}*")
    with col2:
        if project_config["status"] == "coming_soon":
            st.markdown('<div class="project-status status-coming-soon" style="text-align: center; margin-top: 1rem;">🚧 开发中</div>', unsafe_allow_html=True)
    
    # 检查项目是否可用
    if project_config["status"] == "coming_soon":
        st.warning("该项目正在开发中，敬请期待！")
        return
    
    # 检查项目脚本是否存在
    if not project_config["script"] or not os.path.exists(project_config["script"]):
        st.error(f"⚠️ 项目脚本未找到: {project_config['script']}")
        return
    
    # 示例数据展示
    # 参数输入区域
    st.markdown("### 📋 参数设置")
    
    # 添加示例参数加载功能
    if project_config.get("example"):
        example_col1, example_col2, example_col3 = st.columns([1, 1, 2])
        
        with example_col1:
            if st.button("📋 使用示例参数", type="secondary", use_container_width=True):
                # 加载示例参数到session state
                for key, value in project_config["example"].items():
                    # 特殊处理barcode参数，确保转换为正确的格式
                    if key == "barcode" and isinstance(value, list):
                        # 对于Egg Indel Analysis，保持原始的整数列表格式
                        st.session_state[f"{selected_project}_{key}"] = value
                    else:
                        st.session_state[f"{selected_project}_{key}"] = value
                st.success("✅ 示例参数已加载")
                st.rerun()
        
        with example_col2:
            if st.button("🗑️ 清空参数", type="secondary", use_container_width=True):
                # 清空所有参数
                for key in project_config["params"].keys():
                    param_type = project_config["params"][key]["type"]
                    if param_type in ["text", "file"]:
                        st.session_state[f"{selected_project}_{key}"] = ""
                    elif param_type == "number":
                        st.session_state[f"{selected_project}_{key}"] = project_config["params"][key].get("default", 1)
                    elif param_type == "select":
                        st.session_state[f"{selected_project}_{key}"] = project_config["params"][key].get("default", project_config["params"][key]["options"][0])
                    elif param_type == "multiselect":
                        st.session_state[f"{selected_project}_{key}"] = []
                st.rerun()
        
        with example_col3:
            # 简洁显示示例参数信息
            st.info(f"💡 已配置示例参数，点击上方按钮即可加载")
    
    params = {}
    col1, col2 = st.columns(2)
    file_checks = {}
    
    for i, (param_key, param_config) in enumerate(project_config["params"].items()):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            # 获取用户输入值
            if param_config["type"] == "file":
                input_value = st.text_input(
                    param_config['label'],
                    value=st.session_state.get(f"{selected_project}_{param_key}", ""),
                    key=f"{selected_project}_{param_key}",
                    help="输入文件的完整路径"
                )
                params[param_key] = input_value
                
                # 实时检查文件是否存在
                if input_value:
                    exists, msg = check_file_exists(input_value)
                    if exists:
                        st.markdown(f'<span class="file-check file-exists">✅ {msg}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="file-check file-missing">❌ {msg}</span>', unsafe_allow_html=True)
                    file_checks[param_key] = (exists, msg)
                    
            elif param_config["type"] == "text":
                # 特殊处理 WORF-Seq 的 folder_name（文件夹路径）
                if selected_project == "WORF-Seq" and param_key == "folder_name":
                    input_value = st.text_input(
                        param_config['label'],
                        value=st.session_state.get(f"{selected_project}_{param_key}", ""),
                        key=f"{selected_project}_{param_key}",
                        help="输入包含原始测序文件的文件夹绝对路径"
                    )
                    params[param_key] = input_value
                    
                    # 添加快速检查选项
                    if input_value:
                        col_check1, col_check2, col_check3 = st.columns([2, 1, 1])
                        
                        with col_check2:
                            quick_check = st.button("⚡ 快速检查", key=f"quick_check_{selected_project}", help="只检查关键文件，速度更快")
                        with col_check3:
                            detailed_check = st.button("🔍 详细检查", key=f"detailed_check_{selected_project}", help="完整检查所有文件")
                        
                        # 执行检查
                        if quick_check or detailed_check:
                            check_key = f"folder_check_{input_value}"
                            with st.spinner("正在检查路径..."):
                                st.session_state[check_key] = {
                                    "checked": True,
                                    "exists": os.path.exists(input_value),
                                    "is_dir": False,
                                    "has_r1": False,
                                    "has_r2": False,
                                    "folder_files": [],
                                    "check_type": "quick" if quick_check else "detailed"
                                }
                                
                                if st.session_state[check_key]["exists"]:
                                    st.session_state[check_key]["is_dir"] = os.path.isdir(input_value)
                                    if st.session_state[check_key]["is_dir"]:
                                        # 检查预期的文件
                                        raw_r1 = os.path.join(input_value, f"{os.path.basename(input_value)}_raw_1.fq.gz")
                                        raw_r2 = os.path.join(input_value, f"{os.path.basename(input_value)}_raw_2.fq.gz")
                                        st.session_state[check_key]["has_r1"] = os.path.exists(raw_r1)
                                        st.session_state[check_key]["has_r2"] = os.path.exists(raw_r2)
                                        
                                        # 只有详细检查才列出文件内容
                                        if detailed_check:
                                            try:
                                                files = os.listdir(input_value)
                                                # 限制显示的文件数量，避免界面卡顿
                                                if len(files) > 20:
                                                    st.session_state[check_key]["folder_files"] = files[:20] + [f"... (还有{len(files)-20}个文件)"]
                                                else:
                                                    st.session_state[check_key]["folder_files"] = files
                                            except PermissionError:
                                                st.session_state[check_key]["folder_files"] = ["权限不足，无法读取"]
                                            except Exception as e:
                                                st.session_state[check_key]["folder_files"] = [f"读取失败: {str(e)}"]
                        
                        # 显示检查结果
                        check_key = f"folder_check_{input_value}"
                        if check_key in st.session_state and st.session_state[check_key]["checked"]:
                            check_result = st.session_state[check_key]
                            
                            if check_result["exists"]:
                                if check_result["is_dir"]:
                                    st.markdown(f'<span class="file-check file-exists">✅ 文件夹存在</span>', unsafe_allow_html=True)
                                    
                                    # 显示文件夹内容概览（仅在详细检查时显示）
                                    if check_result.get("check_type") == "detailed" and check_result["folder_files"]:
                                        with st.expander(f"📁 文件夹内容 ({len(check_result['folder_files'])} 个文件)", expanded=False):
                                            for file in sorted(check_result["folder_files"]):
                                                if file.startswith("..."):
                                                    st.info(f"📋 {file}")
                                                    continue
                                                    
                                                file_path = os.path.join(input_value, file)
                                                if os.path.isfile(file_path):
                                                    try:
                                                        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                                                        st.write(f"📄 {file} ({file_size:.1f} MB)")
                                                    except:
                                                        st.write(f"📄 {file}")
                                                else:
                                                    st.write(f"📁 {file}/")
                                    
                                    # 检查必需的测序文件
                                    expected_r1 = f"{os.path.basename(input_value)}_raw_1.fq.gz"
                                    expected_r2 = f"{os.path.basename(input_value)}_raw_2.fq.gz"
                                    
                                    st.markdown("**🧬 测序文件检查:**")
                                    if check_result["has_r1"]:
                                        st.markdown(f'<span class="file-check file-exists">✅ {expected_r1}</span>', unsafe_allow_html=True)
                                    else:
                                        st.markdown(f'<span class="file-check file-missing">❌ {expected_r1}</span>', unsafe_allow_html=True)
                                        
                                    if check_result["has_r2"]:
                                        st.markdown(f'<span class="file-check file-exists">✅ {expected_r2}</span>', unsafe_allow_html=True)
                                    else:
                                        st.markdown(f'<span class="file-check file-missing">❌ {expected_r2}</span>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<span class="file-check file-missing">❌ 路径存在但不是文件夹</span>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<span class="file-check file-missing">❌ 文件夹不存在</span>', unsafe_allow_html=True)
                                st.info("💡 请检查路径是否正确，或是否有访问权限")
                        
                        # 显示检查状态和提示
                        if check_key in st.session_state:
                            check_result = st.session_state[check_key]
                            check_type_desc = "快速检查" if check_result.get("check_type") == "quick" else "详细检查" if check_result.get("check_type") == "detailed" else ""
                            if check_type_desc:
                                st.success(f"✅ 已完成{check_type_desc}")
                        else:
                            st.info("🔍 输入完整路径后点击检查按钮验证")
                else:
                    params[param_key] = st.text_input(
                        param_config['label'],
                        value=st.session_state.get(f"{selected_project}_{param_key}", ""),
                        key=f"{selected_project}_{param_key}",
                        help="请输入相应的文本值"
                    )
                
            elif param_config["type"] == "number":
                default_value = st.session_state.get(f"{selected_project}_{param_key}", param_config.get("default", 1))
                params[param_key] = st.number_input(
                    param_config['label'],
                    value=default_value,
                    key=f"{selected_project}_{param_key}",
                    help=f"默认值: {param_config.get('default', 1)}"
                )
                
            elif param_config["type"] == "select":
                default_index = 0
                default_value = st.session_state.get(f"{selected_project}_{param_key}")
                if default_value and default_value in param_config["options"]:
                    default_index = param_config["options"].index(default_value)
                
                params[param_key] = st.selectbox(
                    param_config['label'],
                    options=param_config["options"],
                    index=default_index,
                    key=f"{selected_project}_{param_key}"
                )
                
            elif param_config["type"] == "multiselect":
                # 特殊处理 barcode 多选
                if param_key == "barcode":
                    create_barcode_grid(param_config, params, param_key, selected_project)
                else:
                    default_value = st.session_state.get(f"{selected_project}_{param_key}", [])
                    params[param_key] = st.multiselect(
                        param_config['label'],
                        options=param_config["options"],
                        default=default_value,
                        key=f"{selected_project}_{param_key}"
                    )
    
    st.markdown("---")
    
    # 执行按钮和输出区域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button(f"🚀 执行分析", type="primary", use_container_width=True):
            # 验证参数
            missing_required = []
            for param_key, param_config in project_config["params"].items():
                if param_config.get("required", False) and not params.get(param_key):
                    missing_required.append(param_config['label'])
            
            if missing_required:
                st.error(f"❌ 请填写必需参数: {', '.join(missing_required)}")
                return
            
            # 验证文件存在性
            missing_files = []
            for param_key, param_config in project_config["params"].items():
                if param_config["type"] == "file" and params.get(param_key):
                    exists, _ = check_file_exists(params[param_key])
                    if not exists:
                        missing_files.append(param_config['label'])
            
            # 特殊验证 WORF-Seq 的 folder_name 参数
            if selected_project == "WORF-Seq" and params.get("folder_name"):
                folder_path = params["folder_name"]
                check_key = f"folder_check_{folder_path}"
                
                if check_key in st.session_state and st.session_state[check_key].get("checked"):
                    check_result = st.session_state[check_key]
                    if not check_result.get("exists"):
                        missing_files.append(f"文件夹不存在: {folder_path}")
                    elif not check_result.get("is_dir"):
                        missing_files.append(f"路径不是文件夹: {folder_path}")
                    elif not (check_result.get("has_r1") and check_result.get("has_r2")):
                        expected_r1 = f"{os.path.basename(folder_path)}_raw_1.fq.gz"
                        expected_r2 = f"{os.path.basename(folder_path)}_raw_2.fq.gz"
                        missing_files.append(f"缺少必需文件: {expected_r1} 或 {expected_r2}")
                else:
                    # 如果没有检查过，提示用户先检查
                    st.warning("⚠️ 请先点击「快速检查」或「详细检查」按钮验证文件夹路径")
                    return
            
            # 特殊验证 Egg Indel 的 barcode 参数
            if selected_project == "Egg_Indel" and params.get("barcode"):
                selected_barcodes = params["barcode"]
                invalid_barcodes = [b for b in selected_barcodes if b not in BARCODES]
                
                if invalid_barcodes:
                    missing_files.append(f"无效的 barcode 序号: {', '.join(map(str, invalid_barcodes))}")
                elif selected_barcodes:
                    st.success(f"✅ 已选择 {len(selected_barcodes)} 个 barcode")
                    # 显示前几个选中的 barcode
                    display_count = min(5, len(selected_barcodes))
                    examples = [f"{b:02d}:{BARCODES[b]}" for b in sorted(selected_barcodes)[:display_count]]
                    st.info(f"🔬 示例: {', '.join(examples)}{'...' if len(selected_barcodes) > display_count else ''}")
                else:
                    st.warning("⚠️ 尚未选择任何 barcode")
            
            if missing_files:
                st.error(f"❌ 以下文件不存在: {', '.join(missing_files)}")
                return
            
            # 显示开始信息
            st.session_state.running = True
            st.session_state.start_time = datetime.now()
            st.session_state.process = None
            st.session_state.output = []
            st.session_state.error = ""
            # 设置工作目录，针对不同项目使用不同逻辑
            if selected_project == "WORF-Seq":
                st.session_state.work_dir = params.get("folder_name", "/tmp")  # WORF-Seq使用folder_name作为工作目录
            else:
                # 其他项目使用第一个文件所在目录，确保有有效的文件路径
                first_param_key = list(project_config["params"].keys())[0]
                if params.get(first_param_key):
                    st.session_state.work_dir = os.path.dirname(params[first_param_key])
                else:
                    st.session_state.work_dir = "/tmp"
            
            # 启动脚本
            result = run_script(project_config["script"], params)
            if isinstance(result, tuple) and len(result) == 2 and result[0] is None:
                st.session_state.error = result[1]
                st.session_state.running = False
            else:
                st.session_state.process = result[0]
                st.session_state.log_file = result[1]
                
                # 为Egg Indel设置30秒后下载功能
                if selected_project == "Egg_Indel":
                    st.session_state['download_start_time'] = datetime.now()
                    st.session_state['egg_indel_result_file'] = "/data/sunyuhong/data/20250720_ShangHaiJiaoTongDaXue-sunyuhong-1_1/00.mergeRawFq/UDI001/20250720_result/sample_summary.csv"
            st.rerun()
    
    with col2:
        if st.session_state.get('running', False):
            if st.button("⏹️ 停止执行", use_container_width=True):
                if st.session_state.get('process'):
                    st.session_state.process.terminate()
                st.session_state.running = False
                st.session_state.output.append("\n⏹️ 用户停止执行")
                if hasattr(st, 'experimental_rerun'):
                    st.experimental_rerun()
                else:
                    st.rerun()
    
    # 输出区域
    if st.session_state.get('running', False) or st.session_state.get('output') or st.session_state.get('log_file'):
        st.markdown("### 📊 执行日志")
        
        # 进度信息
        if st.session_state.get('running', False):
            elapsed = datetime.now() - st.session_state.get('start_time', datetime.now())
            st.info(f"⏱️ 运行时间: {elapsed}")
            
            # 添加Egg Indel特定的状态信息
            if selected_project == "Egg_Indel":
                st.info("🔬 Egg Indel CRISPR编辑效率分析进行中...")
                
                # 检查是否已经过了30秒，显示下载选项
                if st.session_state.get('download_start_time'):
                    current_time = datetime.now()
                    time_diff = (current_time - st.session_state['download_start_time']).total_seconds()
                    
                    if time_diff >= 30:
                        st.markdown("### 📥 结果下载")
                        st.info("✅ 分析已开始超过30秒，可以下载结果文件")
                        
                        result_file = st.session_state.get('egg_indel_result_file', "/data/sunyuhong/data/20250720_ShangHaiJiaoTongDaXue-sunyuhong-1_1/00.mergeRawFq/UDI001/20250720_result/sample_summary.csv")
                        
                        if os.path.exists(result_file):
                            # 显示文件信息
                            file_size = os.path.getsize(result_file) / (1024 * 1024)  # MB
                            file_time = datetime.fromtimestamp(os.path.getmtime(result_file))
                            
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.info(f"📁 结果文件: `{os.path.basename(result_file)}`")
                                st.write(f"📏 文件大小: {file_size:.2f} MB")
                                st.write(f"🕐 修改时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            with col2:
                                # 生成下载链接
                                download_link = get_file_download_link(result_file, "📥 下载结果文件")
                                st.markdown(download_link, unsafe_allow_html=True)
                        else:
                            st.warning(f"⚠️ 结果文件不存在: `{result_file}`")
                            st.info("💡 请检查文件路径是否正确，或等待文件生成")
                    else:
                        remaining_time = 30 - time_diff
                        st.info(f"⏳ 分析开始后 {int(remaining_time)} 秒可下载结果文件")
        
        # 读取日志文件内容
        log_content = ""
        if st.session_state.get('log_file') and os.path.exists(st.session_state.get('log_file')):
            try:
                with open(st.session_state.get('log_file'), 'r', encoding='utf-8') as f:
                    log_content = f.read()
            except Exception as e:
                st.warning(f"无法读取日志文件: {e}")
        
        # 读取进程输出（如果仍在运行）
        if st.session_state.get('process'):
            process = st.session_state.process
            
            # 检查进程状态
            try:
                returncode = process.poll()
                if returncode is None:  # 进程仍在运行
                    # 显示进度条和实时状态
                    progress_info = analyze_progress(log_content)
                    
                    # 为Egg Indel添加特定状态信息
                    if selected_project == "Egg_Indel":
                        status_text = f"🔬 Egg Indel Analysis - {progress_info['current_step']} ({progress_info['progress']}%)"
                    else:
                        status_text = f"{progress_info['current_step']} ({progress_info['progress']}%)"
                    
                    st.progress(progress_info['progress'] / 100, text=status_text)
                    
                    # 实时显示最近几行日志
                    if log_content:
                        lines = log_content.strip().split('\n')
                        recent_lines = lines[-10:]  # 显示最后10行
                        st.markdown("### 📋 实时日志输出")
                        st.code("\n".join(recent_lines), language="bash")
                        st.caption(f"🔄 实时更新 (最后{len(recent_lines)}行)")
                    else:
                        st.info("⏳ 等待日志输出...")
                    
                    # 添加自动刷新功能
                    st.markdown("---")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("🔄 手动刷新日志", key="refresh_logs"):
                            st.rerun()
                    with col2:
                        st.info("💡 日志将自动更新，点击按钮可手动刷新")
                    
                    # 设置自动刷新（每5秒）
                    st.markdown("""
                    <script>
                    setTimeout(function() {
                        window.location.reload();
                    }, 5000);
                    </script>
                    """, unsafe_allow_html=True)
                    
                else:  # 进程结束
                    # 清除进度并显示完成状态
                    if returncode == 0:
                        st.success("✅ 执行完成！")
                        
                        # 为Egg Indel添加完成信息和下载选项
                        if selected_project == "Egg_Indel":
                            st.info("🎉 Egg Indel CRISPR编辑效率分析已完成！")
                            
                            # 检查是否已设置下载状态
                            if not st.session_state.get('download_ready', False):
                                st.session_state['download_ready_time'] = datetime.now()
                                st.session_state['download_ready'] = True
                            
                            # 设置结果文件路径
                            st.session_state['egg_indel_result_file'] = "/data/sunyuhong/data/20250720_ShangHaiJiaoTongDaXue-sunyuhong-1_1/00.mergeRawFq/UDI001/20250720_result/sample_summary.csv"
                    else:
                        st.error(f"❌ 执行失败，返回码: {returncode}")
                    
                    # 读取剩余的错误输出（stderr已被重定向到stdout，所以这里为None）
                    try:
                        if process.stderr:
                            error_output = process.stderr.read()
                            if error_output:
                                st.session_state.error = error_output
                    except AttributeError:
                        # process.stderr 为 None，这是正常的（因为重定向了stderr）
                        pass
                    
                    st.session_state.running = False
                    
                    # 重新读取完整的日志文件
                    if st.session_state.get('log_file') and os.path.exists(st.session_state.get('log_file')):
                        try:
                            with open(st.session_state.get('log_file'), 'r', encoding='utf-8') as f:
                                log_content = f.read()
                        except:
                            pass
                            
            except Exception as e:
                st.error(f"❌ 检查进程状态时出错: {e}")
                st.session_state.running = False
        
        # 显示日志内容
        if log_content:
            st.markdown("### 📜 实时日志输出")
            
            # 创建两列布局：日志显示 + 进度信息
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # 日志显示选项
                show_all_logs = st.checkbox("显示完整日志", value=True, key="show_all_logs")
                
                if show_all_logs:
                    # 显示所有日志，使用代码块格式
                    st.code(log_content, language='bash', line_numbers=False)
                else:
                    # 只显示最后N行
                    tail_lines = st.slider("显示最后几行", 100, 2000, 500, key="tail_lines")
                    lines = log_content.split('\n')
                    recent_lines = lines[-tail_lines:] if len(lines) > tail_lines else lines
                    st.code('\n'.join(recent_lines), language='bash', line_numbers=True)
            
            with col2:
                # 进度分析
                progress_info = analyze_progress(log_content)
                
                # 显示状态（简洁显示）
                status_color = "🟢" if progress_info['status'] == "已完成" else "🟡" if progress_info['status'] == "运行中" else "🔴"
                st.metric(f"{status_color} {progress_info['status']}", f"{progress_info['progress']}%")
                
                # 操作按钮
                if st.button("🔄 刷新状态", key="refresh_status", use_container_width=True):
                    if hasattr(st, 'experimental_rerun'):
                        st.experimental_rerun()
                    else:
                        st.rerun()
        
        # 如果有session state的output，也显示（兼容性）
        elif st.session_state.get('output'):
            st.markdown("### 📜 实时日志输出")
            
            # 显示选项
            col1, col2, col3 = st.columns([2, 1, 1])
            
            st.info(f"📝 当前输出行数: {len(st.session_state.output)}")
            
            # 显示日志内容
            output_text = '\n'.join(st.session_state.output)
            st.code(output_text, language='bash', line_numbers=False)
        
        # 显示错误信息
        if st.session_state.get('error'):
            st.error(f"❌ 错误信息:\n{st.session_state.error}")
        
        # 显示错误
        if st.session_state.get('error'):
            st.error(f"❌ 错误信息:\n{st.session_state.error}")
        
        # 如果执行完成，显示结果
        if not st.session_state.get('running', False):
            if not st.session_state.get('error'):
                st.success("✅ 执行完成！")
                
                # 保存日志到文件（如果还没有保存的话）
                if not st.session_state.get('log_file') and st.session_state.get('output') and params.get('name'):
                    work_dir = st.session_state.get('work_dir', '.')
                    log_file = os.path.join(work_dir, f"{params['name']}_pipeline.log")
                    try:
                        with open(log_file, 'w', encoding='utf-8') as f:
                            f.write(f"NGS Tool Analyzer Pipeline Log\n")
                            f.write(f"项目: {selected_project}\n")
                            f.write(f"工作名称: {params.get('name', 'unknown')}\n")
                            f.write(f"开始时间: {st.session_state.get('start_time', datetime.now())}\n")
                            f.write(f"结束时间: {datetime.now()}\n")
                            f.write("=" * 50 + "\n\n")
                            f.write("\n".join(st.session_state.output))
                        st.session_state.log_file = log_file
                        st.info(f"📝 日志已保存到: {os.path.basename(log_file)}")
                    except Exception as e:
                        st.warning(f"保存日志文件失败: {e}")
                
                # 显示日志文件信息
                if st.session_state.get('log_file') and os.path.exists(st.session_state.get('log_file')):
                    st.markdown("### 📁 日志文件信息")
                    st.info(f"📁 日志位置: `{st.session_state.get('log_file')}`")
                
                # 显示结果文件
                work_dir = st.session_state.get('work_dir', '.')
                display_results(selected_project, params, work_dir)
        
        # 无论是否在运行，都检查并显示结果文件
        elif st.session_state.get('log_file') and params.get('name'):
            # 如果有日志文件，可能已经完成了执行
            work_dir = st.session_state.get('work_dir', '.')
            result_file = os.path.join(work_dir, f"{params['name']}_result.csv")
            
            # 如果结果文件存在，直接显示
            if os.path.exists(result_file):
                st.markdown("---")
                st.markdown("### 📊 分析结果")
                st.info("💡 检测到结果文件，直接显示分析结果")
                display_results(selected_project, params, work_dir)
            else:
                # 提供手动检查结果的按钮
                st.markdown("---")
                st.markdown("### 🔍 检查分析结果")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.info("📋 执行可能已完成，点击按钮检查结果文件")
                with col2:
                    if st.button("🔄 检查结果", key="check_results"):
                        if os.path.exists(result_file):
                            st.success("✅ 发现结果文件！")
                            display_results(selected_project, params, work_dir)
                            if hasattr(st, 'experimental_rerun'):
                                st.experimental_rerun()
                            else:
                                st.rerun()
                        else:
                            st.warning("⚠️ 结果文件尚未生成，请稍后重试")
    
    # 添加一个独立的结果检查区域（总是在页面底部显示）
    if params and params.get('name'):
        work_dir = st.session_state.get('work_dir', os.path.dirname(params.get('seq1', '.')))
        result_file = os.path.join(work_dir, f"{params['name']}_result.csv")
        
        # 添加调试信息
        with st.expander("🔍 调试信息", expanded=False):
            st.write(f"**工作目录**: `{work_dir}`")
            st.write(f"**结果文件路径**: `{result_file}`")
            st.write(f"**文件是否存在**: `{os.path.exists(result_file)}`")
            
            # 列出工作目录中的文件
            if os.path.exists(work_dir):
                files = os.listdir(work_dir)
                result_files = [f for f in files if 'result' in f and f.endswith('.csv')]
                st.write(f"**目录中的文件数**: {len(files)}")
                st.write(f"**CSV结果文件**: {result_files}")
                
                if files:
                    st.write("**所有文件列表**:")
                    for file in sorted(files):
                        file_path = os.path.join(work_dir, file)
                        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                        st.write(f"  - `{file}` ({file_size} bytes)")
        
        # 如果结果文件存在，总是显示一个结果检查卡片
        if os.path.exists(result_file):
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success("🎉 分析完成！结果文件已生成")
                st.info(f"📁 结果文件位置: `{result_file}`")
                
                # 显示文件信息
                try:
                    file_size = os.path.getsize(result_file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(result_file))
                    st.write(f"📏 文件大小: {file_size} bytes")
                    st.write(f"🕐 修改时间: {file_time}")
                except:
                    pass
                    
            with col2:
                if st.button("📊 查看结果", key="view_results_final", use_container_width=True):
                    display_results(selected_project, params, work_dir)
                    if hasattr(st, 'experimental_rerun'):
                        st.experimental_rerun()
                    else:
                        st.rerun()
        else:
            # 如果文件不存在，提供搜索功能
            st.markdown("---")
            st.markdown("### 🔍 查找结果文件")
            
            if os.path.exists(work_dir):
                csv_files = [f for f in os.listdir(work_dir) if f.endswith('.csv')]
                if csv_files:
                    st.info(f"发现 {len(csv_files)} 个CSV文件，请选择查看:")
                    selected_file = st.selectbox(
                        "选择CSV文件:",
                        options=csv_files,
                        key="select_csv_file"
                    )
                    
                    if selected_file:
                        file_path = os.path.join(work_dir, selected_file)
                        st.info(f"📁 选择的文件: `{file_path}`")
                        
                        if st.button("📊 查看选中的文件", key="view_selected_file"):
                            # 临时修改参数来显示选中的文件
                            temp_params = params.copy()
                            temp_params['name'] = selected_file.replace('_result.csv', '').replace('.csv', '')
                            display_results(selected_project, temp_params, work_dir)
                            if hasattr(st, 'experimental_rerun'):
                                st.experimental_rerun()
                            else:
                                st.rerun()
                else:
                    st.warning("⚠️ 工作目录中没有找到CSV文件")
            else:
                st.error("❌ 工作目录不存在")

    # 为Egg_indel分析添加始终显示的下载功能
    if selected_project == "Egg_Indel" and params and params.get('name'):
        st.markdown("---")
        st.markdown("### 📥 CSV结果文件下载")
        
        # 定义结果文件夹路径
        result_dir = "/data/sunyuhong/data/20250720_ShangHaiJiaoTongDaXue-sunyuhong-1_1/00.mergeRawFq/UDI001/20250720_result"
        
        # 查找所有CSV文件
        csv_files = []
        if os.path.exists(result_dir):
            for file in os.listdir(result_dir):
                if file.endswith('.csv'):
                    csv_files.append(file)
        
        if csv_files:
            # 文件选择器
            st.markdown("#### 🔍 选择要下载的CSV文件")
            selected_csv = st.selectbox(
                "选择CSV文件:",
                csv_files,
                key="egg_indel_csv_download_selector"
            )
            
            if selected_csv:
                result_file = os.path.join(result_dir, selected_csv)
                
                if os.path.exists(result_file):
                    # 显示文件信息（简化版，不显示大小和时间）
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.info(f"📁 选中文件: `{selected_csv}`")
                    
                    with col2:
                        # 生成下载链接
                        download_link = get_file_download_link(result_file, "📥 下载选中文件")
                        st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ 文件不存在: `{result_file}`")
        else:
            st.warning("⚠️ 未找到任何CSV文件")
            st.info("💡 请检查结果文件夹路径是否正确，或等待文件生成")

if __name__ == "__main__":
    # 初始化session state
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'output' not in st.session_state:
        st.session_state.output = []
    if 'error' not in st.session_state:
        st.session_state.error = ""
    
    main()