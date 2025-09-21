#!/bin/bash

# Smart Git Commit Script
# 智能Git提交脚本 - 根据代码变更自动生成语义化commit message
# 使用方法: ./scripts/smart-commit.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 检查是否在Git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ 错误: 当前目录不是Git仓库${NC}"
    exit 1
fi

# 检查是否有变更
if git diff --cached --quiet && git diff --quiet; then
    echo -e "${YELLOW}⚠️  没有检测到代码变更${NC}"
    echo "请先使用 'git add' 添加要提交的文件"
    exit 0
fi

# 自动添加所有变更（可选，用户可以注释掉这行）
echo -e "${BLUE}📦 自动添加所有变更文件...${NC}"
git add .

# 获取变更统计
echo -e "${CYAN}🔍 分析代码变更...${NC}"

# 获取变更文件列表
changed_files=$(git diff --cached --name-only)
num_files=$(echo "$changed_files" | wc -l | tr -d ' ')

# 获取变更统计
stats=$(git diff --cached --numstat)
insertions=$(echo "$stats" | awk '{sum += $1} END {print sum+0}')
deletions=$(echo "$stats" | awk '{sum += $2} END {print sum+0}')

# 分析变更类型
function analyze_changes() {
    local changes=$(git diff --cached --name-status)
    local commit_type=""
    local scope=""
    local description=""
    local details=()
    
    # 统计不同类型的变更
    local added_files=0
    local modified_files=0
    local deleted_files=0
    local renamed_files=0
    
    if [[ -n "$changes" ]]; then
        added_files=$(echo "$changes" | grep -c "^A" 2>/dev/null | tr -d '\n' || echo "0")
        modified_files=$(echo "$changes" | grep -c "^M" 2>/dev/null | tr -d '\n' || echo "0")
        deleted_files=$(echo "$changes" | grep -c "^D" 2>/dev/null | tr -d '\n' || echo "0")
        renamed_files=$(echo "$changes" | grep -c "^R" 2>/dev/null | tr -d '\n' || echo "0")
        
        # 确保变量是数字
        added_files=${added_files:-0}
        modified_files=${modified_files:-0}
        deleted_files=${deleted_files:-0}
        renamed_files=${renamed_files:-0}
    fi
    
    # 分析文件类型和变更模式
    local has_new_features=false
    local has_bug_fixes=false
    local has_refactor=false
    local has_docs=false
    local has_tests=false
    local has_config=false
    local has_ui=false
    
    # 检查具体文件变更
    while IFS= read -r line; do
        local file=$(echo "$line" | awk '{print $2}')
        local status=$(echo "$line" | awk '{print $1}')
        
        # 根据文件名和路径判断变更类型
        case "$file" in
            *.md|*.txt|*.rst|docs/*|README*)
                has_docs=true
                ;;
            *test*|*spec*|*_test.go|*_spec.js)
                has_tests=true
                ;;
            *.json|*.yaml|*.yml|*.toml|*.ini|config/*|.env*)
                has_config=true
                ;;
            *.html|*.css|*.js|*.vue|*.jsx|*.tsx|templates/*|static/*|assets/*)
                has_ui=true
                ;;
        esac
        
        # 分析代码内容变更
        if [[ "$status" == "M" ]]; then
            local diff_content=$(git diff --cached "$file")
            
            # 检查是否包含新功能关键词
            if echo "$diff_content" | grep -qi "\(+.*func\|+.*function\|+.*def\|+.*class\|+.*interface\|+.*struct\)"; then
                has_new_features=true
            fi
            
            # 检查是否包含修复关键词
            if echo "$diff_content" | grep -qi "\(fix\|bug\|error\|issue\|patch\|correct\)"; then
                has_bug_fixes=true
            fi
            
            # 检查是否为重构
            if echo "$diff_content" | grep -qi "\(refactor\|rename\|reorganize\|restructure\|optimize\)"; then
                has_refactor=true
            fi
        fi
    done <<< "$changes"
    
    # 确定主要的commit类型
    if [[ "$added_files" -gt 0 ]] && [[ "$has_new_features" == true ]]; then
        commit_type="feat"
        description="add new functionality"
    elif [[ "$has_bug_fixes" == true ]]; then
        commit_type="fix"
        description="resolve issues and bugs"
    elif [[ "$has_refactor" == true ]]; then
        commit_type="refactor"
        description="improve code structure"
    elif [[ "$has_docs" == true ]] && [[ "$modified_files" -eq "$num_files" ]]; then
        commit_type="docs"
        description="update documentation"
    elif [[ "$has_tests" == true ]] && [[ "$modified_files" -eq "$num_files" ]]; then
        commit_type="test"
        description="update tests"
    elif [[ "$has_config" == true ]]; then
        commit_type="config"
        description="update configuration"
    elif [[ "$has_ui" == true ]]; then
        commit_type="ui"
        description="update user interface"
    elif [[ "$added_files" -gt 0 ]]; then
        commit_type="feat"
        description="add new files"
    elif [[ "$deleted_files" -gt 0 ]]; then
        commit_type="remove"
        description="remove files"
    elif [[ "$renamed_files" -gt 0 ]]; then
        commit_type="rename"
        description="rename files"
    else
        commit_type="update"
        description="update existing functionality"
    fi
    
    # 确定作用域
    local main_dirs=$(echo "$changed_files" | cut -d'/' -f1 | sort | uniq -c | sort -nr | head -1 | awk '{print $2}')
    if [[ -n "$main_dirs" ]] && [[ "$main_dirs" != "." ]]; then
        scope="$main_dirs"
    fi
    
    # 生成详细描述
    if [[ "$added_files" -gt 0 ]]; then
        details+=("add $added_files files")
    fi
    if [[ "$modified_files" -gt 0 ]]; then
        details+=("modify $modified_files files")
    fi
    if [[ "$deleted_files" -gt 0 ]]; then
        details+=("delete $deleted_files files")
    fi
    if [[ "$renamed_files" -gt 0 ]]; then
        details+=("rename $renamed_files files")
    fi
    
    # 构建commit message
    local commit_msg="$commit_type"
    if [[ -n "$scope" ]]; then
        commit_msg="$commit_msg($scope)"
    fi
    commit_msg="$commit_msg: $description"
    
    # 添加详细信息
    if [[ "${#details[@]}" -gt 0 ]]; then
        local detail_str=$(IFS=', '; echo "${details[*]}")
        commit_msg="$commit_msg\n\n- $detail_str"
        commit_msg="$commit_msg\n- +$insertions insertions, -$deletions deletions"
    fi
    
    echo "$commit_msg"
}

# 生成commit message
commit_message=$(analyze_changes)

# 显示变更摘要
echo -e "${GREEN}📊 变更摘要:${NC}"
echo -e "  📁 文件数量: ${YELLOW}$num_files${NC}"
echo -e "  ➕ 新增行数: ${GREEN}+$insertions${NC}"
echo -e "  ➖ 删除行数: ${RED}-$deletions${NC}"
echo ""

# 显示变更文件列表
echo -e "${BLUE}📝 变更文件:${NC}"
git diff --cached --name-status | while read -r status file; do
    if [[ -n "$status" ]] && [[ -n "$file" ]]; then
        status_icon=""
        case "$status" in
            "A") status_icon="${GREEN}➕${NC}" ;;
            "M") status_icon="${YELLOW}📝${NC}" ;;
            "D") status_icon="${RED}➖${NC}" ;;
            "R"*) status_icon="${PURPLE}🔄${NC}" ;;
            *) status_icon="${CYAN}❓${NC}" ;;
        esac
        echo -e "  $status_icon $file"
    fi
done
echo ""

# 显示生成的commit message
echo -e "${PURPLE}💬 生成的Commit Message:${NC}"
echo -e "${CYAN}┌─────────────────────────────────────────────────────────────┐${NC}"
echo -e "$commit_message" | while IFS= read -r line; do
    echo -e "${CYAN}│${NC} $line"
done
echo -e "${CYAN}└─────────────────────────────────────────────────────────────┘${NC}"
echo ""

# 直接提交，不询问用户确认
echo -e "${GREEN}✅ 正在提交...${NC}"
git commit -m "$(echo -e "$commit_message")"
echo -e "${GREEN}🎉 提交成功!${NC}"
echo -e "${BLUE}💡 提示: 使用 'git push' 推送到远程仓库${NC}"

# 显示当前Git状态
echo ""
echo -e "${CYAN}📋 当前Git状态:${NC}"
git status --short