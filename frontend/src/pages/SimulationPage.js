import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Button,
  Progress,
  Alert,
  Space,
  Statistic,
  Row,
  Col,
  Typography,
  message,
  Select,
  Table,
  Divider,
  Tag
} from 'antd';
import {
  PlayCircleOutlined,
  StopOutlined,
  ReloadOutlined,
  TrophyOutlined,
  DollarOutlined,
  PercentageOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;

const SimulationPage = () => {
  const [configs, setConfigs] = useState([]);
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [progress, setProgress] = useState(null);
  const [realtimeData, setRealtimeData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchConfigs = async () => {
    try {
      const response = await axios.get('/api/v1/config/list');
      setConfigs(response.data.configs);
    } catch (error) {
      message.error('获取配置列表失败');
    }
  };

  const fetchProgress = useCallback(async () => {
    if (!simulation) return;

    try {
      const response = await axios.get(`/api/v1/simulation/progress/${simulation.simulation_id}`);
      setProgress(response.data);

      if (response.data.completed) {
        setSimulation(prev => ({ ...prev, status: 'completed' }));
      }
    } catch (error) {
      console.error('获取进度失败:', error);
    }
  }, [simulation]);

  const fetchRealtimeData = useCallback(async () => {
    if (!simulation) return;

    try {
      const response = await axios.get(`/api/v1/simulation/realtime-data/${simulation.simulation_id}`);
      setRealtimeData(response.data);
    } catch (error) {
      console.error('获取实时数据失败:', error);
    }
  }, [simulation]);

  useEffect(() => {
    fetchConfigs();
  }, []);

  useEffect(() => {
    let progressInterval;
    let dataInterval;

    if (simulation && (simulation.status === 'running' || simulation.status === 'started')) {
      // 每秒更新进度
      progressInterval = setInterval(fetchProgress, 1000);
      // 每2秒更新实时数据
      dataInterval = setInterval(fetchRealtimeData, 2000);
    }

    return () => {
      if (progressInterval) clearInterval(progressInterval);
      if (dataInterval) clearInterval(dataInterval);
    };
  }, [simulation, fetchProgress, fetchRealtimeData]);

  const handleStartSimulation = async () => {
    if (!selectedConfig) {
      message.error('请先选择配置');
      return;
    }

    setLoading(true);
    try {
      // 加载配置详情
      const configResponse = await axios.get(`/api/v1/config/load/${selectedConfig}`);
      const config = configResponse.data.config;

      // 启动模拟
      const simulationResponse = await axios.post('/api/v1/simulation/start', {
        game_config: config.game_rules,
        simulation_config: config.simulation_config
      });

      setSimulation(simulationResponse.data);
      setProgress({ progress_percentage: 0, current_round: 0 });
      message.success('模拟已启动');
    } catch (error) {
      message.error('启动模拟失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleStopSimulation = async () => {
    if (!simulation) return;

    try {
      await axios.post(`/api/v1/simulation/stop/${simulation.simulation_id}`);
      message.success('停止请求已发送');
    } catch (error) {
      message.error('停止模拟失败');
    }
  };

  const handleViewResults = () => {
    if (simulation && simulation.simulation_id) {
      // 这里可以跳转到结果页面
      window.location.href = `/results?simulation_id=${simulation.simulation_id}`;
    }
  };

  const formatTime = (seconds) => {
    if (!seconds) return '0秒';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}小时${minutes}分钟${secs}秒`;
    } else if (minutes > 0) {
      return `${minutes}分钟${secs}秒`;
    } else {
      return `${secs}秒`;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'started':
      case 'running': return '#52c41a';
      case 'completed': return '#1890ff';
      case 'error': return '#ff4d4f';
      case 'stopped': return '#faad14';
      default: return '#d9d9d9';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'started': return '启动中';
      case 'running': return '运行中';
      case 'completed': return '已完成';
      case 'error': return '错误';
      case 'stopped': return '已停止';
      default: return '未知';
    }
  };

  return (
    <div>
      <div className="page-header">
        <Title level={1}>运行模拟</Title>
        <Text>选择配置并启动数值模拟验证</Text>
      </div>

      {/* 配置选择 */}
      <Card title="选择配置" style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Select
              style={{ width: '100%' }}
              placeholder="选择已保存的配置"
              value={selectedConfig}
              onChange={setSelectedConfig}
              showSearch
              optionFilterProp="children"
            >
              {configs.map(config => (
                <Option key={config.name} value={config.name}>
                  {config.display_name} ({config.game_type})
                </Option>
              ))}
            </Select>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchConfigs}
              >
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleStartSimulation}
                loading={loading}
                disabled={!selectedConfig || (simulation && (simulation.status === 'running' || simulation.status === 'started'))}
              >
                启动模拟
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 模拟状态 */}
      {simulation && (
        <Card title="模拟状态" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="模拟ID"
                value={simulation.simulation_id?.slice(0, 8) + '...'}
                prefix={
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: getStatusColor(simulation.status),
                      display: 'inline-block',
                      marginRight: 8
                    }}
                  />
                }
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="状态"
                value={getStatusText(simulation.status)}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="当前轮次"
                value={progress?.current_round || 0}
                suffix={`/ ${progress?.total_rounds || 0}`}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="已用时间"
                value={formatTime(progress?.elapsed_time)}
              />
            </Col>
          </Row>

          {progress && (
            <div style={{ marginTop: 16 }}>
              <Progress
                percent={Math.round(progress.progress_percentage || 0)}
                status={simulation.status === 'error' ? 'exception' : 'active'}
                strokeColor={getStatusColor(simulation.status)}
              />
              
              {progress.estimated_remaining && (
                <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
                  预计剩余时间: {formatTime(progress.estimated_remaining)}
                </Text>
              )}
            </div>
          )}

          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Space>
              {(simulation.status === 'running' || simulation.status === 'started') && (
                <Button
                  danger
                  icon={<StopOutlined />}
                  onClick={handleStopSimulation}
                >
                  停止模拟
                </Button>
              )}
              
              {(simulation.status === 'completed' || simulation.status === 'stopped') && (
                <Button
                  type="primary"
                  onClick={handleViewResults}
                >
                  查看结果
                </Button>
              )}
            </Space>
          </div>
        </Card>
      )}

      {/* 实时数据统计 */}
      {simulation && progress && progress.real_time_stats && (
        <Card title="实时数据统计" style={{ marginBottom: 24 }}>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Statistic
                title="当前RTP"
                value={progress.real_time_stats.current_rtp}
                precision={4}
                prefix={<PercentageOutlined />}
                valueStyle={{ color: progress.real_time_stats.current_rtp > 0.8 ? '#3f8600' : '#cf1322' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="奖池余额"
                value={progress.real_time_stats.current_jackpot}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="总投注金额"
                value={progress.real_time_stats.total_bet_amount}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="总派奖金额"
                value={progress.real_time_stats.total_payout}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
              />
            </Col>
          </Row>

          <Divider>奖级统计</Divider>

          <Table
            dataSource={Object.entries(progress.real_time_stats.prize_stats || {}).map(([level, stats]) => ({
              key: level,
              level: level,
              name: stats.name,
              winners: stats.winners_count,
              amount: stats.total_amount
            }))}
            columns={[
              {
                title: '奖级',
                dataIndex: 'name',
                key: 'name',
                render: (text, record) => (
                  <Tag color={record.level === '1' ? 'gold' : record.level === '2' ? 'silver' : 'blue'}>
                    <TrophyOutlined /> {text}
                  </Tag>
                )
              },
              {
                title: '中奖人数',
                dataIndex: 'winners',
                key: 'winners',
                render: (value) => value.toLocaleString()
              },
              {
                title: '总奖金',
                dataIndex: 'amount',
                key: 'amount',
                render: (value) => `¥${value.toLocaleString()}`
              }
            ]}
            pagination={false}
            size="small"
          />

          {progress.real_time_stats.recent_rtps && progress.real_time_stats.recent_rtps.length > 0 && (
            <>
              <Divider>RTP趋势 (最近10轮)</Divider>
              <div style={{ textAlign: 'center' }}>
                <Space wrap>
                  {progress.real_time_stats.recent_rtps.map((rtp, index) => (
                    <Tag
                      key={index}
                      color={rtp > 0.8 ? 'green' : rtp > 0.7 ? 'orange' : 'red'}
                    >
                      {rtp.toFixed(4)}
                    </Tag>
                  ))}
                </Space>
              </div>
            </>
          )}
        </Card>
      )}

      {/* 图表数据展示 */}
      {simulation && realtimeData && realtimeData.chart_data && (
        <Card title="数据图表" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Card size="small" title="RTP趋势">
                {realtimeData.chart_data.rtp_trend && realtimeData.chart_data.rtp_trend.length > 0 ? (
                  <div style={{ textAlign: 'center' }}>
                    <p>数据点数: {realtimeData.chart_data.rtp_trend.length}</p>
                    <p>最新RTP: {realtimeData.chart_data.rtp_trend[realtimeData.chart_data.rtp_trend.length - 1]?.toFixed(4)}</p>
                    <p>平均RTP: {(realtimeData.chart_data.rtp_trend.reduce((a, b) => a + b, 0) / realtimeData.chart_data.rtp_trend.length).toFixed(4)}</p>
                  </div>
                ) : (
                  <p style={{ textAlign: 'center', color: '#999' }}>暂无数据</p>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="奖级分布">
                {realtimeData.chart_data.prize_distribution && realtimeData.chart_data.prize_distribution.length > 0 ? (
                  <div>
                    {realtimeData.chart_data.prize_distribution.map((prize, index) => (
                      <div key={index} style={{ marginBottom: 8 }}>
                        <Row justify="space-between">
                          <Col>
                            <Tag color={prize.level === 1 ? 'gold' : prize.level === 2 ? 'silver' : 'blue'}>
                              {prize.name}
                            </Tag>
                          </Col>
                          <Col>
                            <Text>{prize.count}人 / ¥{prize.amount.toLocaleString()}</Text>
                          </Col>
                        </Row>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ textAlign: 'center', color: '#999' }}>暂无中奖数据</p>
                )}
              </Card>
            </Col>
          </Row>
        </Card>
      )}

      {/* 提示信息 */}
      {!simulation && (
        <Alert
          message="使用提示"
          description={
            <div>
              <p>1. 首先在"游戏配置"页面创建或选择一个配置</p>
              <p>2. 在此页面选择配置并启动模拟</p>
              <p>3. 模拟过程中可以实时查看进度</p>
              <p>4. 模拟完成后可以查看详细结果</p>
            </div>
          }
          type="info"
          showIcon
        />
      )}

      {simulation?.status === 'error' && (
        <Alert
          message="模拟错误"
          description="模拟过程中发生错误，请检查配置或重新启动"
          type="error"
          showIcon
          style={{ marginTop: 16 }}
        />
      )}
    </div>
  );
};

export default SimulationPage;
