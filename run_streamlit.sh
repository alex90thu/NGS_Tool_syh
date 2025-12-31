#!/bin/bash

# Streamlit应用启动脚本

echo "🚀 NGS Tool Analyzer 启动脚本"
echo "================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到pip3，请先安装pip3"
    exit 1
fi

echo "📦 检查并安装依赖..."

# 检查并安装streamlit
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "正在安装 streamlit..."
    pip3 install streamlit>=1.28.0
fi

# 检查并安装pandas
if ! python3 -c "import pandas" 2>/dev/null; then
    echo "正在安装 pandas..."
    pip3 install pandas>=1.5.0
fi

# 检查脚本文件是否存在
if [ ! -f "app.py" ]; then
    echo "❌ 未找到app.py文件，请确保在正确的目录中运行脚本"
    exit 1
fi

echo ""
echo "✅ 依赖检查完成"
echo "🌐 启动NGS Tool Analyzer..."
echo "📱 应用将在浏览器中打开: http://localhost:8501"
echo "⏹️  按 Ctrl+C 停止应用"
echo ""

# 启动streamlit应用
streamlit run app.py --server.port=623 --server.address=0.0.0.0