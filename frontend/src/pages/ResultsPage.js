import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Row,
  Col,
  Statistic,
  Select,
  Button,
  Space,
  Typography,
  message,
  Empty,
  Divider,
  Progress,
  Tag,
  Descriptions,
  Alert,
  Tabs
} from 'antd';
import {
  DownloadOutlined,
  ReloadOutlined,
  BarChartOutlined,
  TrophyOutlined,
  DollarOutlined,
  PercentageOutlined,
  UserOutlined,
  LineChartOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import Plot from 'react-plotly.js';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const ResultsPage = () => {
  const [simulations, setSimulations] = useState([]);
  const [selectedSimulation, setSelectedSimulation] = useState(null);
  const [result, setResult] = useState(null);
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSimulations();
  }, []);

  useEffect(() => {
    if (selectedSimulation) {
      fetchResult(selectedSimulation);
    }
  }, [selectedSimulation]);

  const fetchSimulations = async () => {
    try {
      const response = await axios.get('/api/v1/simulation/list');
      const completedSims = response.data.simulations.filter(
        sim => sim.status === 'completed'
      );
      setSimulations(completedSims);
      
      if (completedSims.length > 0 && !selectedSimulation) {
        setSelectedSimulation(completedSims[0].simulation_id);
      }
    } catch (error) {
      message.error('获取模拟列表失败');
    }
  };

  const fetchResult = async (simulationId) => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/v1/simulation/result/${simulationId}`);
      setResult(response.data);
      
      // 获取图表数据
      try {
        const chartsResponse = await axios.get(`/api/v1/reports/charts/${simulationId}`);
        setCharts(chartsResponse.data.charts);
      } catch (error) {
        console.error('获取图表数据失败:', error);
      }
    } catch (error) {
      message.error('获取模拟结果失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async (format) => {
    if (!selectedSimulation) return;
    
    try {
      const response = await axios.get(
        `/api/v1/reports/download/${selectedSimulation}?format=${format}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `simulation_report_${selectedSimulation}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('报告下载成功');
    } catch (error) {
      message.error('下载报告失败');
    }
  };

  const formatCurrency = (amount) => {
    return `¥${amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`;
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const prizeColumns = [
    {
      title: '奖级',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '中奖人数',
      dataIndex: 'winners_count',
      key: 'winners_count',
      render: (value) => value?.toLocaleString()
    },
    {
      title: '总奖金',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (value) => formatCurrency(value)
    },
    {
      title: '中奖概率',
      dataIndex: 'probability',
      key: 'probability',
      render: (value) => formatPercentage(value)
    }
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={1}>结果分析</Title>
        <Text>查看和分析模拟结果数据</Text>
      </div>

      {/* 模拟选择 */}
      <Card title="选择模拟" style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Select
              style={{ width: '100%' }}
              placeholder="选择要查看的模拟结果"
              value={selectedSimulation}
              onChange={setSelectedSimulation}
              loading={loading}
            >
              {simulations.map(sim => (
                <Option key={sim.simulation_id} value={sim.simulation_id}>
                  {sim.game_name} - {new Date(sim.start_time).toLocaleString()}
                </Option>
              ))}
            </Select>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchSimulations}
              >
                刷新
              </Button>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={() => handleDownloadReport('html')}
                disabled={!selectedSimulation}
              >
                下载报告
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {result ? (
        <>
          {/* 模拟状态概览 */}
          <Card style={{ marginBottom: 24 }}>
            <Row gutter={16} align="middle">
              <Col span={6}>
                <div style={{ textAlign: 'center' }}>
                  <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
                  <div style={{ marginTop: 8 }}>
                    <Text strong>模拟完成</Text>
                    <br />
                    <Text type="secondary">{new Date(result.end_time).toLocaleString()}</Text>
                  </div>
                </div>
              </Col>
              <Col span={18}>
                <Descriptions column={3} size="small">
                  <Descriptions.Item label="游戏名称">{result.game_name}</Descriptions.Item>
                  <Descriptions.Item label="模拟轮数">{result.summary?.total_rounds?.toLocaleString()}</Descriptions.Item>
                  <Descriptions.Item label="耗时">{result.duration ? `${result.duration.toFixed(2)}秒` : '-'}</Descriptions.Item>
                  <Descriptions.Item label="平均RTP">
                    <Tag color={result.summary?.average_rtp > 0.85 ? 'green' : result.summary?.average_rtp > 0.75 ? 'orange' : 'red'}>
                      {formatPercentage(result.summary?.average_rtp)}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="总投注">{formatCurrency(result.summary?.total_bet_amount)}</Descriptions.Item>
                  <Descriptions.Item label="总派奖">{formatCurrency(result.summary?.total_payout)}</Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
          </Card>

          {/* 详细分析标签页 */}
          <Tabs defaultActiveKey="overview" style={{ marginBottom: 24 }}>
            <TabPane tab={<span><BarChartOutlined />核心指标</span>} key="overview">
              {/* 核心指标卡片 */}
              <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={12} md={6}>
                  <Card size="small" style={{ textAlign: 'center', backgroundColor: '#f6ffed' }}>
                    <TrophyOutlined style={{ fontSize: '24px', color: '#52c41a', marginBottom: 8 }} />
                    <Statistic
                      title="平均RTP"
                      value={result.summary?.average_rtp}
                      formatter={(value) => formatPercentage(value)}
                      valueStyle={{ color: '#52c41a', fontSize: '20px' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card size="small" style={{ textAlign: 'center', backgroundColor: '#fff7e6' }}>
                    <DollarOutlined style={{ fontSize: '24px', color: '#fa8c16', marginBottom: 8 }} />
                    <Statistic
                      title="利润率"
                      value={(() => {
                        const totalBet = result.summary?.total_bet_amount || 1;
                        const totalPayout = result.summary?.total_payout || 0;
                        return (totalBet - totalPayout) / totalBet;
                      })()}
                      formatter={(value) => formatPercentage(value)}
                      valueStyle={{ color: '#fa8c16', fontSize: '20px' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card size="small" style={{ textAlign: 'center', backgroundColor: '#f0f5ff' }}>
                    <UserOutlined style={{ fontSize: '24px', color: '#1890ff', marginBottom: 8 }} />
                    <Statistic
                      title="中奖率"
                      value={(() => {
                        const totalPlayers = result.summary?.total_players || 1;
                        const totalWinners = result.summary?.prize_summary?.reduce((sum, prize) => sum + (prize.winners_count || 0), 0) || 0;
                        return totalWinners / totalPlayers;
                      })()}
                      formatter={(value) => formatPercentage(value)}
                      valueStyle={{ color: '#1890ff', fontSize: '20px' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card size="small" style={{ textAlign: 'center', backgroundColor: '#f9f0ff' }}>
                    <PercentageOutlined style={{ fontSize: '24px', color: '#722ed1', marginBottom: 8 }} />
                    <Statistic
                      title="奖池增长"
                      value={(() => {
                        const initial = result.summary?.initial_jackpot || 1;
                        const final = result.summary?.final_jackpot || 0;
                        return (final - initial) / initial;
                      })()}
                      formatter={(value) => formatPercentage(value)}
                      valueStyle={{ color: '#722ed1', fontSize: '20px' }}
                    />
                  </Card>
                </Col>
              </Row>

              {/* 详细统计 */}
              <Row gutter={16}>
                <Col xs={24} lg={12}>
                  <Card title="投注与派奖统计" size="small">
                    <Row gutter={16}>
                      <Col span={12}>
                        <Statistic
                          title="总投注金额"
                          value={result.summary?.total_bet_amount}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="总派奖金额"
                          value={result.summary?.total_payout}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Col>
                    </Row>
                    <Divider />
                    <Row gutter={16}>
                      <Col span={12}>
                        <Statistic
                          title="平均每轮投注"
                          value={result.summary?.total_bet_amount / (result.summary?.total_rounds || 1)}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="平均每轮派奖"
                          value={result.summary?.total_payout / (result.summary?.total_rounds || 1)}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Col>
                    </Row>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="玩家与中奖统计" size="small">
                    <Row gutter={16}>
                      <Col span={12}>
                        <Statistic
                          title="总玩家数"
                          value={result.summary?.total_players}
                          formatter={(value) => value?.toLocaleString()}
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="总中奖人数"
                          value={result.summary?.prize_summary?.reduce((sum, prize) => sum + (prize.winners_count || 0), 0)}
                          formatter={(value) => value?.toLocaleString()}
                        />
                      </Col>
                    </Row>
                    <Divider />
                    <Row gutter={16}>
                      <Col span={12}>
                        <Statistic
                          title="平均每轮玩家"
                          value={result.summary?.total_players / (result.summary?.total_rounds || 1)}
                          formatter={(value) => value?.toFixed(0)}
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="平均每人投注"
                          value={result.summary?.total_bet_amount / (result.summary?.total_players || 1)}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Col>
                    </Row>
                  </Card>
                </Col>
              </Row>
            </TabPane>

            <TabPane tab={<span><LineChartOutlined />图表分析</span>} key="charts">
              {/* 图表展示 */}
              {charts.length > 0 ? (
                <Row gutter={16}>
                  {charts.map((chart, index) => (
                    <Col xs={24} lg={12} key={index} style={{ marginBottom: 16 }}>
                      <Card title={chart.title} className="chart-container">
                        <Plot
                          data={[chart.data]}
                          layout={{
                            ...chart.config?.layout,
                            autosize: true,
                            margin: { t: 20, r: 20, b: 40, l: 60 }
                          }}
                          style={{ width: '100%', height: '400px' }}
                          useResizeHandler={true}
                        />
                      </Card>
                    </Col>
                  ))}
                </Row>
              ) : (
                <Alert
                  message="暂无图表数据"
                  description="图表数据正在生成中，请稍后刷新页面查看。"
                  type="info"
                  showIcon
                />
              )}
            </TabPane>

            <TabPane tab={<span><TrophyOutlined />奖级分析</span>} key="prizes">
              {/* 奖级统计 */}
              {result.summary?.prize_summary ? (
                <>
                  {/* 奖级概览卡片 */}
                  <Row gutter={16} style={{ marginBottom: 24 }}>
                    {result.summary.prize_summary.map((prize, index) => (
                      <Col xs={24} sm={12} md={8} lg={6} key={prize.level} style={{ marginBottom: 16 }}>
                        <Card size="small" style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff', marginBottom: 8 }}>
                            {prize.name}
                          </div>
                          <Row gutter={8}>
                            <Col span={24}>
                              <Statistic
                                title="中奖人数"
                                value={prize.winners_count}
                                formatter={(value) => value?.toLocaleString()}
                                valueStyle={{ fontSize: '16px' }}
                              />
                            </Col>
                          </Row>
                          <Divider style={{ margin: '8px 0' }} />
                          <Row gutter={8}>
                            <Col span={24}>
                              <Statistic
                                title="总奖金"
                                value={prize.total_amount}
                                formatter={(value) => formatCurrency(value)}
                                valueStyle={{ fontSize: '14px', color: '#52c41a' }}
                              />
                            </Col>
                          </Row>
                          <Divider style={{ margin: '8px 0' }} />
                          <Row gutter={8}>
                            <Col span={24}>
                              <Statistic
                                title="中奖概率"
                                value={prize.probability}
                                formatter={(value) => formatPercentage(value)}
                                valueStyle={{ fontSize: '14px', color: '#fa8c16' }}
                              />
                            </Col>
                          </Row>
                          <Divider style={{ margin: '8px 0' }} />
                          <Row gutter={8}>
                            <Col span={24}>
                              <Statistic
                                title="平均奖金"
                                value={prize.winners_count > 0 ? prize.total_amount / prize.winners_count : 0}
                                formatter={(value) => formatCurrency(value)}
                                valueStyle={{ fontSize: '14px', color: '#722ed1' }}
                              />
                            </Col>
                          </Row>
                        </Card>
                      </Col>
                    ))}
                  </Row>

                  {/* 详细奖级表格 */}
                  <Card title="奖级统计详情" size="small">
                    <Table
                      dataSource={result.summary.prize_summary.map(prize => ({
                        ...prize,
                        average_amount: prize.winners_count > 0 ? prize.total_amount / prize.winners_count : 0,
                        percentage_of_total: (prize.total_amount / (result.summary?.total_payout || 1)) * 100
                      }))}
                      columns={[
                        ...prizeColumns,
                        {
                          title: '平均奖金',
                          dataIndex: 'average_amount',
                          key: 'average_amount',
                          render: (value) => formatCurrency(value)
                        },
                        {
                          title: '占总派奖比例',
                          dataIndex: 'percentage_of_total',
                          key: 'percentage_of_total',
                          render: (value) => `${value.toFixed(2)}%`
                        }
                      ]}
                      rowKey="level"
                      pagination={false}
                      size="small"
                    />
                  </Card>
                </>
              ) : (
                <Alert
                  message="暂无奖级数据"
                  description="奖级统计数据不可用。"
                  type="warning"
                  showIcon
                />
              )}
            </TabPane>

            <TabPane tab={<span><InfoCircleOutlined />详细信息</span>} key="details">
              {/* 模拟配置信息 */}
              <Row gutter={16}>
                <Col xs={24} lg={12}>
                  <Card title="模拟基本信息" size="small" style={{ marginBottom: 16 }}>
                    <Descriptions column={1} size="small">
                      <Descriptions.Item label="模拟ID">
                        <Text code>{result.simulation_id}</Text>
                      </Descriptions.Item>
                      <Descriptions.Item label="游戏名称">{result.game_name}</Descriptions.Item>
                      <Descriptions.Item label="状态">
                        <Tag color={result.status === 'completed' ? 'green' : 'red'}>
                          {result.status === 'completed' ? '已完成' : result.status}
                        </Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="开始时间">
                        {new Date(result.start_time).toLocaleString()}
                      </Descriptions.Item>
                      <Descriptions.Item label="结束时间">
                        {result.end_time ? new Date(result.end_time).toLocaleString() : '-'}
                      </Descriptions.Item>
                      <Descriptions.Item label="总耗时">
                        {result.duration ? `${result.duration.toFixed(2)}秒` : '-'}
                      </Descriptions.Item>
                    </Descriptions>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="性能指标" size="small" style={{ marginBottom: 16 }}>
                    <Descriptions column={1} size="small">
                      <Descriptions.Item label="模拟轮数">
                        {result.summary?.total_rounds?.toLocaleString()}
                      </Descriptions.Item>
                      <Descriptions.Item label="平均每秒轮数">
                        {result.duration ? ((result.summary?.total_rounds || 0) / result.duration).toFixed(0) : '-'}
                      </Descriptions.Item>
                      <Descriptions.Item label="数据完整性">
                        <Progress
                          percent={result.summary?.total_rounds > 0 ? 100 : 0}
                          size="small"
                          status={result.summary?.total_rounds > 0 ? 'success' : 'exception'}
                        />
                      </Descriptions.Item>
                      <Descriptions.Item label="RTP稳定性">
                        <Progress
                          percent={(() => {
                            const rtp = result.summary?.average_rtp || 0;
                            const target = 0.85;
                            const deviation = Math.abs(rtp - target);
                            return Math.max(0, 100 - deviation * 1000);
                          })()}
                          size="small"
                          status={(() => {
                            const rtp = result.summary?.average_rtp || 0;
                            const target = 0.85;
                            const deviation = Math.abs(rtp - target);
                            return deviation < 0.02 ? 'success' : deviation < 0.05 ? 'active' : 'exception';
                          })()}
                        />
                      </Descriptions.Item>
                    </Descriptions>
                  </Card>
                </Col>
              </Row>

              {/* 质量评估 */}
              <Card title="模拟质量评估" size="small">
                <Row gutter={16}>
                  <Col xs={24} sm={8}>
                    <div style={{ textAlign: 'center', padding: '16px' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#52c41a' }}>
                        {(() => {
                          const rtp = result.summary?.average_rtp || 0;
                          const completeness = result.summary?.total_rounds > 1000 ? 1 : (result.summary?.total_rounds || 0) / 1000;
                          const score = (rtp * 0.7 + completeness * 0.3) * 100;
                          return score.toFixed(0);
                        })()}
                      </div>
                      <div style={{ color: '#666', marginTop: 4 }}>质量评分</div>
                    </div>
                  </Col>
                  <Col xs={24} sm={16}>
                    <div style={{ padding: '16px 0' }}>
                      <div style={{ marginBottom: 12 }}>
                        <Text strong>RTP准确性: </Text>
                        <Progress
                          percent={(() => {
                            const rtp = result.summary?.average_rtp || 0;
                            return Math.min(100, rtp * 100);
                          })()}
                          size="small"
                          strokeColor={{
                            '0%': '#ff4d4f',
                            '75%': '#fa8c16',
                            '85%': '#52c41a',
                            '100%': '#52c41a'
                          }}
                        />
                      </div>
                      <div style={{ marginBottom: 12 }}>
                        <Text strong>数据完整性: </Text>
                        <Progress
                          percent={result.summary?.total_rounds > 1000 ? 100 : ((result.summary?.total_rounds || 0) / 1000) * 100}
                          size="small"
                        />
                      </div>
                      <div style={{ marginBottom: 12 }}>
                        <Text strong>中奖分布: </Text>
                        <Progress
                          percent={(() => {
                            const prizeCount = result.summary?.prize_summary?.length || 0;
                            return Math.min(100, (prizeCount / 5) * 100);
                          })()}
                          size="small"
                        />
                      </div>
                    </div>
                  </Col>
                </Row>

                {/* 建议和提示 */}
                <Divider />
                <div>
                  <Text strong>分析建议：</Text>
                  <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                    {(() => {
                      const suggestions = [];
                      const rtp = result.summary?.average_rtp || 0;
                      const rounds = result.summary?.total_rounds || 0;

                      if (rtp < 0.75) {
                        suggestions.push('RTP偏低，建议检查奖级设置和概率配置');
                      } else if (rtp > 0.95) {
                        suggestions.push('RTP偏高，可能影响盈利能力，建议适当调整');
                      } else {
                        suggestions.push('RTP在合理范围内，表现良好');
                      }

                      if (rounds < 1000) {
                        suggestions.push('建议增加模拟轮数以获得更准确的统计结果');
                      }

                      if (result.summary?.jackpot_hits === 0) {
                        suggestions.push('模拟中未出现头奖，可能需要更多轮次或调整概率');
                      }

                      return suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ));
                    })()}
                  </ul>
                </div>
              </Card>
            </TabPane>
          </Tabs>
        </>
      ) : (
        <Card>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="请选择一个模拟结果进行查看"
          />
        </Card>
      )}
    </div>
  );
};

export default ResultsPage;
