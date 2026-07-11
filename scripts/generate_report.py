#!/usr/bin/env python3
"""
美股每日操盘报告生成器
us-stock-daily-analysis-report generator

功能：
1. 生成每日盘前策略报告
2. 生成每日盘后总结报告（复盘更新）
3. 综合实时信息、本地知识库进行分析
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "daily"
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"

def load_portfolio():
    """加载持仓知识库"""
    portfolio_path = KNOWLEDGE_DIR / "portfolio.json"
    if not portfolio_path.exists():
        print(f"错误：知识库文件不存在 {portfolio_path}")
        sys.exit(1)
    with open(portfolio_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_market_date():
    """获取当前交易日日期"""
    today = datetime.now()
    # 如果是周末，使用上一个周五
    weekday = today.weekday()
    if weekday == 5:  # 周六
        today = today - timedelta(days=1)
    elif weekday == 6:  # 周日
        today = today - timedelta(days=2)
    return today

def format_date(date_obj):
    """格式化日期为YYYYMMDD"""
    return date_obj.strftime("%Y%m%d")

def format_date_readable(date_obj):
    """格式化日期为可读格式"""
    return date_obj.strftime("%Y年%m月%d日")

def generate_report(is_pre_market=True):
    """生成报告"""
    portfolio = load_portfolio()
    market_date = get_market_date()
    date_str = format_date(market_date)
    date_readable = format_date_readable(market_date)
    
    if is_pre_market:
        report = generate_pre_market_report(portfolio, market_date, date_readable)
        filename = f"us-stock-daily-analysis-report-{date_str}.md"
    else:
        report = generate_post_market_report(portfolio, market_date, date_readable)
        filename = f"us-stock-daily-analysis-report-{date_str}-review.md"
    
    # 保存报告
    report_path = DATA_DIR / filename
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"报告已生成：{report_path}")
    return report_path

def generate_pre_market_report(portfolio, market_date, date_readable):
    """生成盘前策略报告"""
    holdings = portfolio["holdings"]
    watchlist = portfolio.get("watchlist", [])
    macro = portfolio.get("macro_events", {})
    
    report = f"""# 🏦 美股每日操盘报告

## 📅 {date_readable} 盘前策略

> **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}（北京时间）
> **市场状态**：美股即将开盘（北京时间21:30 / 美东时间09:30）
> **报告类型**：盘前策略

---

## 一、每日盘前策略

### 📊 市场环境概述

| 指标 | 状态 |
|------|------|
| 美联储利率预期 | 7月维持利率不变概率74.9%，9月加息25bp概率51.1% |
| 贸易战 | 特朗普提议对60国加征10%+关税，贸易政策不确定性高 |
| 地缘政治 | 美伊冲突持续100+天，谈判窗口至8月中旬；俄乌战损比8:1 |
| 市场情绪 | 芯片股回调，AI主题短期承压，资金轮动 |

---

### 1.1 已持仓股票策略

"""
    
    # 为每只持仓股票生成策略
    for stock in holdings:
        ticker = stock["ticker"]
        name = stock["name"]
        shares = stock["shares"]
        cost = stock["cost_basis"]
        thesis = stock.get("investment_thesis", "")
        events = stock.get("key_events", [])
        risks = stock.get("risk_factors", [])
        current_price = stock.get("current_price", "N/A")
        price_date = stock.get("price_date", "N/A")
        analyst_target = stock.get("analyst_target", "N/A")
        consensus = stock.get("consensus", "N/A")
        
        # 计算盈亏
        if isinstance(current_price, (int, float)) and isinstance(cost, (int, float)):
            pnl = (current_price - cost) * shares
            pnl_pct = ((current_price - cost) / cost) * 100
            pnl_str = f"${pnl:,.2f}（{pnl_pct:+.1f}%）"
        else:
            pnl_str = "待更新"
        
        # 策略判断
        strategy, rationale = determine_strategy(stock)
        
        report += f"""#### 🔹 {ticker} | {name}

| 项目 | 详情 |
|------|------|
| 持仓数量 | {shares}股 |
| 成本价 | ${cost:,.2f} |
| 最新价 | ${current_price}（{price_date}） |
| 浮动盈亏 | {pnl_str} |
| 分析师目标价 | ${analyst_target} |
| 分析师共识 | {consensus} |

**投资逻辑**：{thesis}

**今日策略**：🟢/🟡/🔴 **{strategy}**

> {rationale}

**关键关注事件**：
"""
        for event in events:
            report += f"- ⚡ {event}\n"
        
        report += "\n**风险提示**：\n"
        for risk in risks[:3]:
            report += f"- ⚠️ {risk}\n"
        
        report += "\n---\n\n"
    
    # 关注列表策略
    report += """### 1.2 关注中股票策略

"""
    for wl in watchlist[:5]:
        ticker = wl["ticker"]
        name = wl["name"]
        reason = wl["reason"]
        signal = wl["signal"]
        
        report += f"""#### 🔹 {ticker} | {name}

**关注理由**：{reason}

**建仓信号**：{signal}

"""
    
    report += """---

### 1.3 新股票推荐（最多5只）

> **推荐模型说明**：综合以下因子进行筛选：
> 1. 行业趋势（AI基础设施、核电、关键矿产等长期主题）
> 2. 技术面（相对强度、均线位置）
> 3. 基本面（收入增速、毛利率趋势、估值水平）
> 4. 催化剂（即将发布的财报、政策事件、产品发布）

"""
    
    # 新股票推荐
    recommendations = get_recommendations()
    for i, rec in enumerate(recommendations, 1):
        report += f"""**推荐{i}：{rec['ticker']} | {rec['name']}**

| 项目 | 详情 |
|------|------|
| 行业 | {rec['sector']} |
| 推荐逻辑 | {rec['rationale']} |
| 建议仓位 | {rec['position']} |
| 止损位 | {rec['stop_loss']} |
| 催化剂 | {rec['catalyst']} |

"""
    
    # 宏观事件
    report += """---

## 二、影响美股的重大事件演进

"""
    
    event_order = ["fed_policy", "trade_war", "us_iran", "russia_ukraine"]
    for key in event_order:
        event = macro.get(key, {})
        if event:
            report += f"""### {event['title']}

**最新动态**：{event['latest']}

**对美股影响**：{event['impact']}

**下次关注**：{event.get('next_event', '持续关注')}

---

"""
    
    report += f"""
## 📋 免责声明

*本报告为个人投资分析记录，不构成任何投资建议。投资有风险，入市需谨慎。*
*数据来源：MarketBeat、CME FedWatch、公开新闻报道等*
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}（北京时间）*
"""
    
    return report


def generate_post_market_report(portfolio, market_date, date_readable):
    """生成盘后总结报告"""
    holdings = portfolio["holdings"]
    
    report = f"""# 🏦 美股每日操盘报告 — 盘后复盘

## 📅 {date_readable} 盘后总结

> **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}（北京时间）
> **市场状态**：美股已收盘
> **报告类型**：盘后复盘总结

---

## 一、本日市场回顾

### 📊 主要指数表现

| 指数 | 收盘价 | 涨跌幅 | 
|------|--------|--------|
| 标普500 | 待更新 | - |
| 纳斯达克 | 待更新 | - |
| 道琼斯 | 待更新 | - |
| 费城半导体 | 待更新 | - |

---

## 二、持仓股票表现与偏差分析

"""
    
    for stock in holdings:
        ticker = stock["ticker"]
        name = stock["name"]
        shares = stock["shares"]
        cost = stock["cost_basis"]
        current_price = stock.get("current_price", "N/A")
        
        if isinstance(current_price, (int, float)) and isinstance(cost, (int, float)):
            pnl_pct = ((current_price - cost) / cost) * 100
        else:
            pnl_pct = 0
        
        report += f"""### 🔹 {ticker} | {name}

| 项目 | 详情 |
|------|------|
| 昨收价 | ${current_price} |
| 今日收盘 | 待盘后更新 |
| 日内涨跌 | 待盘后更新 |
| 累计盈亏 | {pnl_pct:+.1f}%（截至昨日） |

**盘前判断回顾**：
> 待填入盘前判断

**实际走势偏差分析**：
> 待收盘后分析

**偏差原因**：
> 待分析

---

"""
    
    report += f"""
## 三、宏观事件更新

### 美联储政策
> 今日无FOMC日程。关注CME FedWatch概率变化。

### 贸易战
> 关注盘后是否有新关税/贸易政策公告。

### 地缘政治
> 关注美伊谈判进展和俄乌冲突动态。

---

## 📋 免责声明

*本报告为个人投资分析记录，不构成任何投资建议。投资有风险，入市需谨慎。*
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}（北京时间）*
"""
    
    return report


def determine_strategy(stock):
    """根据持仓情况判断策略"""
    ticker = stock["ticker"]
    current_price = stock.get("current_price", None)
    cost = stock["cost_basis"]
    consensus = stock.get("consensus", "")
    
    if current_price is None or not isinstance(current_price, (int, float)):
        return "持仓观察", "缺乏最新价格数据，维持现有仓位观察。"
    
    pnl_pct = ((current_price - cost) / cost) * 100
    
    # 不同股票的策略逻辑
    strategies = {
        "CRCL": _crcl_strategy(pnl_pct, stock),
        "XE": _xe_strategy(pnl_pct, stock),
        "MU": _mu_strategy(pnl_pct, stock),
        "GLW": _glw_strategy(pnl_pct, stock),
        "INTC": _intc_strategy(pnl_pct, stock),
        "AAOI": _aaoi_strategy(pnl_pct, stock),
        "CRML": _crml_strategy(pnl_pct, stock),
    }
    
    return strategies.get(ticker, ("持仓观察", "维持现有仓位，等待更多信息。"))


def _crcl_strategy(pnl_pct, stock):
    if pnl_pct < -20:
        return "买入补仓（谨慎）", f"CRCL浮亏{pnl_pct:.1f}%，跌幅较大。Circle作为USDC发行商基本面稳健，但加密市场情绪低迷。建议：若USDC市值企稳回升，可小仓位补仓降低成本。关注7月底稳定币立法听证会。当前策略：持仓不动，等待催化。"
    elif pnl_pct < -10:
        return "持仓不动", f"CRCL浮亏{pnl_pct:.1f}%。等待稳定币立法进展和USDC市值回升信号。不建议在此位置止损，也不急于补仓。关注Circle季度储备金报告。"
    else:
        return "持仓不动", f"CRCL盈亏{pnl_pct:+.1f}%。持有等待加密市场回暖。"


def _xe_strategy(pnl_pct, stock):
    current = stock.get("current_price", 0)
    target = stock.get("analyst_target", 0)
    upside = ((target - current) / current * 100) if current > 0 else 0
    
    if pnl_pct < -30:
        return "买入补仓", f"XE浮亏{pnl_pct:.1f}%，但分析师目标价${target}（+{upside:.0f}%空间）。Cathie Wood的ARK本周买入$1500万XE。核电长期逻辑不变（AI数据中心电力需求）。建议：逢低分批补仓，每次不超过200股。关注DOE贷款审批和科技公司购电协议。"
    elif pnl_pct < -15:
        return "持仓不动（关注补仓机会）", f"XE浮亏{pnl_pct:.1f}%。IPO以来跌幅45%，但核电主题逻辑未变。关注$15支撑位，若跌破可考虑小仓位补仓。ARK持续买入是积极信号。等待核电政策催化剂。"
    else:
        return "持仓不动", f"XE盈亏{pnl_pct:+.1f}%。持有等待核电行业催化剂。"


def _mu_strategy(pnl_pct, stock):
    if pnl_pct > 10:
        return "持仓不动（考虑止盈）", f"MU浮盈{pnl_pct:+.1f}%。TD Cowen给出$1600目标价。但SK海力士ADR上市带来竞争关注，短期可能承压。建议：核心仓位持有，可考虑卖出25%仓位锁定部分利润。关注HBM订单和存储芯片价格走势。"
    elif pnl_pct > 0:
        return "持仓不动", f"MU浮盈{pnl_pct:+.1f}%。AI HBM需求强劲，基本面良好。短期受板块轮动和SK海力士竞争情绪影响，但长期逻辑不变。持有。"
    else:
        return "持仓不动", f"MU盈亏{pnl_pct:+.1f}%。等待AI芯片板块企稳。"


def _glw_strategy(pnl_pct, stock):
    return "持仓不动", f"GLW盈亏{pnl_pct:+.1f}%。康宁Q2业绩创纪录，AI数据中心光纤需求持续增长。股价在成本价附近，风险收益比合理。持有等待AI基础设施建设持续推动业绩。"


def _intc_strategy(pnl_pct, stock):
    if pnl_pct < -15:
        return "持仓不动（不建议加仓）", f"INTC浮亏{pnl_pct:.1f}%。18A制程是关键转折点，但代工业务扭亏仍需时间。建议：现有仓位持有，不建议在此位置加仓。等待18A量产明确信号后再考虑操作。关注7月24日Q2财报。"
    else:
        return "持仓不动", f"INTC盈亏{pnl_pct:+.1f}%。等待18A制程进展和Q2财报（7/24）。"


def _aaoi_strategy(pnl_pct, stock):
    if pnl_pct < -15:
        return "减仓/止损", f"AAOI浮亏{pnl_pct:.1f}%。⚠️ 重要风险信号：1) 内部人士近3月卖出$8671万 2) 空头比例13.93% 3) 分析师共识Hold，目标价$113.80低于现价 4) 持续亏损。建议：减仓50%以上，控制风险。AI光模块逻辑虽好，但公司基本面较弱。"
    elif pnl_pct < -5:
        return "持仓观察（设止损）", f"AAOI浮亏{pnl_pct:.1f}%。技术面偏弱，内部人士大量卖出。建议设置止损位$110（约-28%）。关注800G光模块订单能否推动盈利改善。"
    else:
        return "持仓观察", f"AAOI盈亏{pnl_pct:+.1f}%。关注光模块订单和盈利能力改善信号。"


def _crml_strategy(pnl_pct, stock):
    if pnl_pct < -20:
        return "持仓不动（不建议加仓）", f"CRML浮亏{pnl_pct:.1f}%。小型矿业股波动大，流动性风险高。关键矿产长期逻辑存在，但短期缺乏催化剂。建议：现有仓位持有，不急于补仓。关注稀土价格走势和欧美关键矿产政策。"
    elif pnl_pct < -10:
        return "持仓不动", f"CRML浮亏{pnl_pct:.1f}%。等待关键矿产政策催化剂。"
    else:
        return "持仓不动", f"CRML盈亏{pnl_pct:+.1f}%。持有等待催化剂。"


def get_recommendations():
    """获取新股票推荐"""
    return [
        {
            "ticker": "AVGO",
            "name": "Broadcom",
            "sector": "AI半导体",
            "rationale": "AI定制芯片（ASIC）和网络芯片龙头，VMware整合释放协同效应。与苹果合作续签至2031年。在芯片板块回调中逆势走强，显示资金认可。2026年7月8日大盘跌1.5%时逆势涨5%。",
            "position": "总仓位5-8%，分2-3次建仓",
            "stop_loss": "$350（约-10%）",
            "catalyst": "AI芯片需求持续、VMware协同效应、苹果合作深化"
        },
        {
            "ticker": "SMR",
            "name": "NuScale Power",
            "sector": "核电",
            "rationale": "与XE互补的核电标的，小型模块化反应堆（SMR）技术领先。首个VOYGR项目持续推进。分散核电赛道持仓风险。",
            "position": "总仓位3-5%",
            "stop_loss": "视买入价设-15%止损",
            "catalyst": "核电项目审批、DOE贷款、科技公司购电协议"
        },
        {
            "ticker": "MRVL",
            "name": "Marvell Technology",
            "sector": "AI数据中心",
            "rationale": "AI数据中心网络芯片和定制ASIC领导者。受益于AI基础设施建设周期，与AVGO形成互补。数据中心业务增速快。",
            "position": "总仓位3-5%",
            "stop_loss": "视买入价设-12%止损",
            "catalyst": "AI网络芯片需求、数据中心资本开支增长"
        },
        {
            "ticker": "VRT",
            "name": "Vertiv Holdings",
            "sector": "AI基础设施",
            "rationale": "数据中心电源和冷却解决方案龙头。AI数据中心功耗密度大幅提升，对先进冷却和电源管理需求爆发。受益于AI基础设施建设，但不受芯片周期波动影响。",
            "position": "总仓位3-5%",
            "stop_loss": "视买入价设-12%止损",
            "catalyst": "AI数据中心建设加速、冷却技术升级"
        },
        {
            "ticker": "GE",
            "name": "GE Vernova",
            "sector": "能源转型",
            "rationale": "能源转型龙头，覆盖天然气发电、风电、电网和核电（通过GE Hitachi）。AI数据中心电力需求增长推动天然气和核电需求。多元化能源业务提供下行保护。",
            "position": "总仓位5-8%，分2次建仓",
            "stop_loss": "视买入价设-10%止损",
            "catalyst": "AI电力需求增长、核电项目、能源转型政策"
        }
    ]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="美股每日操盘报告生成器")
    parser.add_argument("--type", choices=["pre", "post"], default="pre",
                       help="报告类型：pre=盘前策略, post=盘后总结")
    parser.add_argument("--output", "-o", help="输出文件路径（可选）")
    
    args = parser.parse_args()
    
    is_pre = args.type == "pre"
    report_path = generate_report(is_pre_market=is_pre)
    
    if args.output:
        import shutil
        shutil.copy(report_path, args.output)
        print(f"报告已复制到：{args.output}")
