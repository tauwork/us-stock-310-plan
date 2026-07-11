#!/bin/bash
# ============================================================
# KOL数据抓取与报告发布脚本
# ============================================================
# 用法：
#   ./scripts/publish_kol_report.sh
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  美股KOL数据抓取与分析报告"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 1. 生成 KOL 分析报告
echo ""
echo "[1/3] 正在生成 KOL 聚合分析报告..."
cd "$PROJECT_DIR"
python3 scripts/generate_kol_report.py

# 2. 配置 Git 推送
echo ""
echo "[2/3] 正在配置 GitHub 推送..."

# 优先使用环境变量
if [ -n "$GITHUB_PAT" ]; then
    GIT_TOKEN="$GITHUB_PAT"
elif [ -f /root/.codebuddy/skills/github-connector/scripts/get_token.sh ]; then
    source /root/.codebuddy/skills/github-connector/scripts/get_token.sh github 2>/dev/null || true
    GIT_TOKEN="${GITHUB_TOKEN}"
fi

if [ -z "$GIT_TOKEN" ]; then
    echo "无法获取 GitHub Token，跳过推送。"
    exit 0
fi

git remote set-url origin "https://oauth2:${GIT_TOKEN}@github.com/tauwork/us-stock-310-agent.git" 2>/dev/null || true

# 3. 提交并推送
echo ""
echo "[3/3] 正在提交到 GitHub..."
git add data/kol/ scripts/
REPORT_DATE=$(date '+%Y%m%d')

if git diff --cached --quiet; then
    echo "没有新的变更需要提交。"
else
    git -c user.name="Stock Advisor Bot" \
        -c user.email="stock-advisor@bot.local" \
        commit -m "🎯 KOL聚合分析报告: ${REPORT_DATE}"
    
    echo ""
    git push origin main
fi

echo ""
echo "=========================================="
echo "  ✅ KOL报告生成与发布完成！"
echo "=========================================="
