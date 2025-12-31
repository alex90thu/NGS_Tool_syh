# WORF-Seq 路径修复验证

## 🔧 修复内容

### 问题
原始bash脚本在处理绝对路径时出现路径重复：
```
错误: /data/path/UDI002//data/path/UDI002_raw_1.fq.gz
```

### 解决方案
在bash脚本中添加了`FOLDER_BASENAME`变量：
```bash
# 设置文件夹基本名称
FOLDER_BASENAME=$(basename "$FOLDER_NAME")

# 使用基本名称构建文件路径
RAW_R1="${FOLDER_NAME}/${FOLDER_BASENAME}_raw_1.fq.gz"
```

## ✅ 修复的文件路径

### 输入文件（检查）
- R1: `${FOLDER_NAME}/${FOLDER_BASENAME}_raw_1.fq.gz`
- R2: `${FOLDER_NAME}/${FOLDER_BASENAME}_raw_2.fq.gz`

### 输出文件（生成）
- Clean R1: `${FOLDER_NAME}/${FOLDER_BASENAME}_clean_1.fq.gz`
- Clean R2: `${FOLDER_NAME}/${FOLDER_BASENAME}_clean_2.fq.gz`
- SAM: `${FOLDER_NAME}/${FOLDER_BASENAME}_aligned_minimap.sam`
- BAM: `${FOLDER_NAME}/${FOLDER_BASENAME}_aligned_minimap.sorted.bam`
- 日志: `${FOLDER_NAME}/${FOLDER_BASENAME}_worf_seq_pipeline.log`

## 🎯 示例验证

### 输入路径
```
FOLDER_NAME="/data/lulab_commonspace/sunyuhong/20251216_ShangHaiJiaoTongDaXue-yaozonglin-1_2/00.mergeRawFq/UDI002"
```

### 处理结果
```
FOLDER_BASENAME="UDI002"
RAW_R1="/data/lulab_commonspace/sunyuhong/20251216_ShangHaiJiaoTongDaXue-yaozonglin-1_2/00.mergeRawFq/UDI002/UDI002_raw_1.fq.gz"
```

### 网页端验证
app.py中的验证逻辑已经正确：
```python
raw_r1 = os.path.join(input_value, f"{os.path.basename(input_value)}_raw_1.fq.gz")
raw_r2 = os.path.join(input_value, f"{os.path.basename(input_value)}_raw_2.fq.gz")
```

## ✅ 修复验证

1. **Bash语法检查**: ✅ 通过
2. **路径构建逻辑**: ✅ 正确
3. **变量定义**: ✅ 完整
4. **网页验证**: ✅ 一致

## 🚀 现在可以使用

对于您的路径：
```
/data/lulab_commonspace/sunyuhong/20251216_ShangHaiJiaoTongDaXue-yaozonglin-1_2/00.mergeRawFq/UDI002
```

系统现在会正确查找：
```
/data/lulab_commonspace/sunyuhong/20251216_ShangHaiJiaoTongDaXue-yaozonglin-1_2/00.mergeRawFq/UDI002/UDI002_raw_1.fq.gz
/data/lulab_commonspace/sunyuhong/20251216_ShangHaiJiaoTongDaXue-yaozonglin-1_2/00.mergeRawFq/UDI002/UDI002_raw_2.fq.gz
```

---
*修复时间：2025年12月18日*