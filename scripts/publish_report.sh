#!/bin/bash
# ============================================================
# 美股每日操盘报告 - 自动生成与发布脚本
# ============================================================
# 用法：
#   ./scripts/publish_report.sh pre    # 生成盘前策略报告
#   ./scripts/publish_report.sh post   # 生成盘后总结报告
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPORT_TYPE="${1:-pre}"

echo "=========================================="
echo "  美股每日操盘报告 - 自动生成与发布"
echo "  类型: $REPORT_TYPE"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 1. 生成报告
cd "$PROJECT_DIR"
echo ""
echo "[1/4] 正在生成报告..."
python3 scripts/generate_report.py --type "$REPORT_TYPE"

# 2. 获取 GitHub Token
echo ""
echo "[2/4] 正在配置 GitHub..."
source "$PROJECT_DIR/../.codebuddy/skills/github-connector/scripts/get_token.sh" github 2>/dev/null || \
source /root/.codebuddy/skills/github-connector/scripts/get_token.sh github

# 3. 配置远程仓库
echo ""
echo "[3/4] 正在提交到 GitHub..."
cd "$PROJECT_DIR"
git remote set-url origin "https://oauth2:${GITHUB_TOKEN}@github.com/tauwork/us-stock-310-agent.git" 2>/dev/null || true

# 4. 提交并推送
git add data/daily/ data/knowledge/
REPORT_DATE=$(date '+%Y%m%d')
if [ "$REPORT_TYPE" = "pre" ]; then
    COMMIT_MSG="📊 每日操盘报告: ${REPORT_DATE} 盘前策略"
else
    COMMIT_MSG="📋 每日操盘报告: ${REPORT_DATE} 盘后复盘"
fi

# 检查是否有变更
if git diff --cached --quiet; then
    echo "没有新的变更需要提交。"
else
    git -c user.name="Stock Advisor Bot" \
        -c user.email="stock-advisor@bot.local" \
        commit -m "$COMMIT_MSG"
    
    echo ""
    echo "[4/4] 正在推送到远程仓库..."
    git push origin main
fi

echo ""
echo "=========================================="
echo "  ✅ 报告生成与发布完成！"
echo "=========================================="
