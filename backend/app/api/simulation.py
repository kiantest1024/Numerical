"""
模拟相关API路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import asyncio
import json
from datetime import datetime

from ..models.game_config import GameConfiguration
from ..models.simulation_result import (
    SimulationRequest, SimulationResponse, SimulationResult
)
from ..core.simulation_engine import UniversalSimulationEngine

router = APIRouter()

# 存储运行中的模拟
running_simulations: Dict[str, UniversalSimulationEngine] = {}
simulation_results: Dict[str, SimulationResult] = {}


@router.post("/start", response_model=SimulationResponse)
async def start_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """启动新的模拟"""
    try:
        # 解析配置
        game_config = GameConfiguration(**{
            "game_rules": request.game_config,
            "simulation_config": request.simulation_config
        })
        
        # 创建模拟引擎
        engine = UniversalSimulationEngine(game_config)
        simulation_id = engine.simulation_id
        
        # 存储引擎实例
        running_simulations[simulation_id] = engine
        
        # 在后台运行模拟
        background_tasks.add_task(run_simulation_task, simulation_id, engine)
        
        return SimulationResponse(
            simulation_id=simulation_id,
            status="started",
            message="模拟已启动"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"启动模拟失败: {str(e)}")


async def run_simulation_task(simulation_id: str, engine: UniversalSimulationEngine):
    """后台运行模拟任务"""
    import concurrent.futures
    import time

    def run_sync_simulation():
        """在线程池中运行同步模拟"""
        try:
            engine.start_time = datetime.now()
            engine.is_running = True
            engine.should_stop = False

            for round_num in range(1, min(engine.sim_config.rounds, 100) + 1):
                if engine.should_stop:
                    break

                engine.current_round = round_num
                round_result = engine.simulate_round(round_num)
                engine.round_results.append(round_result)

                if round_num % 10 == 0:
                    time.sleep(0.1)

            # 生成结果
            end_time = datetime.now()
            duration = (end_time - engine.start_time).total_seconds()

            result = SimulationResult(
                simulation_id=simulation_id,
                game_config_id=engine.game_config.id,
                start_time=engine.start_time,
                end_time=end_time,
                duration=duration,
                status="completed" if not engine.should_stop else "stopped",
                game_name=engine.game_rules.name,
                simulation_rounds=len(engine.round_results),
                round_results=engine.round_results,
                summary=engine._generate_summary() if engine.round_results else None
            )

            return result

        except Exception as e:
            return SimulationResult(
                simulation_id=simulation_id,
                start_time=datetime.now(),
                end_time=datetime.now(),
                status="error",
                game_name="Unknown",
                simulation_rounds=0,
                error_message=str(e)
            )
        finally:
            engine.is_running = False

    try:
        # 在线程池中运行模拟
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            result = await loop.run_in_executor(executor, run_sync_simulation)

        simulation_results[simulation_id] = result

        # 清理运行中的模拟
        if simulation_id in running_simulations:
            del running_simulations[simulation_id]

    except Exception as e:
        # 创建错误结果
        error_result = SimulationResult(
            simulation_id=simulation_id,
            start_time=datetime.now(),
            end_time=datetime.now(),
            status="error",
            game_name="Unknown",
            simulation_rounds=0,
            error_message=str(e)
        )
        simulation_results[simulation_id] = error_result

        # 清理运行中的模拟
        if simulation_id in running_simulations:
            del running_simulations[simulation_id]


@router.get("/status/{simulation_id}")
async def get_simulation_status(simulation_id: str):
    """获取模拟状态"""
    # 检查是否在运行中
    if simulation_id in running_simulations:
        engine = running_simulations[simulation_id]
        progress_percentage = (engine.current_round / engine.sim_config.rounds) * 100 if engine.sim_config.rounds > 0 else 0
        elapsed_time = (datetime.now() - engine.start_time).total_seconds() if engine.start_time else 0
        
        return {
            "simulation_id": simulation_id,
            "status": "running",
            "progress": {
                "current_round": engine.current_round,
                "total_rounds": engine.sim_config.rounds,
                "progress_percentage": progress_percentage,
                "elapsed_time": elapsed_time
            }
        }
    
    # 检查是否已完成
    if simulation_id in simulation_results:
        result = simulation_results[simulation_id]
        return {
            "simulation_id": simulation_id,
            "status": result.status,
            "completed": True,
            "duration": result.duration,
            "error_message": result.error_message
        }
    
    # 未找到模拟
    raise HTTPException(status_code=404, detail="模拟未找到")


@router.get("/result/{simulation_id}", response_model=SimulationResult)
async def get_simulation_result(simulation_id: str):
    """获取模拟结果"""
    if simulation_id not in simulation_results:
        raise HTTPException(status_code=404, detail="模拟结果未找到")
    
    return simulation_results[simulation_id]


@router.post("/stop/{simulation_id}")
async def stop_simulation(simulation_id: str):
    """停止运行中的模拟"""
    if simulation_id not in running_simulations:
        raise HTTPException(status_code=404, detail="运行中的模拟未找到")
    
    engine = running_simulations[simulation_id]
    engine.stop_simulation()
    
    return {
        "simulation_id": simulation_id,
        "status": "stopping",
        "message": "模拟停止请求已发送"
    }


@router.get("/progress/{simulation_id}")
async def get_simulation_progress(simulation_id: str):
    """获取模拟进度（用于实时更新）"""
    if simulation_id not in running_simulations:
        if simulation_id in simulation_results:
            result = simulation_results[simulation_id]
            return {
                "simulation_id": simulation_id,
                "status": result.status,
                "completed": True,
                "progress_percentage": 100.0 if result.status == "completed" else 0.0,
                "final_summary": result.summary.model_dump() if result.summary else None
            }
        raise HTTPException(status_code=404, detail="模拟未找到")

    engine = running_simulations[simulation_id]
    progress_percentage = (engine.current_round / engine.sim_config.rounds) * 100 if engine.sim_config.rounds > 0 else 0
    elapsed_time = (datetime.now() - engine.start_time).total_seconds() if engine.start_time else 0

    # 估算剩余时间
    estimated_remaining = None
    if engine.current_round > 0 and progress_percentage > 0:
        time_per_round = elapsed_time / engine.current_round
        remaining_rounds = engine.sim_config.rounds - engine.current_round
        estimated_remaining = time_per_round * remaining_rounds

    # 计算实时统计数据
    real_time_stats = None
    if engine.round_results:
        # 计算当前的汇总统计
        completed_rounds = len(engine.round_results)
        total_bet_amount = sum(r.total_bet_amount for r in engine.round_results)
        total_payout = sum(r.total_payout for r in engine.round_results)
        current_rtp = (total_payout / total_bet_amount) if total_bet_amount > 0 else 0.0

        # 计算中奖和未中奖人数统计
        total_players = sum(r.players_count for r in engine.round_results)
        total_winners = sum(r.winners_count or 0 for r in engine.round_results)
        total_non_winners = sum(r.non_winners_count or 0 for r in engine.round_results)
        winning_rate = (total_winners / total_players) if total_players > 0 else 0.0

        # 计算各奖级统计
        prize_stats = {}
        for prize_level in engine.game_rules.prize_levels:
            level = prize_level.level
            total_winners = sum(
                sum(stat.winners_count for stat in r.prize_stats if stat.level == level)
                for r in engine.round_results
            )
            total_amount = sum(
                sum(stat.total_amount for stat in r.prize_stats if stat.level == level)
                for r in engine.round_results
            )
            prize_stats[level] = {
                "name": prize_level.name,
                "winners_count": total_winners,
                "total_amount": total_amount
            }

        # 最近10轮的RTP趋势
        recent_rtps = [r.rtp for r in engine.round_results[-10:]]

        # 获取奖池阶段信息
        jackpot_phase_info = {}
        if engine.game_rules.jackpot.enabled:
            return_phase_completed = engine.total_returned_amount >= engine.initial_jackpot_amount
            if return_phase_completed:
                current_contribution_rate = engine.game_rules.jackpot.post_return_contribution_rate
            else:
                current_contribution_rate = engine.game_rules.jackpot.contribution_rate

            jackpot_phase_info = {
                "return_phase_completed": return_phase_completed,
                "current_contribution_rate": current_contribution_rate,
                "total_returned_amount": engine.total_returned_amount,
                "initial_jackpot_amount": engine.initial_jackpot_amount,
                "phase_1_rate": engine.game_rules.jackpot.contribution_rate,
                "phase_2_rate": engine.game_rules.jackpot.post_return_contribution_rate
            }

        real_time_stats = {
            "completed_rounds": completed_rounds,
            "total_bet_amount": total_bet_amount,
            "total_payout": total_payout,
            "current_rtp": current_rtp,
            "prize_stats": prize_stats,
            "recent_rtps": recent_rtps,
            "current_jackpot": engine.jackpot_pool,
            "total_sales_amount": engine.total_sales_amount,  # 累计销售金额
            "jackpot_hits_count": engine.jackpot_hits_count,  # 头奖中出次数
            "total_players": total_players,  # 总玩家数
            "total_winners": total_winners,  # 总中奖人数
            "total_non_winners": total_non_winners,  # 总未中奖人数
            "winning_rate": winning_rate,  # 中奖率
            **jackpot_phase_info  # 合并奖池阶段信息
        }

    return {
        "simulation_id": simulation_id,
        "status": "running",
        "current_round": engine.current_round,
        "total_rounds": engine.sim_config.rounds,
        "progress_percentage": progress_percentage,
        "elapsed_time": elapsed_time,
        "estimated_remaining": estimated_remaining,
        "real_time_stats": real_time_stats
    }


@router.get("/realtime-data/{simulation_id}")
async def get_realtime_simulation_data(simulation_id: str):
    """获取实时模拟数据（用于图表展示）"""
    if simulation_id not in running_simulations:
        if simulation_id in simulation_results:
            result = simulation_results[simulation_id]
            if result.summary:
                return {
                    "simulation_id": simulation_id,
                    "status": "completed",
                    "chart_data": {
                        "rtp_trend": [r.rtp for r in result.round_results] if result.round_results else [],
                        "jackpot_trend": [r.jackpot_amount for r in result.round_results] if result.round_results else [],
                        "prize_distribution": [
                            {"level": stat.level, "name": stat.name, "count": stat.winners_count, "amount": stat.total_amount}
                            for stat in result.summary.prize_summary
                        ] if result.summary.prize_summary else [],
                        "summary": {
                            "total_rounds": result.summary.total_rounds,
                            "average_rtp": result.summary.average_rtp,
                            "total_bet_amount": result.summary.total_bet_amount,
                            "total_payout": result.summary.total_payout,
                            "final_jackpot": result.summary.final_jackpot
                        }
                    }
                }
        raise HTTPException(status_code=404, detail="模拟未找到")

    engine = running_simulations[simulation_id]

    # 构建实时图表数据
    chart_data = {
        "rtp_trend": [r.rtp for r in engine.round_results],
        "jackpot_trend": [r.jackpot_amount for r in engine.round_results],
        "prize_distribution": [],
        "round_labels": list(range(1, len(engine.round_results) + 1))
    }

    # 计算奖级分布
    if engine.round_results:
        for prize_level in engine.game_rules.prize_levels:
            level = prize_level.level
            total_winners = sum(
                sum(stat.winners_count for stat in r.prize_stats if stat.level == level)
                for r in engine.round_results
            )
            total_amount = sum(
                sum(stat.total_amount for stat in r.prize_stats if stat.level == level)
                for r in engine.round_results
            )
            if total_winners > 0:  # 只显示有中奖的奖级
                chart_data["prize_distribution"].append({
                    "level": level,
                    "name": prize_level.name,
                    "count": total_winners,
                    "amount": total_amount
                })

    return {
        "simulation_id": simulation_id,
        "status": "running",
        "current_round": engine.current_round,
        "chart_data": chart_data
    }


@router.get("/stream/{simulation_id}")
async def stream_simulation_progress(simulation_id: str):
    """流式获取模拟进度（Server-Sent Events）"""
    
    async def generate_progress():
        """生成进度数据流"""
        while simulation_id in running_simulations:
            engine = running_simulations[simulation_id]
            progress_percentage = (engine.current_round / engine.sim_config.rounds) * 100 if engine.sim_config.rounds > 0 else 0
            elapsed_time = (datetime.now() - engine.start_time).total_seconds() if engine.start_time else 0
            
            progress_data = {
                "simulation_id": simulation_id,
                "status": "running",
                "current_round": engine.current_round,
                "total_rounds": engine.sim_config.rounds,
                "progress_percentage": progress_percentage,
                "elapsed_time": elapsed_time
            }
            
            yield f"data: {json.dumps(progress_data)}\n\n"
            await asyncio.sleep(1)  # 每秒更新一次
        
        # 模拟完成后发送最终状态
        if simulation_id in simulation_results:
            result = simulation_results[simulation_id]
            final_data = {
                "simulation_id": simulation_id,
                "status": result.status,
                "completed": True,
                "progress_percentage": 100.0 if result.status == "completed" else 0.0,
                "duration": result.duration
            }
            yield f"data: {json.dumps(final_data)}\n\n"
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.get("/list")
async def list_simulations():
    """列出所有模拟"""
    simulations = []
    
    # 运行中的模拟
    for sim_id, engine in running_simulations.items():
        simulations.append({
            "simulation_id": sim_id,
            "status": "running",
            "game_name": engine.game_rules.name,
            "start_time": engine.start_time.isoformat() if engine.start_time else None,
            "current_round": engine.current_round,
            "total_rounds": engine.sim_config.rounds
        })
    
    # 已完成的模拟
    for sim_id, result in simulation_results.items():
        simulations.append({
            "simulation_id": sim_id,
            "status": result.status,
            "game_name": result.game_name,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "duration": result.duration,
            "total_rounds": result.simulation_rounds
        })
    
    return {"simulations": simulations}


@router.delete("/result/{simulation_id}")
async def delete_simulation_result(simulation_id: str):
    """删除模拟结果"""
    if simulation_id in simulation_results:
        del simulation_results[simulation_id]
        return {"message": "模拟结果已删除"}
    
    raise HTTPException(status_code=404, detail="模拟结果未找到")


@router.post("/validate-config")
async def validate_game_config(config: Dict[str, Any]):
    """验证游戏配置"""
    try:
        # 尝试解析配置
        game_config = GameConfiguration(**config)
        return {
            "valid": True,
            "message": "配置验证通过",
            "config": game_config.model_dump()
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"配置验证失败: {str(e)}",
            "errors": [str(e)]
        }
