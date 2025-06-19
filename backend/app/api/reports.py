"""
报告生成API路由
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse
from typing import Dict, Any, Optional
import json
import os
import tempfile
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from ..models.simulation_result import SimulationResult, ChartData
from ..core.config import settings

router = APIRouter()

# 报告存储路径
REPORTS_DIR = settings.REPORTS_DIR
os.makedirs(REPORTS_DIR, exist_ok=True)


@router.get("/generate/{simulation_id}")
async def generate_report(simulation_id: str, format: str = "html"):
    """生成模拟报告"""
    # 这里需要从模拟结果存储中获取数据
    # 为了演示，我们先返回一个示例
    
    if format not in ["html", "json", "excel"]:
        raise HTTPException(status_code=400, detail="不支持的报告格式")
    
    try:
        # 获取模拟结果（这里需要实际的数据获取逻辑）
        # result = get_simulation_result(simulation_id)
        
        if format == "html":
            return await generate_html_report(simulation_id)
        elif format == "json":
            return await generate_json_report(simulation_id)
        elif format == "excel":
            return await generate_excel_report(simulation_id)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")


async def generate_html_report(simulation_id: str) -> HTMLResponse:
    """生成HTML报告"""
    
    # 示例HTML报告模板
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
                    <p class="value">1,000</p>
                </div>
                <div class="summary-card">
                    <h3>总投注金额</h3>
                    <p class="value">¥2,000,000</p>
                </div>
                <div class="summary-card">
                    <h3>总派奖金额</h3>
                    <p class="value">¥1,800,000</p>
                </div>
                <div class="summary-card">
                    <h3>平均RTP</h3>
                    <p class="value">90.0%</p>
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
                        <tr>
                            <td>一等奖</td>
                            <td>5</td>
                            <td>¥1,500,000</td>
                            <td>0.0001%</td>
                        </tr>
                        <tr>
                            <td>二等奖</td>
                            <td>150</td>
                            <td>¥7,500,000</td>
                            <td>0.01%</td>
                        </tr>
                        <tr>
                            <td>三等奖</td>
                            <td>3,000</td>
                            <td>¥4,500,000</td>
                            <td>0.2%</td>
                        </tr>
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
                x: Array.from({length: 100}, (_, i) => i + 1),
                y: Array.from({length: 100}, () => Math.random() * 20 + 80),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'RTP',
                line: {color: '#007bff'}
            }];
            
            var rtpLayout = {
                title: '',
                xaxis: {title: '轮次'},
                yaxis: {title: 'RTP (%)'},
                showlegend: false,
                margin: {t: 20}
            };
            
            Plotly.newPlot('rtp-chart', rtpData, rtpLayout);
            
            // 奖级分布图
            var prizeData = [{
                x: ['一等奖', '二等奖', '三等奖', '四等奖', '五等奖'],
                y: [5, 150, 3000, 15000, 50000],
                type: 'bar',
                marker: {color: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']}
            }];
            
            var prizeLayout = {
                title: '',
                xaxis: {title: '奖级'},
                yaxis: {title: '中奖人数'},
                showlegend: false,
                margin: {t: 20}
            };
            
            Plotly.newPlot('prize-chart', prizeData, prizeLayout);
        </script>
    </body>
    </html>
    """.format(
        simulation_id=simulation_id,
        generate_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    return HTMLResponse(content=html_template)


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
        temp_file.write(html_content.body.decode('utf-8'))
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
