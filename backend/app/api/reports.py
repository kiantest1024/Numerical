"""
报告生成API路由
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any
import json
import os
import tempfile
from datetime import datetime
import pandas as pd

from ..core.config import settings

# 导入模拟相关的存储
from .simulation import simulation_results, running_simulations

router = APIRouter()

# 报告存储路径
REPORTS_DIR = settings.REPORTS_DIR
os.makedirs(REPORTS_DIR, exist_ok=True)


@router.get("/generate/{simulation_id}")
async def generate_report(simulation_id: str, format: str = "html"):
    """生成模拟报告"""
    if format not in ["html", "json", "excel"]:
        raise HTTPException(status_code=400, detail="不支持的报告格式")

    try:
        if format == "html":
            return await generate_html_report(simulation_id)
        elif format == "json":
            return await generate_json_report(simulation_id)
        elif format == "excel":
            return await generate_excel_report(simulation_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")


async def generate_html_report(simulation_id: str) -> str:
    """生成HTML报告"""

    # 获取真实的模拟数据
    simulation_data = None
    if simulation_id in simulation_results:
        simulation_data = simulation_results[simulation_id]
    elif simulation_id in running_simulations:
        # 如果模拟还在运行中，获取当前状态
        engine = running_simulations[simulation_id]
        simulation_data = {
            'summary': {
                'total_rounds': len(engine.round_results),
                'total_bet_amount': sum(r.total_bet_amount for r in engine.round_results),
                'total_payout': sum(r.total_payout for r in engine.round_results),
                'average_rtp': sum(r.rtp for r in engine.round_results) / len(engine.round_results) if engine.round_results else 0,
                'final_jackpot': engine.jackpot_pool
            },
            'round_results': engine.round_results,
            'game_name': engine.game_rules.name,
            'start_time': engine.start_time,
            'status': 'running'
        }

    # 如果没有找到数据，使用默认值
    if not simulation_data:
        simulation_data = {
            'summary': {
                'total_rounds': 0,
                'total_bet_amount': 0,
                'total_payout': 0,
                'average_rtp': 0,
                'final_jackpot': 0
            },
            'round_results': [],
            'game_name': '未知游戏',
            'start_time': datetime.now(),
            'status': 'not_found'
        }

    # 计算详细统计数据
    summary = simulation_data.get('summary', {})
    round_results = simulation_data.get('round_results', [])

    # 计算奖级统计
    prize_stats = {}
    total_winners = 0
    if round_results:
        for round_result in round_results:
            for prize_stat in round_result.prize_stats:
                level = prize_stat.level
                if level not in prize_stats:
                    prize_stats[level] = {
                        'name': prize_stat.name,
                        'winners_count': 0,
                        'total_amount': 0
                    }
                prize_stats[level]['winners_count'] += prize_stat.winners_count
                prize_stats[level]['total_amount'] += prize_stat.total_amount
                total_winners += prize_stat.winners_count

    # HTML报告模板
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>@numericalTools 模拟报告</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                border-bottom: 2px solid #007bff;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            .header h1 {
                color: #007bff;
                margin: 0;
                font-size: 2.5em;
            }
            .header p {
                color: #666;
                margin: 10px 0 0 0;
                font-size: 1.1em;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .summary-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            .summary-card h3 {
                margin: 0 0 10px 0;
                font-size: 1.2em;
                opacity: 0.9;
            }
            .summary-card .value {
                font-size: 2em;
                font-weight: bold;
                margin: 0;
            }
            .chart-container {
                margin: 30px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            .chart-title {
                font-size: 1.5em;
                color: #333;
                margin-bottom: 15px;
                text-align: center;
            }
            .table-container {
                margin: 30px 0;
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background: #007bff;
                color: white;
                font-weight: 600;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>@numericalTools</h1>
                <p>数值模拟验证报告</p>
                <p>模拟ID: {simulation_id}</p>
                <p>生成时间: {generate_time}</p>
            </div>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>总轮数</h3>
                    <p class="value">{total_rounds:,}</p>
                </div>
                <div class="summary-card">
                    <h3>总投注金额</h3>
                    <p class="value">¥{total_bet_amount:,.2f}</p>
                </div>
                <div class="summary-card">
                    <h3>总派奖金额</h3>
                    <p class="value">¥{total_payout:,.2f}</p>
                </div>
                <div class="summary-card">
                    <h3>平均RTP</h3>
                    <p class="value">{average_rtp:.2f}%</p>
                </div>
                <div class="summary-card">
                    <h3>最终奖池</h3>
                    <p class="value">¥{final_jackpot:,.2f}</p>
                </div>
                <div class="summary-card">
                    <h3>总中奖人数</h3>
                    <p class="value">{total_winners:,}</p>
                </div>
                <div class="summary-card">
                    <h3>游戏名称</h3>
                    <p class="value">{game_name}</p>
                </div>
                <div class="summary-card">
                    <h3>模拟状态</h3>
                    <p class="value">{status}</p>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">RTP变化趋势</div>
                <div id="rtp-chart"></div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">奖级分布</div>
                <div id="prize-chart"></div>
            </div>
            
            <div class="table-container">
                <h3>奖级统计详情</h3>
                <table>
                    <thead>
                        <tr>
                            <th>奖级</th>
                            <th>中奖人数</th>
                            <th>总奖金</th>
                            <th>中奖概率</th>
                        </tr>
                    </thead>
                    <tbody>
                        {prize_table_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p>报告由 @numericalTools 自动生成</p>
                <p>© 2025 数值模拟验证工具</p>
            </div>
        </div>
        
        <script>
            // RTP趋势图
            var rtpData = [{
                x: {rtp_x_data},
                y: {rtp_y_data},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'RTP',
                line: {{color: '#007bff', width: 2}},
                marker: {{size: 4}}
            }];

            var rtpLayout = {{
                title: '',
                xaxis: {{title: '轮次', gridcolor: '#f0f0f0'}},
                yaxis: {{title: 'RTP (%)', gridcolor: '#f0f0f0'}},
                showlegend: false,
                margin: {{t: 20, b: 50, l: 60, r: 20}},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white'
            }};

            Plotly.newPlot('rtp-chart', rtpData, rtpLayout);

            // 奖级分布图
            var prizeData = [{{
                x: {prize_x_data},
                y: {prize_y_data},
                type: 'bar',
                marker: {{
                    color: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#fd79a8', '#fdcb6e'],
                    line: {{color: 'white', width: 1}}
                }}
            }}];

            var prizeLayout = {{
                title: '',
                xaxis: {{title: '奖级', gridcolor: '#f0f0f0'}},
                yaxis: {{title: '中奖人数', gridcolor: '#f0f0f0'}},
                showlegend: false,
                margin: {{t: 20, b: 50, l: 60, r: 20}},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white'
            }};

            Plotly.newPlot('prize-chart', prizeData, prizeLayout);
        </script>
    </body>
    </html>
    """

    # 准备图表数据
    rtp_x_data = list(range(1, len(round_results) + 1)) if round_results else [1]
    rtp_y_data = [r.rtp * 100 for r in round_results] if round_results else [0]

    prize_x_data = [f"{level}等奖" for level in sorted(prize_stats.keys())] if prize_stats else ["无数据"]
    prize_y_data = [prize_stats[level]['winners_count'] for level in sorted(prize_stats.keys())] if prize_stats else [0]

    # 生成奖级表格行
    prize_table_rows = ""
    if prize_stats:
        for level in sorted(prize_stats.keys()):
            stat = prize_stats[level]
            total_players = sum(r.total_players for r in round_results) if round_results else 1
            probability = (stat['winners_count'] / total_players * 100) if total_players > 0 else 0
            prize_table_rows += f"<tr><td>{level}等奖 - {stat['name']}</td><td>{stat['winners_count']:,}</td><td>¥{stat['total_amount']:,.2f}</td><td>{probability:.4f}%</td></tr>"
    else:
        prize_table_rows = "<tr><td colspan='4' style='text-align: center; color: #999;'>暂无奖级数据</td></tr>"

    # 获取汇总数据
    summary_data = simulation_data.get('summary', {})

    # 格式化模板
    formatted_html = html_template.format(
        simulation_id=simulation_id,
        generate_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_rounds=summary_data.get('total_rounds', 0),
        total_bet_amount=summary_data.get('total_bet_amount', 0),
        total_payout=summary_data.get('total_payout', 0),
        average_rtp=summary_data.get('average_rtp', 0) * 100,
        final_jackpot=summary_data.get('final_jackpot', 0),
        total_winners=total_winners,
        game_name=simulation_data.get('game_name', '未知游戏'),
        status=simulation_data.get('status', '未知'),
        prize_table_rows=prize_table_rows,
        rtp_x_data=json.dumps(rtp_x_data),
        rtp_y_data=json.dumps(rtp_y_data),
        prize_x_data=json.dumps(prize_x_data),
        prize_y_data=json.dumps(prize_y_data)
    )

    return formatted_html


async def generate_json_report(simulation_id: str) -> Dict[str, Any]:
    """生成JSON报告"""
    
    # 示例JSON报告数据
    report_data = {
        "simulation_id": simulation_id,
        "generate_time": datetime.now().isoformat(),
        "summary": {
            "total_rounds": 1000,
            "total_bet_amount": 2000000.0,
            "total_payout": 1800000.0,
            "average_rtp": 90.0,
            "jackpot_hits": 5
        },
        "prize_statistics": [
            {
                "level": 1,
                "name": "一等奖",
                "winners_count": 5,
                "total_amount": 1500000.0,
                "probability": 0.0001
            },
            {
                "level": 2,
                "name": "二等奖",
                "winners_count": 150,
                "total_amount": 7500000.0,
                "probability": 0.01
            }
        ],
        "charts": {
            "rtp_trend": {
                "type": "line",
                "data": {
                    "x": list(range(1, 101)),
                    "y": [90 + (i % 10 - 5) for i in range(100)]
                }
            }
        }
    }
    
    return report_data


async def generate_excel_report(simulation_id: str) -> FileResponse:
    """生成Excel报告"""
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_file.close()
    
    try:
        # 创建示例数据
        summary_data = {
            "指标": ["总轮数", "总投注金额", "总派奖金额", "平均RTP", "头奖中出次数"],
            "数值": [1000, 2000000.0, 1800000.0, "90.0%", 5]
        }
        
        prize_data = {
            "奖级": ["一等奖", "二等奖", "三等奖", "四等奖", "五等奖"],
            "中奖人数": [5, 150, 3000, 15000, 50000],
            "总奖金": [1500000.0, 7500000.0, 4500000.0, 900000.0, 1000000.0],
            "中奖概率": ["0.0001%", "0.01%", "0.2%", "1.0%", "3.3%"]
        }
        
        # 创建DataFrame
        summary_df = pd.DataFrame(summary_data)
        prize_df = pd.DataFrame(prize_data)
        
        # 写入Excel
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
            prize_df.to_excel(writer, sheet_name='奖级统计', index=False)
        
        # 返回文件
        return FileResponse(
            path=temp_file.name,
            filename=f"simulation_report_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        # 清理临时文件
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


@router.get("/charts/{simulation_id}")
async def get_simulation_charts(simulation_id: str):
    """获取模拟图表数据"""
    
    # 示例图表数据
    charts = [
        {
            "chart_type": "line",
            "title": "RTP变化趋势",
            "data": {
                "x": list(range(1, 101)),
                "y": [90 + (i % 10 - 5) for i in range(100)],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "RTP"
            },
            "config": {
                "layout": {
                    "xaxis": {"title": "轮次"},
                    "yaxis": {"title": "RTP (%)"}
                }
            }
        },
        {
            "chart_type": "bar",
            "title": "奖级分布",
            "data": {
                "x": ["一等奖", "二等奖", "三等奖", "四等奖", "五等奖"],
                "y": [5, 150, 3000, 15000, 50000],
                "type": "bar"
            },
            "config": {
                "layout": {
                    "xaxis": {"title": "奖级"},
                    "yaxis": {"title": "中奖人数"}
                }
            }
        }
    ]
    
    return {"charts": charts}


@router.get("/download/{simulation_id}")
async def download_report(simulation_id: str, format: str = "html"):
    """下载报告文件"""
    
    if format == "html":
        # 生成HTML文件
        html_content = await generate_html_report(simulation_id)

        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8')
        temp_file.write(html_content)
        temp_file.close()
        
        return FileResponse(
            path=temp_file.name,
            filename=f"simulation_report_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            media_type="text/html"
        )
    
    elif format == "excel":
        return await generate_excel_report(simulation_id)
    
    elif format == "json":
        json_data = await generate_json_report(simulation_id)
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8')
        json.dump(json_data, temp_file, ensure_ascii=False, indent=2)
        temp_file.close()
        
        return FileResponse(
            path=temp_file.name,
            filename=f"simulation_report_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            media_type="application/json"
        )
    
    else:
        raise HTTPException(status_code=400, detail="不支持的报告格式")
