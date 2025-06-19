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
  Tag,
  Tabs,
  Form,
  Input,
  InputNumber,
  Switch,
  Collapse,
  Divider,
  Table
} from 'antd';
import {
  PlayCircleOutlined,
  StopOutlined,
  ReloadOutlined,
  TrophyOutlined,
  DollarOutlined,
  PercentageOutlined,
  UserOutlined,
  FrownOutlined,
  SaveOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { Panel } = Collapse;

const SimulationPage = () => {
  const [configs, setConfigs] = useState([]);
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [progress, setProgress] = useState(null);
  const [realtimeData, setRealtimeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('existing'); // 'existing' 或 'new'
  const [configForm] = Form.useForm();

  const fetchConfigs = async () => {
    try {
      const response = await axios.get('/api/v1/config/list');
      setConfigs(response.data.configs);
    } catch (error) {
      message.error('获取配置列表失败');
    }
  };



  const fetchRealtimeData = useCallback(async () => {
    if (!simulation) return;

    try {
      const response = await axios.get(`/api/v1/simulation/realtime-data/${simulation.simulation_id}`);
      setRealtimeData(response.data);
    } catch (error) {
      console.error('获取实时数据失败:', error);
    }
  }, [simulation]);

  const fetchProgress = useCallback(async () => {
    if (!simulation) return;

    try {
      const response = await axios.get(`/api/v1/simulation/progress/${simulation.simulation_id}`);
      setProgress(response.data);

      if (response.data.completed) {
        setSimulation(prev => ({ ...prev, status: 'completed' }));
        // 模拟完成时，立即获取最终的实时数据
        fetchRealtimeData();
      }
    } catch (error) {
      console.error('获取进度失败:', error);
    }
  }, [simulation, fetchRealtimeData]);

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
    } else if (simulation && simulation.status === 'completed') {
      // 模拟完成后，获取一次最终的实时数据
      fetchRealtimeData();
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

  const handleStartNewSimulation = async () => {
    try {
      const values = await configForm.validateFields();

      setLoading(true);

      // 构建配置对象
      const gameConfig = {
        game_type: "lottery",
        name: values.game_name || "临时配置",
        description: values.description || "运行模拟时创建的临时配置",
        number_range: [1, values.number_range_max || 49],
        selection_count: values.selection_count || 6,
        ticket_price: values.ticket_price || 10.0,
        prize_levels: values.prize_levels || [],
        jackpot: {
          enabled: values.jackpot_enabled || false,
          initial_amount: values.initial_jackpot || 1000.0,
          contribution_rate: (values.contribution_rate || 30) / 100,
          post_return_contribution_rate: (values.post_return_contribution_rate || 50) / 100,
          return_rate: (values.return_rate || 20) / 100,
          jackpot_fixed_prize: values.jackpot_fixed_prize || null,
          min_jackpot: values.min_jackpot || 500.0
        }
      };

      const simulationConfig = {
        rounds: values.rounds || 100,
        players_range: [values.min_players || 50, values.max_players || 100],
        bets_range: [values.min_bets || 1, values.max_bets || 3],
        seed: values.seed || null
      };

      // 启动模拟
      const simulationResponse = await axios.post('/api/v1/simulation/start', {
        game_config: gameConfig,
        simulation_config: simulationConfig
      });

      setSimulation(simulationResponse.data);
      setProgress({ progress_percentage: 0, current_round: 0 });
      message.success('模拟已启动');
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查配置表单中的错误');
      } else {
        message.error('启动模拟失败: ' + (error.response?.data?.detail || error.message));
      }
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
      <Card title="模拟配置" style={{ marginBottom: 24 }}>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="使用已保存配置" key="existing">
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
          </TabPane>

          <TabPane tab="创建新配置并运行" key="new">
            <Form
              form={configForm}
              layout="vertical"
              initialValues={{
                number_range_max: 49,
                selection_count: 6,
                ticket_price: 10.0,
                rounds: 100,
                min_players: 50,
                max_players: 100,
                min_bets: 1,
                max_bets: 3,
                jackpot_enabled: true,
                initial_jackpot: 1000.0,
                contribution_rate: 30,
                post_return_contribution_rate: 50,
                return_rate: 20,
                min_jackpot: 500.0
              }}
            >
              <Collapse defaultActiveKey={['basic', 'simulation']}>
                <Panel header="基础游戏配置" key="basic">
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        label="游戏名称"
                        name="game_name"
                        rules={[{ required: true, message: '请输入游戏名称' }]}
                      >
                        <Input placeholder="输入游戏名称" />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        label="描述"
                        name="description"
                      >
                        <Input placeholder="输入游戏描述" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item
                        label="数字范围上限"
                        name="number_range_max"
                        rules={[{ required: true, message: '请输入数字范围上限' }]}
                      >
                        <InputNumber min={5} max={100} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="选择数量"
                        name="selection_count"
                        rules={[{ required: true, message: '请输入选择数量' }]}
                      >
                        <InputNumber min={1} max={20} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="票价 (¥)"
                        name="ticket_price"
                        rules={[{ required: true, message: '请输入票价' }]}
                      >
                        <InputNumber min={1} step={0.1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>
                </Panel>

                <Panel header="模拟配置" key="simulation">
                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item
                        label="模拟轮数"
                        name="rounds"
                        rules={[{ required: true, message: '请输入模拟轮数' }]}
                      >
                        <InputNumber min={1} max={10000} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="最小玩家数"
                        name="min_players"
                        rules={[{ required: true, message: '请输入最小玩家数' }]}
                      >
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="最大玩家数"
                        name="max_players"
                        rules={[{ required: true, message: '请输入最大玩家数' }]}
                      >
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item
                        label="最小投注次数"
                        name="min_bets"
                        rules={[{ required: true, message: '请输入最小投注次数' }]}
                      >
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="最大投注次数"
                        name="max_bets"
                        rules={[{ required: true, message: '请输入最大投注次数' }]}
                      >
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="随机种子"
                        name="seed"
                      >
                        <InputNumber style={{ width: '100%' }} placeholder="留空为随机" />
                      </Form.Item>
                    </Col>
                  </Row>
                </Panel>

                <Panel header="奖池配置" key="jackpot">
                  <Form.Item
                    label="启用奖池"
                    name="jackpot_enabled"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>

                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item
                        label="初始奖池金额 (¥)"
                        name="initial_jackpot"
                      >
                        <InputNumber min={0} step={100} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="第一阶段奖池注入比例 (%)"
                        name="contribution_rate"
                      >
                        <InputNumber min={0} max={100} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="第二阶段奖池注入比例 (%)"
                        name="post_return_contribution_rate"
                      >
                        <InputNumber min={0} max={100} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item
                        label="销售方返还比例 (%)"
                        name="return_rate"
                      >
                        <InputNumber min={0} max={100} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="头奖固定奖金 (¥)"
                        name="jackpot_fixed_prize"
                      >
                        <InputNumber min={0} style={{ width: '100%' }} placeholder="留空为奖池金额" />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        label="最小奖池金额 (¥)"
                        name="min_jackpot"
                      >
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>
                </Panel>
              </Collapse>

              <div style={{ marginTop: 16, textAlign: 'center' }}>
                <Space>
                  <Button
                    icon={<SaveOutlined />}
                    onClick={() => {
                      // 可以添加保存配置的功能
                      message.info('保存配置功能待实现');
                    }}
                  >
                    保存配置
                  </Button>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={handleStartNewSimulation}
                    loading={loading}
                    disabled={simulation && (simulation.status === 'running' || simulation.status === 'started')}
                  >
                    启动模拟
                  </Button>
                </Space>
              </div>
            </Form>
          </TabPane>
        </Tabs>
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
                value={progress.real_time_stats.current_rtp * 100}
                precision={2}
                suffix="%"
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

          {/* 玩家统计 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Statistic
                title="总玩家数"
                value={progress.real_time_stats.total_players || 0}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="中奖人数"
                value={progress.real_time_stats.total_winners || 0}
                prefix={<TrophyOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="未中奖人数"
                value={progress.real_time_stats.total_non_winners || 0}
                prefix={<FrownOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="中奖率"
                value={(progress.real_time_stats.winning_rate || 0) * 100}
                precision={2}
                suffix="%"
                prefix={<PercentageOutlined />}
                valueStyle={{ color: (progress.real_time_stats.winning_rate || 0) > 0.3 ? '#52c41a' : '#ff4d4f' }}
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
                      {(rtp * 100).toFixed(2)}%
                    </Tag>
                  ))}
                </Space>
              </div>
            </>
          )}

          {/* 新增：综合RTP统计分析 */}
          <Divider>综合RTP统计分析</Divider>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Statistic
                title="当前RTP"
                value={((progress.real_time_stats.current_rtp || 0) * 100).toFixed(2)}
                suffix="%"
                prefix={<PercentageOutlined />}
                valueStyle={{
                  color: (() => {
                    const rtp = progress.real_time_stats.current_rtp || 0;
                    return rtp > 0.85 ? '#52c41a' : rtp > 0.75 ? '#fa8c16' : '#ff4d4f';
                  })()
                }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="目标RTP"
                value="85.00"
                suffix="%"
                prefix={<PercentageOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="RTP偏差"
                value={(() => {
                  const currentRtp = (progress.real_time_stats.current_rtp || 0) * 100;
                  const targetRtp = 85.0;
                  return (currentRtp - targetRtp).toFixed(2);
                })()}
                suffix="%"
                prefix={(() => {
                  const currentRtp = (progress.real_time_stats.current_rtp || 0) * 100;
                  const targetRtp = 85.0;
                  return currentRtp >= targetRtp ? '+' : '';
                })()}
                valueStyle={{
                  color: (() => {
                    const currentRtp = (progress.real_time_stats.current_rtp || 0) * 100;
                    const targetRtp = 85.0;
                    const deviation = Math.abs(currentRtp - targetRtp);
                    return deviation <= 2 ? '#52c41a' : deviation <= 5 ? '#fa8c16' : '#ff4d4f';
                  })()
                }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="RTP稳定度"
                value={(() => {
                  const recentRtps = progress.real_time_stats.recent_rtps;
                  if (!recentRtps || recentRtps.length < 3) return 0;
                  const variance = recentRtps.reduce((sum, rtp, index, arr) => {
                    const mean = arr.reduce((s, r) => s + r, 0) / arr.length;
                    return sum + Math.pow(rtp - mean, 2);
                  }, 0) / recentRtps.length;
                  const stability = Math.max(0, 100 - variance * 1000);
                  return stability.toFixed(1);
                })()}
                suffix="/100"
                valueStyle={{
                  color: (() => {
                    const recentRtps = progress.real_time_stats.recent_rtps;
                    if (!recentRtps || recentRtps.length < 3) return '#999';
                    const variance = recentRtps.reduce((sum, rtp, index, arr) => {
                      const mean = arr.reduce((s, r) => s + r, 0) / arr.length;
                      return sum + Math.pow(rtp - mean, 2);
                    }, 0) / recentRtps.length;
                    const stability = Math.max(0, 100 - variance * 1000);
                    return stability > 80 ? '#52c41a' : stability > 60 ? '#fa8c16' : '#ff4d4f';
                  })()
                }}
              />
            </Col>
          </Row>

          {/* RTP分级统计 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={24}>
              <Card size="small" title="RTP分级统计" style={{ marginBottom: 12 }}>
                <Row gutter={8}>
                  <Col span={4}>
                    <div style={{ textAlign: 'center', padding: '8px', backgroundColor: '#f6ffed', borderRadius: '4px', border: '1px solid #b7eb8f' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                        {(() => {
                          const recentRtps = progress.real_time_stats.recent_rtps || [];
                          const excellentCount = recentRtps.filter(rtp => rtp >= 0.85).length;
                          return excellentCount;
                        })()}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>优秀(≥85%)</div>
                    </div>
                  </Col>
                  <Col span={4}>
                    <div style={{ textAlign: 'center', padding: '8px', backgroundColor: '#fff7e6', borderRadius: '4px', border: '1px solid #ffd591' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#fa8c16' }}>
                        {(() => {
                          const recentRtps = progress.real_time_stats.recent_rtps || [];
                          const goodCount = recentRtps.filter(rtp => rtp >= 0.75 && rtp < 0.85).length;
                          return goodCount;
                        })()}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>良好(75-85%)</div>
                    </div>
                  </Col>
                  <Col span={4}>
                    <div style={{ textAlign: 'center', padding: '8px', backgroundColor: '#fff2f0', borderRadius: '4px', border: '1px solid #ffb3b3' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#ff4d4f' }}>
                        {(() => {
                          const recentRtps = progress.real_time_stats.recent_rtps || [];
                          const poorCount = recentRtps.filter(rtp => rtp < 0.75).length;
                          return poorCount;
                        })()}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>待改进(&lt;75%)</div>
                    </div>
                  </Col>
                  <Col span={4}>
                    <div style={{ textAlign: 'center', padding: '8px', backgroundColor: '#f0f2f5', borderRadius: '4px', border: '1px solid #d9d9d9' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                        {(() => {
                          const recentRtps = progress.real_time_stats.recent_rtps || [];
                          return recentRtps.length;
                        })()}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>总轮次</div>
                    </div>
                  </Col>
                  <Col span={4}>
                    <div style={{ textAlign: 'center', padding: '8px', backgroundColor: '#f9f0ff', borderRadius: '4px', border: '1px solid #d3adf7' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#722ed1' }}>
                        {(() => {
                          const recentRtps = progress.real_time_stats.recent_rtps || [];
                          if (recentRtps.length === 0) return '0.0';
                          const excellentCount = recentRtps.filter(rtp => rtp >= 0.85).length;
                          return ((excellentCount / recentRtps.length) * 100).toFixed(1);
                        })()}%
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>优秀率</div>
                    </div>
                  </Col>
                  <Col span={4}>
                    <div style={{ textAlign: 'center', padding: '8px', backgroundColor: '#e6f7ff', borderRadius: '4px', border: '1px solid #91d5ff' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                        {(() => {
                          const recentRtps = progress.real_time_stats.recent_rtps || [];
                          if (recentRtps.length === 0) return '0.0';
                          const acceptableCount = recentRtps.filter(rtp => rtp >= 0.75).length;
                          return ((acceptableCount / recentRtps.length) * 100).toFixed(1);
                        })()}%
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>合格率</div>
                    </div>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>

          {/* RTP趋势预测和分析 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Card size="small" title="RTP趋势预测" style={{ height: '100%' }}>
                {progress.real_time_stats.recent_rtps && progress.real_time_stats.recent_rtps.length >= 3 ? (
                  <div>
                    <div style={{ marginBottom: 8 }}>
                      <Text strong>趋势方向: </Text>
                      <Tag color={(() => {
                        const rtps = progress.real_time_stats.recent_rtps;
                        const recent3 = rtps.slice(-3);
                        const trend = recent3[2] - recent3[0];
                        return trend > 0.02 ? 'green' : trend < -0.02 ? 'red' : 'orange';
                      })()}>
                        {(() => {
                          const rtps = progress.real_time_stats.recent_rtps;
                          const recent3 = rtps.slice(-3);
                          const trend = recent3[2] - recent3[0];
                          return trend > 0.02 ? '上升' : trend < -0.02 ? '下降' : '稳定';
                        })()}
                      </Tag>
                    </div>
                    <div style={{ marginBottom: 8 }}>
                      <Text strong>预测下轮RTP: </Text>
                      <Text type={(() => {
                        const rtps = progress.real_time_stats.recent_rtps;
                        const recent3 = rtps.slice(-3);
                        const trend = (recent3[2] - recent3[0]) / 2;
                        const predicted = recent3[2] + trend;
                        return predicted >= 0.85 ? 'success' : predicted >= 0.75 ? 'warning' : 'danger';
                      })()}>
                        {(() => {
                          const rtps = progress.real_time_stats.recent_rtps;
                          const recent3 = rtps.slice(-3);
                          const trend = (recent3[2] - recent3[0]) / 2;
                          const predicted = recent3[2] + trend;
                          return (predicted * 100).toFixed(1) + '%';
                        })()}
                      </Text>
                    </div>
                    <div style={{ marginBottom: 8 }}>
                      <Text strong>波动幅度: </Text>
                      <Text>
                        {(() => {
                          const rtps = progress.real_time_stats.recent_rtps;
                          const max = Math.max(...rtps);
                          const min = Math.min(...rtps);
                          return ((max - min) * 100).toFixed(2) + '%';
                        })()}
                      </Text>
                    </div>
                    <div>
                      <Text strong>收敛性: </Text>
                      <Tag color={(() => {
                        const rtps = progress.real_time_stats.recent_rtps;
                        const recent5 = rtps.slice(-5);
                        if (recent5.length < 5) return 'default';
                        const variance = recent5.reduce((sum, rtp, index, arr) => {
                          const mean = arr.reduce((s, r) => s + r, 0) / arr.length;
                          return sum + Math.pow(rtp - mean, 2);
                        }, 0) / recent5.length;
                        return variance < 0.001 ? 'green' : variance < 0.005 ? 'orange' : 'red';
                      })()}>
                        {(() => {
                          const rtps = progress.real_time_stats.recent_rtps;
                          const recent5 = rtps.slice(-5);
                          if (recent5.length < 5) return '数据不足';
                          const variance = recent5.reduce((sum, rtp, index, arr) => {
                            const mean = arr.reduce((s, r) => s + r, 0) / arr.length;
                            return sum + Math.pow(rtp - mean, 2);
                          }, 0) / recent5.length;
                          return variance < 0.001 ? '高收敛' : variance < 0.005 ? '中收敛' : '低收敛';
                        })()}
                      </Tag>
                    </div>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
                    需要至少3轮数据进行趋势分析
                  </div>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="RTP质量评估" style={{ height: '100%' }}>
                <div>
                  <div style={{ marginBottom: 8 }}>
                    <Text strong>整体评级: </Text>
                    <Tag color={(() => {
                      const currentRtp = progress.real_time_stats.current_rtp || 0;
                      const rtps = progress.real_time_stats.recent_rtps || [];
                      const stability = rtps.length >= 5 ?
                        (1 - (Math.max(...rtps) - Math.min(...rtps))) * 100 : 0;
                      const score = (currentRtp * 100 * 0.7) + (stability * 0.3);
                      return score >= 80 ? 'green' : score >= 70 ? 'orange' : 'red';
                    })()} style={{ fontSize: '14px' }}>
                      {(() => {
                        const currentRtp = progress.real_time_stats.current_rtp || 0;
                        const rtps = progress.real_time_stats.recent_rtps || [];
                        const stability = rtps.length >= 5 ?
                          (1 - (Math.max(...rtps) - Math.min(...rtps))) * 100 : 0;
                        const score = (currentRtp * 100 * 0.7) + (stability * 0.3);
                        return score >= 80 ? 'A级' : score >= 70 ? 'B级' : 'C级';
                      })()}
                    </Tag>
                  </div>
                  <div style={{ marginBottom: 8 }}>
                    <Text strong>质量得分: </Text>
                    <Text strong style={{ color: '#1890ff' }}>
                      {(() => {
                        const currentRtp = progress.real_time_stats.current_rtp || 0;
                        const rtps = progress.real_time_stats.recent_rtps || [];
                        const stability = rtps.length >= 5 ?
                          (1 - (Math.max(...rtps) - Math.min(...rtps))) * 100 : 0;
                        const score = (currentRtp * 100 * 0.7) + (stability * 0.3);
                        return score.toFixed(1);
                      })()}/100
                    </Text>
                  </div>
                  <div style={{ marginBottom: 8 }}>
                    <Text strong>改进建议: </Text>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
                      {(() => {
                        const currentRtp = progress.real_time_stats.current_rtp || 0;
                        const rtps = progress.real_time_stats.recent_rtps || [];
                        if (currentRtp < 0.75) {
                          return '• RTP过低，建议调整奖级设置或奖金比例';
                        } else if (currentRtp > 0.95) {
                          return '• RTP过高，可能影响盈利能力';
                        } else if (rtps.length >= 5 && (Math.max(...rtps) - Math.min(...rtps)) > 0.2) {
                          return '• RTP波动较大，建议优化游戏参数';
                        } else {
                          return '• RTP表现良好，继续保持当前设置';
                        }
                      })()}
                    </div>
                  </div>
                  <div>
                    <Text strong>风险提示: </Text>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
                      {(() => {
                        const currentRtp = progress.real_time_stats.current_rtp || 0;
                        const targetRtp = 0.85;
                        const deviation = Math.abs(currentRtp - targetRtp);
                        if (deviation > 0.1) {
                          return '⚠️ RTP偏离目标值较大，需要关注';
                        } else if (deviation > 0.05) {
                          return '⚡ RTP偏离目标值，建议监控';
                        } else {
                          return '✅ RTP在合理范围内';
                        }
                      })()}
                    </div>
                  </div>
                </div>
              </Card>
            </Col>
          </Row>

          {/* 新增：详细财务分析 */}
          <Divider>财务分析</Divider>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Statistic
                title="销售收入"
                value={progress.real_time_stats.total_sales_amount || progress.real_time_stats.total_bet_amount || 0}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="奖池贡献"
                value={(() => {
                  const currentJackpot = progress.real_time_stats.current_jackpot || 0;
                  const initialJackpot = 800; // 从配置获取，这里暂时硬编码
                  return Math.max(0, currentJackpot - initialJackpot);
                })()}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="卖方返还"
                value={progress.real_time_stats.total_returned_amount || 0}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
                valueStyle={{ color: '#722ed1' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="利润率"
                value={(() => {
                  const totalBet = progress.real_time_stats.total_bet_amount || 0;
                  const totalPayout = progress.real_time_stats.total_payout || 0;
                  return totalBet > 0 ? ((totalBet - totalPayout) / totalBet * 100) : 0;
                })()}
                precision={2}
                suffix="%"
                prefix={<PercentageOutlined />}
                valueStyle={{
                  color: (() => {
                    const totalBet = progress.real_time_stats.total_bet_amount || 0;
                    const totalPayout = progress.real_time_stats.total_payout || 0;
                    const profitRate = totalBet > 0 ? ((totalBet - totalPayout) / totalBet) : 0;
                    return profitRate > 0.2 ? '#52c41a' : '#ff4d4f';
                  })()
                }}
              />
            </Col>
          </Row>

          {/* 新增：游戏统计 */}
          <Divider>游戏统计</Divider>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Statistic
                title="平均每轮玩家"
                value={(() => {
                  const totalPlayers = progress.real_time_stats.total_players || 0;
                  const currentRound = progress.real_time_stats.completed_rounds || progress.current_round || 1;
                  return Math.round(totalPlayers / currentRound);
                })()}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均每人投注"
                value={(() => {
                  const totalBet = progress.real_time_stats.total_bet_amount || 0;
                  const totalPlayers = progress.real_time_stats.total_players || 1;
                  return totalBet / totalPlayers;
                })()}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均每轮投注"
                value={(() => {
                  const totalBet = progress.real_time_stats.total_bet_amount || 0;
                  const currentRound = progress.real_time_stats.completed_rounds || progress.current_round || 1;
                  return totalBet / currentRound;
                })()}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
                valueStyle={{ color: '#13c2c2' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均中奖金额"
                value={(() => {
                  const totalPayout = progress.real_time_stats.total_payout || 0;
                  const totalWinners = progress.real_time_stats.total_winners || 1;
                  return totalPayout / totalWinners;
                })()}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${value.toLocaleString()}`}
                valueStyle={{ color: '#eb2f96' }}
              />
            </Col>
          </Row>

          {/* 新增：奖池状态分析 */}
          {progress.real_time_stats.current_jackpot && (
            <>
              <Divider>奖池状态分析</Divider>
              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={8}>
                  <Statistic
                    title="奖池增长率"
                    value={(() => {
                      const currentJackpot = progress.real_time_stats.current_jackpot || 0;
                      const initialJackpot = progress.real_time_stats.initial_jackpot_amount || 800; // 从后端获取或默认值
                      return initialJackpot > 0 ? ((currentJackpot - initialJackpot) / initialJackpot * 100).toFixed(2) : 0;
                    })()}
                    suffix="%"
                    prefix={<PercentageOutlined />}
                    valueStyle={{
                      color: (() => {
                        const currentJackpot = progress.real_time_stats.current_jackpot || 0;
                        const initialJackpot = progress.real_time_stats.initial_jackpot_amount || 800;
                        return currentJackpot > initialJackpot ? '#52c41a' : '#ff4d4f';
                      })()
                    }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="奖池贡献率"
                    value={(() => {
                      const currentRate = progress.real_time_stats.current_contribution_rate;
                      if (currentRate !== undefined) {
                        return (currentRate * 100).toFixed(2);
                      }
                      // 计算实际贡献率
                      const currentJackpot = progress.real_time_stats.current_jackpot || 0;
                      const initialJackpot = progress.real_time_stats.initial_jackpot_amount || 800;
                      const totalBet = progress.real_time_stats.total_bet_amount || 1;
                      const contribution = Math.max(0, currentJackpot - initialJackpot);
                      return totalBet > 0 ? (contribution / totalBet * 100).toFixed(2) : 0;
                    })()}
                    suffix="%"
                    prefix={<PercentageOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="奖池风险指数"
                    value={(() => {
                      const currentJackpot = progress.real_time_stats.current_jackpot || 0;
                      const totalBet = progress.real_time_stats.total_bet_amount || 1;
                      const riskRatio = currentJackpot / (totalBet * 0.1);
                      return Math.min(100, Math.max(0, riskRatio * 100));
                    })()}
                    precision={1}
                    suffix="/100"
                    valueStyle={{
                      color: (() => {
                        const currentJackpot = progress.real_time_stats.current_jackpot || 0;
                        const totalBet = progress.real_time_stats.total_bet_amount || 1;
                        const riskRatio = currentJackpot / (totalBet * 0.1);
                        return riskRatio > 0.8 ? '#ff4d4f' : '#52c41a';
                      })()
                    }}
                  />
                </Col>
              </Row>
            </>
          )}
        </Card>
      )}

      {/* 图表数据展示 */}
      {simulation && realtimeData && realtimeData.chart_data && (
        <Card title="数据图表与趋势分析" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Card size="small" title="RTP趋势分析">
                {realtimeData.chart_data.rtp_trend && realtimeData.chart_data.rtp_trend.length > 0 ? (
                  <div>
                    <Row gutter={8} style={{ marginBottom: 12 }}>
                      <Col span={8}>
                        <Statistic
                          title="数据点数"
                          value={realtimeData.chart_data.rtp_trend.length}
                          valueStyle={{ fontSize: '14px' }}
                        />
                      </Col>
                      <Col span={8}>
                        <Statistic
                          title="最新RTP"
                          value={(realtimeData.chart_data.rtp_trend[realtimeData.chart_data.rtp_trend.length - 1] * 100)?.toFixed(2)}
                          suffix="%"
                          valueStyle={{ fontSize: '14px', color: '#1890ff' }}
                        />
                      </Col>
                      <Col span={8}>
                        <Statistic
                          title="平均RTP"
                          value={((realtimeData.chart_data.rtp_trend.reduce((a, b) => a + b, 0) / realtimeData.chart_data.rtp_trend.length) * 100).toFixed(2)}
                          suffix="%"
                          valueStyle={{ fontSize: '14px', color: '#52c41a' }}
                        />
                      </Col>
                    </Row>
                    <Row gutter={8}>
                      <Col span={8}>
                        <Statistic
                          title="最高RTP"
                          value={(Math.max(...realtimeData.chart_data.rtp_trend) * 100).toFixed(2)}
                          suffix="%"
                          valueStyle={{ fontSize: '14px', color: '#f5222d' }}
                        />
                      </Col>
                      <Col span={8}>
                        <Statistic
                          title="最低RTP"
                          value={(Math.min(...realtimeData.chart_data.rtp_trend) * 100).toFixed(2)}
                          suffix="%"
                          valueStyle={{ fontSize: '14px', color: '#fa8c16' }}
                        />
                      </Col>
                      <Col span={8}>
                        <Statistic
                          title="RTP波动"
                          value={((Math.max(...realtimeData.chart_data.rtp_trend) - Math.min(...realtimeData.chart_data.rtp_trend)) * 100).toFixed(2)}
                          suffix="%"
                          valueStyle={{ fontSize: '14px', color: '#722ed1' }}
                        />
                      </Col>
                    </Row>
                  </div>
                ) : (
                  <p style={{ textAlign: 'center', color: '#999' }}>暂无数据</p>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="奖级分布统计">
                {realtimeData.chart_data.prize_distribution && realtimeData.chart_data.prize_distribution.length > 0 ? (
                  <div>
                    {realtimeData.chart_data.prize_distribution.map((prize, index) => (
                      <div key={index} style={{ marginBottom: 12 }}>
                        <Row justify="space-between" align="middle">
                          <Col span={8}>
                            <Tag color={prize.level === 1 ? 'gold' : prize.level === 2 ? 'silver' : 'blue'}>
                              {prize.name}
                            </Tag>
                          </Col>
                          <Col span={8} style={{ textAlign: 'center' }}>
                            <Text strong>{prize.count}人</Text>
                          </Col>
                          <Col span={8} style={{ textAlign: 'right' }}>
                            <Text type="success">¥{prize.amount.toLocaleString()}</Text>
                          </Col>
                        </Row>
                        <Row style={{ marginTop: 4 }}>
                          <Col span={24}>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                              平均每人: ¥{(prize.amount / (prize.count || 1)).toLocaleString()} |
                              占总奖金: {((prize.amount / realtimeData.chart_data.prize_distribution.reduce((sum, p) => sum + p.amount, 0)) * 100).toFixed(1)}%
                            </div>
                          </Col>
                        </Row>
                      </div>
                    ))}
                    <Divider style={{ margin: '12px 0' }} />
                    <Row justify="space-between">
                      <Col>
                        <Text strong>总计:</Text>
                      </Col>
                      <Col>
                        <Text strong>
                          {realtimeData.chart_data.prize_distribution.reduce((sum, p) => sum + p.count, 0)}人 /
                          ¥{realtimeData.chart_data.prize_distribution.reduce((sum, p) => sum + p.amount, 0).toLocaleString()}
                        </Text>
                      </Col>
                    </Row>
                  </div>
                ) : (
                  <p style={{ textAlign: 'center', color: '#999' }}>暂无中奖数据</p>
                )}
              </Card>
            </Col>
          </Row>

          {/* 奖池趋势分析 */}
          {realtimeData.chart_data.jackpot_trend && realtimeData.chart_data.jackpot_trend.length > 0 && (
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={24}>
                <Card size="small" title="奖池趋势分析">
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic
                        title="初始奖池"
                        value={realtimeData.chart_data.jackpot_trend[0]}
                        precision={2}
                        prefix="¥"
                        valueStyle={{ fontSize: '14px', color: '#1890ff' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="当前奖池"
                        value={realtimeData.chart_data.jackpot_trend[realtimeData.chart_data.jackpot_trend.length - 1]}
                        precision={2}
                        prefix="¥"
                        valueStyle={{ fontSize: '14px', color: '#52c41a' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="最高奖池"
                        value={Math.max(...realtimeData.chart_data.jackpot_trend)}
                        precision={2}
                        prefix="¥"
                        valueStyle={{ fontSize: '14px', color: '#f5222d' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="奖池变化"
                        value={realtimeData.chart_data.jackpot_trend[realtimeData.chart_data.jackpot_trend.length - 1] - realtimeData.chart_data.jackpot_trend[0]}
                        precision={2}
                        prefix={realtimeData.chart_data.jackpot_trend[realtimeData.chart_data.jackpot_trend.length - 1] >= realtimeData.chart_data.jackpot_trend[0] ? '+¥' : '-¥'}
                        valueStyle={{
                          fontSize: '14px',
                          color: realtimeData.chart_data.jackpot_trend[realtimeData.chart_data.jackpot_trend.length - 1] >= realtimeData.chart_data.jackpot_trend[0] ? '#52c41a' : '#f5222d'
                        }}
                      />
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          )}
        </Card>
      )}

      {/* 新增：综合分析报告 */}
      {simulation && progress && progress.real_time_stats && (
        <Card title="综合分析报告" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Card size="small" title="模拟进度分析" style={{ height: '100%' }}>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>模拟完成度: </Text>
                  <Text>{((progress.current_round / progress.total_rounds) * 100).toFixed(1)}%</Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>预计剩余时间: </Text>
                  <Text>
                    {progress.current_round < progress.total_rounds ?
                      `约${Math.ceil((progress.total_rounds - progress.current_round) * 0.1)}秒` :
                      '已完成'
                    }
                  </Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>模拟效率: </Text>
                  <Text>{progress.current_round > 0 ? `${(progress.current_round / ((Date.now() - new Date(simulation.start_time)) / 1000)).toFixed(1)} 轮/秒` : '计算中...'}</Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>数据质量: </Text>
                  <Tag color={progress.current_round >= 10 ? 'green' : progress.current_round >= 5 ? 'orange' : 'red'}>
                    {progress.current_round >= 10 ? '优秀' : progress.current_round >= 5 ? '良好' : '待提升'}
                  </Tag>
                </div>
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="风险评估" style={{ height: '100%' }}>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>RTP稳定性: </Text>
                  <Tag color={(() => {
                    const recentRtps = progress.real_time_stats.recent_rtps;
                    if (!recentRtps || recentRtps.length < 5) return 'red';
                    const volatility = Math.max(...recentRtps) - Math.min(...recentRtps);
                    return volatility < 0.2 ? 'green' : 'orange';
                  })()}>
                    {(() => {
                      const recentRtps = progress.real_time_stats.recent_rtps;
                      if (!recentRtps || recentRtps.length < 5) return '数据不足';
                      const volatility = Math.max(...recentRtps) - Math.min(...recentRtps);
                      return volatility < 0.2 ? '稳定' : '波动';
                    })()}
                  </Tag>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>奖池风险: </Text>
                  <Tag color={(() => {
                    const currentJackpot = progress.real_time_stats.current_jackpot || 0;
                    const totalBet = progress.real_time_stats.total_bet_amount || 1;
                    const ratio = currentJackpot / totalBet;
                    return ratio > 0.5 ? 'red' : ratio > 0.3 ? 'orange' : 'green';
                  })()}>
                    {(() => {
                      const currentJackpot = progress.real_time_stats.current_jackpot || 0;
                      const totalBet = progress.real_time_stats.total_bet_amount || 1;
                      const ratio = currentJackpot / totalBet;
                      return ratio > 0.5 ? '高风险' : ratio > 0.3 ? '中风险' : '低风险';
                    })()}
                  </Tag>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>盈利能力: </Text>
                  <Tag color={(() => {
                    const totalBet = progress.real_time_stats.total_bet_amount || 1;
                    const totalPayout = progress.real_time_stats.total_payout || 0;
                    const profitRate = (totalBet - totalPayout) / totalBet;
                    return profitRate > 0.2 ? 'green' : profitRate > 0.1 ? 'orange' : 'red';
                  })()}>
                    {(() => {
                      const totalBet = progress.real_time_stats.total_bet_amount || 1;
                      const totalPayout = progress.real_time_stats.total_payout || 0;
                      const profitRate = (totalBet - totalPayout) / totalBet;
                      return profitRate > 0.2 ? '优秀' : profitRate > 0.1 ? '良好' : '需改进';
                    })()}
                  </Tag>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>玩家满意度: </Text>
                  <Tag color={(() => {
                    const winningRate = progress.real_time_stats.winning_rate || 0;
                    return winningRate > 0.3 ? 'green' : winningRate > 0.2 ? 'orange' : 'red';
                  })()}>
                    {(() => {
                      const winningRate = progress.real_time_stats.winning_rate || 0;
                      return winningRate > 0.3 ? '高' : winningRate > 0.2 ? '中' : '低';
                    })()}
                  </Tag>
                </div>
              </Card>
            </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={24}>
              <Card size="small" title="关键指标总结">
                <Row gutter={16}>
                  <Col span={6}>
                    <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#f0f2f5', borderRadius: '6px' }}>
                      <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                        {((progress.real_time_stats.current_rtp || 0) * 100).toFixed(1)}%
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>当前RTP</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#f0f2f5', borderRadius: '6px' }}>
                      <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
                        ¥{(progress.real_time_stats.current_jackpot || 0).toLocaleString()}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>奖池余额</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#f0f2f5', borderRadius: '6px' }}>
                      <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fa8c16' }}>
                        {((progress.real_time_stats.winning_rate || 0) * 100).toFixed(1)}%
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>中奖率</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#f0f2f5', borderRadius: '6px' }}>
                      <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#722ed1' }}>
                        {(() => {
                          const totalBet = progress.real_time_stats.total_bet_amount || 1;
                          const totalPayout = progress.real_time_stats.total_payout || 0;
                          return ((totalBet - totalPayout) / totalBet * 100).toFixed(1);
                        })()}%
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>利润率</div>
                    </div>
                  </Col>
                </Row>
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
