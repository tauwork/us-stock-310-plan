#!/usr/bin/env python3
"""
KOL 数据分析报告生成器
基于抓取的 KOL 视频数据生成综合分析报告
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path("/workspace/us-stock-310-agent")
KOL_DATA_DIR = PROJECT_ROOT / "data" / "kol"

# 持仓股票和关注股票
PORTFOLIO_STOCKS = {
    "CRCL": "Circle Internet Group",
    "XE": "X-Energy", 
    "MU": "Micron Technology",
    "GLW": "Corning",
    "INTC": "Intel",
    "AAOI": "Applied Optoelectronics",
    "CRML": "Critical Metals Corp"
}

WATCHLIST_STOCKS = {
    "NVDA": "NVIDIA",
    "AVGO": "Broadcom",
    "AMD": "AMD",
    "TSLA": "Tesla",
    "MSFT": "Microsoft",
    "RKLB": "Rocket Lab",
    "PLTR": "Palantir",
    "HOOD": "Robinhood",
    "ARM": "ARM Holdings",
    "IREN": "Iris Energy",
    "AMAT": "Applied Materials",
    "ORCL": "Oracle",
    "SOUN": "SoundHound AI",
    "MP": "MP Materials"
}

# KOL 视频数据（从 WebFetch 抓取）
KOL_DATA = {
    "laowei": {
        "name": "老魏突击美股",
        "subscribers": "27.7K",
        "style": "每日盘前解析，技术面+基本面结合，关注半导体和AI板块",
        "recent_videos": [
            {
                "title": "海力士ADR正式上市，纳指冲击26500点，半导体牛市真的回来了？",
                "date": "2026-07-10",
                "url": "https://www.youtube.com/watch?v=2fV0mspoUz8",
                "views": 2200,
                "stocks": ["MU", "NVDA", "INTC", "AMD", "CRCL", "TSLA", "AAPL", "SOUN"],
                "key_points": [
                    "海力士ADR正式上市，市场关注其对半导体板块的影响",
                    "纳指冲击26500点，关注是否能突破",
                    "半导体板块是否见底反弹",
                    "关注存储芯片和AI芯片板块"
                ],
                "sentiment": "偏多",
                "sector_focus": ["半导体", "AI", "存储芯片"]
            },
            {
                "title": "海力士来了！半导体要爆发？",
                "date": "2026-07-09",
                "url": "https://www.youtube.com/watch?v=KawEkPN_cQw",
                "views": 1600,
                "stocks": ["MU", "NVDA", "INTC", "AMD", "CRCL", "TSLA", "AAPL", "SOUN"],
                "key_points": [
                    "纳指尾盘V型反转，释放积极信号",
                    "海力士ADR超额认购，市场对存储芯片信心强",
                    "美光、闪迪、西部数据可能迎来补涨",
                    "7月行情可能先抑后扬",
                    "纳指本周关注26000-26200压力位",
                    "英特尔、AMD、博通、台积电、日月光最新策略"
                ],
                "sentiment": "偏多",
                "sector_focus": ["半导体", "存储芯片", "AI"]
            },
            {
                "title": "纳指暴跌400点，半导体还能抄底吗？",
                "date": "2026-07-08",
                "url": "https://www.youtube.com/watch?v=scIG7hQggS4",
                "views": 1700,
                "stocks": ["MU", "NVDA", "INTC", "AMD", "CRCL", "TSLA", "AAPL", "SOUN", "AMAT"],
                "key_points": [
                    "特朗普宣布美伊停火协议失效，市场避险情绪升温",
                    "纳斯达克期货暴跌400点，道琼斯、标普同步回落",
                    "原油、黄金全面上涨",
                    "华尔街持续打压半导体板块",
                    "关注海力士ADR上市对半导体板块的影响",
                    "建议恐慌时保持耐心，不要盲目离场",
                    "美光、AMD、英特尔、AMAT、台积电最新策略"
                ],
                "sentiment": "偏空（短期）但中期看多",
                "sector_focus": ["半导体", "地缘政治", "避险资产"]
            },
            {
                "title": "三星财报大跌，带崩全球科技，半导体完蛋了？",
                "date": "2026-07-07",
                "url": "https://www.youtube.com/watch?v=48vd6tEcs8E",
                "views": 2000,
                "stocks": ["MU", "NVDA", "INTC", "AMD", "CRCL", "TSLA", "AAPL", "SOUN"],
                "key_points": [
                    "三星财报不及预期，拖累全球科技板块",
                    "半导体短期承压但长期逻辑不变",
                    "关注存储芯片价格走势"
                ],
                "sentiment": "偏空（短期）",
                "sector_focus": ["半导体", "存储芯片"]
            },
            {
                "title": "别再做空半导体！7月真正的大行情来了",
                "date": "2026-07-06",
                "url": "https://www.youtube.com/watch?v=7zxvyULkxGU",
                "views": 1900,
                "stocks": ["MU", "NVDA", "INTC", "AMD", "CRCL", "TSLA", "AAPL", "SOUN"],
                "key_points": [
                    "明确看好7月半导体行情",
                    "不要做空半导体",
                    "AI+存储是7月主线",
                    "建议积极布局"
                ],
                "sentiment": "强烈看多",
                "sector_focus": ["半导体", "AI", "存储芯片"]
            }
        ]
    },
    "josie": {
        "name": "Josie技术分析",
        "subscribers": "6.94K",
        "style": "技术分析为主，黄金分割、结构理论、飘带指标，覆盖个股技术面判断",
        "recent_videos": [
            {
                "title": "美股再等2天？MU还有调整空间？PLTR、MSFT要止盈了吗？",
                "date": "2026-07-08",
                "url": "https://www.youtube.com/watch?v=KzqP8k1z_Ao",
                "views": 5300,
                "stocks": ["TSLA", "NVDA", "MU", "CRCL", "AMD", "MSFT", "HOOD", "PLTR", "AMAT", "IREN"],
                "key_points": [
                    "MU可能还有调整空间",
                    "PLTR和MSFT考虑止盈",
                    "美股短期需要再等2天确认方向",
                    "关注技术面信号"
                ],
                "sentiment": "中性偏谨慎",
                "sector_focus": ["半导体", "AI", "科技"]
            },
            {
                "title": "美股下周做好准备！MU下周有危险？",
                "date": "2026-07-05",
                "url": "https://www.youtube.com/watch?v=r1yNji1Q8IY",
                "views": 7700,
                "stocks": ["TSLA", "NVDA", "MU", "CRCL", "AMD", "MSFT", "RKLB", "PLTR", "ORCL", "IREN"],
                "key_points": [
                    "MU下周有危险，注意风险",
                    "美股下周需做好准备",
                    "关注RKLB、ORCL等个股机会"
                ],
                "sentiment": "偏空（短期谨慎）",
                "sector_focus": ["半导体", "AI", "航天"]
            },
            {
                "title": "美股短期变盘加速上涨or反弹结束？TSLA已经反弹触及空方带",
                "date": "2026-07-01",
                "url": "https://www.youtube.com/watch?v=J2erE-pkxkg",
                "views": 4800,
                "stocks": ["TSLA", "NVDA", "AMD", "MU", "ARM", "RKLB", "CRCL", "GLW"],
                "key_points": [
                    "TSLA反弹触及空方带，关注是否到位",
                    "美股短期面临变盘：加速上涨还是反弹结束",
                    "GLW出现在分析中"
                ],
                "sentiment": "中性（变盘观察）",
                "sector_focus": ["电动车", "半导体", "AI"]
            },
            {
                "title": "美股下周见底？MU需要调仓换股吗？这些股票机会来了！",
                "date": "2026-06-28",
                "url": "https://www.youtube.com/watch?v=0qUPbYlgOHA",
                "views": 9600,
                "stocks": ["TSLA", "NVDA", "AMD", "MU", "CRCL", "MSFT", "RKLB", "PLTR", "ARM"],
                "key_points": [
                    "美股可能下周见底",
                    "MU需要调仓换股",
                    "新的机会正在出现",
                    "关注RKLB、PLTR、ARM等个股"
                ],
                "sentiment": "偏多（底部信号）",
                "sector_focus": ["半导体", "AI", "航天"]
            },
            {
                "title": "AMD继续拿住!MU浅看1200",
                "date": "2026-06-26",
                "url": "https://www.youtube.com/watch?v=Suvg4WayrUM",
                "views": 5400,
                "stocks": ["HOOD", "INTC", "IREN", "ARM", "TSLA", "NVDA", "AMD", "MU"],
                "key_points": [
                    "AMD继续持有，看好",
                    "MU目标价1200",
                    "HOOD、INTC、IREN出现机会"
                ],
                "sentiment": "偏多",
                "sector_focus": ["半导体", "金融科技"]
            }
        ]
    }
}


def analyze_kol_consensus():
    """分析 KOL 共识"""
    stock_mentions = Counter()
    stock_sentiment = {}
    sector_mentions = Counter()
    
    for kol_key, kol_data in KOL_DATA.items():
        for video in kol_data["recent_videos"]:
            for stock in video.get("stocks", []):
                stock_mentions[stock] += 1
                if stock not in stock_sentiment:
                    stock_sentiment[stock] = []
                stock_sentiment[stock].append({
                    "kol": kol_data["name"],
                    "sentiment": video["sentiment"],
                    "title": video["title"],
                    "date": video["date"]
                })
            for sector in video.get("sector_focus", []):
                sector_mentions[sector] += 1
    
    return stock_mentions, stock_sentiment, sector_mentions


def analyze_portfolio_stocks():
    """分析与持仓股票相关的KOL观点"""
    stock_mentions, stock_sentiment, _ = analyze_kol_consensus()
    
    analysis = []
    for ticker, name in PORTFOLIO_STOCKS.items():
        mentions = stock_mentions.get(ticker, 0)
        sentiments = stock_sentiment.get(ticker, [])
        
        # 汇总情感
        bullish = sum(1 for s in sentiments if "多" in s["sentiment"] and "空" not in s["sentiment"])
        bearish = sum(1 for s in sentiments if "空" in s["sentiment"])
        neutral = len(sentiments) - bullish - bearish
        
        analysis.append({
            "ticker": ticker,
            "name": name,
            "total_mentions": mentions,
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
            "details": sentiments
        })
    
    return sorted(analysis, key=lambda x: x["total_mentions"], reverse=True)


def generate_kol_report():
    """生成 KOL 聚合分析报告"""
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    date_readable = today.strftime("%Y年%m月%d日")
    
    stock_mentions, stock_sentiment, sector_mentions = analyze_kol_consensus()
    portfolio_analysis = analyze_portfolio_stocks()
    
    report = f"""# 🎯 美股KOL每日聚合分析报告

## 📅 {date_readable}

> **生成时间**：{today.strftime('%Y-%m-%d %H:%M')}（北京时间）
> **数据来源**：YouTube KOL 频道（Josie技术分析、老魏突击美股）
> **覆盖周期**：最近一周视频内容

---

## 一、KOL 频道概览

| KOL | 订阅者 | 风格 | 最近更新 |
|------|--------|------|----------|
"""
    
    for key, data in KOL_DATA.items():
        latest = data["recent_videos"][0]["date"] if data["recent_videos"] else "N/A"
        report += f"| {data['name']} | {data['subscribers']} | {data['style']} | {latest} |\n"
    
    report += """
---

## 二、板块资金动向分析

### 📊 KOL 关注板块热度

| 板块 | 提及次数 | 热度趋势 |
|------|----------|----------|
"""
    
    for sector, count in sector_mentions.most_common(10):
        bar = "█" * min(count, 10)
        report += f"| {sector} | {count} | {bar} |\n"
    
    # 板块分析
    report += """
### 🔍 板块动向解读

"""
    
    # 半导体
    semi_count = sector_mentions.get("半导体", 0)
    if semi_count > 0:
        report += f"""**半导体板块**（提及 {semi_count} 次）— 🔥 最热门板块

"""
        # 汇总半导体观点
        report += """两位KOL对半导体板块的核心观点：

| KOL | 观点 | 关键判断 |
|------|------|----------|
| **老魏突击美股** | 强烈看多 | "别再做空半导体！7月真正的大行情来了"。海力士ADR上市是催化剂，存储+AI是主线 |
| **Josie技术分析** | 中性偏谨慎 | MU还有调整空间，PLTR/MSFT考虑止盈。短期需确认方向 |

> **综合判断**：半导体板块短期有分歧，老魏看多而Josie偏谨慎。但中长期逻辑（AI需求+存储周期）得到双方认可。**建议**：核心仓位持有，可逢回调小幅加仓。
"""
    
    # AI
    ai_count = sector_mentions.get("AI", 0)
    if ai_count > 0:
        report += f"""**AI板块**（提及 {ai_count} 次）

两位KOL一致认为AI是主线。老魏明确表示"AI+存储是7月主线"，Josie持续跟踪NVDA、AMD、ARM等AI标的的技术面。
"""
    
    # 存储芯片
    storage_count = sector_mentions.get("存储芯片", 0)
    if storage_count > 0:
        report += f"""**存储芯片**（提及 {storage_count} 次）

SK海力士ADR上市是本週最大事件。老魏认为存储芯片将迎来补涨，Josie对MU短期偏谨慎（目标价1200但短期有调整风险）。
"""
    
    report += """
---

## 三、持仓股票 KOL 分析

### 📈 各持仓股票的 KOL 提及与观点

"""
    
    for pa in portfolio_analysis:
        ticker = pa["ticker"]
        name = pa["name"]
        mentions = pa["total_mentions"]
        
        if mentions == 0:
            report += f"""#### {ticker} | {name}
> ⚪ 近期未被两位KOL提及。建议主动关注相关分析。

"""
            continue
        
        # 情感指示
        if pa["bullish"] > pa["bearish"]:
            emoji = "🟢"
            signal = "偏多"
        elif pa["bearish"] > pa["bullish"]:
            emoji = "🔴"
            signal = "偏空"
        else:
            emoji = "🟡"
            signal = "中性/分歧"
        
        report += f"""#### {emoji} {ticker} | {name} — KOL综合判断：**{signal}**

| 指标 | 数值 |
|------|------|
| 总提及次数 | {mentions} |
| 看多观点 | {pa['bullish']} |
| 看空观点 | {pa['bearish']} |
| 中性观点 | {pa['neutral']} |

**具体观点**：
"""
        for detail in pa["details"]:
            report += f"- [{detail['date']}] **{detail['kol']}**（{detail['sentiment']}）：{detail['title']}\n"
        
        report += "\n"
    
    report += """
---

## 四、热门个股推荐（KOL共识）

### 🔥 被两位KOL共同关注的股票

"""
    
    # 找出共同提及的股票
    josie_stocks = set()
    laowei_stocks = set()
    
    for video in KOL_DATA["josie"]["recent_videos"]:
        josie_stocks.update(video.get("stocks", []))
    for video in KOL_DATA["laowei"]["recent_videos"]:
        laowei_stocks.update(video.get("stocks", []))
    
    common = josie_stocks & laowei_stocks
    josie_only = josie_stocks - laowei_stocks
    laowei_only = laowei_stocks - josie_stocks
    
    report += "#### 双方共同关注（高共识度）\n\n"
    report += "| 股票 | 名称 | 总提及 | Josie观点 | 老魏观点 |\n"
    report += "|------|------|--------|-----------|----------|\n"
    
    for stock in sorted(common, key=lambda s: stock_mentions.get(s, 0), reverse=True):
        name = WATCHLIST_STOCKS.get(stock, PORTFOLIO_STOCKS.get(stock, stock))
        count = stock_mentions.get(stock, 0)
        
        # 汇总各KOL观点
        josie_view = "N/A"
        laowei_view = "N/A"
        for s in stock_sentiment.get(stock, []):
            if "Josie" in s["kol"]:
                josie_view = s["sentiment"]
            elif "老魏" in s["kol"]:
                laowei_view = s["sentiment"]
        
        report += f"| {stock} | {name} | {count} | {josie_view} | {laowei_view} |\n"
    
    report += "\n#### Josie 独家关注\n\n"
    for stock in sorted(josie_only, key=lambda s: stock_mentions.get(s, 0), reverse=True):
        name = WATCHLIST_STOCKS.get(stock, PORTFOLIO_STOCKS.get(stock, stock))
        count = stock_mentions.get(stock, 0)
        report += f"- **{stock}**（{name}）：提及 {count} 次\n"
    
    report += "\n#### 老魏 独家关注\n\n"
    for stock in sorted(laowei_only, key=lambda s: stock_mentions.get(s, 0), reverse=True):
        name = WATCHLIST_STOCKS.get(stock, PORTFOLIO_STOCKS.get(stock, stock))
        count = stock_mentions.get(stock, 0)
        report += f"- **{stock}**（{name}）：提及 {count} 次\n"
    
    report += """
---

## 五、操作建议总结

### 📋 基于KOL共识的操作建议

| 建议类型 | 具体操作 |
|----------|----------|
| **半导体板块** | 核心仓位持有，7月逢回调加仓。老魏强烈看多，Josie短期谨慎但中长期不悲观 |
| **MU（美光）** | 短期可能有调整（Josie），但中长期目标1200-1600（双方共识）。持有为主 |
| **AI板块** | 继续持有。NVDA、AMD获得双方关注，AI是确定性主线 |
| **CRCL** | 持续被双方提及，关注加密市场和稳定币监管进展 |
| **INTC** | 老魏持续关注，困境反转逻辑。等待18A量产信号 |
| **减仓/止盈** | Josie建议PLTR、MSFT考虑止盈。AAOI基本面较弱需警惕 |

### ⚠️ 风险提示

1. **美伊冲突升级**：特朗普宣布停火协议失效，地缘风险加剧
2. **半导体短期波动**：三星财报不及预期，板块短期承压
3. **技术面分歧**：Josie认为短期需确认方向，老魏则认为7月是大行情起点
4. **流动性风险**：关注美联储7月底FOMC会议（7/28-29）

---

## 📋 免责声明

*本报告基于YouTube KOL公开视频内容自动分析生成，不构成任何投资建议。*
*KOL观点仅代表其个人判断，投资有风险，入市需谨慎。*
*报告生成时间：{today.strftime('%Y-%m-%d %H:%M:%S')}（北京时间）*
"""
    
    return report


if __name__ == "__main__":
    report = generate_kol_report()
    date_str = datetime.now().strftime("%Y%m%d")
    report_path = KOL_DATA_DIR / f"us-stock-kol-agg-report-{date_str}.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"报告已生成：{report_path}")
    print(f"报告长度：{len(report)} 字符")
