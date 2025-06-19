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
  Empty
} from 'antd';
import {
  DownloadOutlined,
  ReloadOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import Plot from 'react-plotly.js';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;

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
          {/* 汇总统计 */}
          {result.summary && (
            <Card title="汇总统计" style={{ marginBottom: 24 }}>
              <Row gutter={16}>
                <Col xs={24} sm={12} md={6}>
                  <Statistic
                    title="总轮数"
                    value={result.summary.total_rounds}
                    formatter={(value) => value?.toLocaleString()}
                  />
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Statistic
                    title="总投注金额"
                    value={result.summary.total_bet_amount}
                    formatter={(value) => formatCurrency(value)}
                  />
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Statistic
                    title="总派奖金额"
                    value={result.summary.total_payout}
                    formatter={(value) => formatCurrency(value)}
                  />
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Statistic
                    title="平均RTP"
                    value={result.summary.average_rtp}
                    formatter={(value) => formatPercentage(value)}
                    valueStyle={{ 
                      color: result.summary.average_rtp > 0.9 ? '#3f8600' : '#cf1322' 
                    }}
                  />
                </Col>
              </Row>
              
              <Row gutter={16} style={{ marginTop: 16 }}>
                <Col xs={24} sm={12} md={6}>
                  <Statistic
                    title="总玩家数"
                    value={result.summary.total_players}
                    formatter={(value) => value?.toLocaleString()}
                  />
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Statistic
                    title="头奖中出次数"
                    value={result.summary.jackpot_hits}
                  />
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Statistic
                    title="初始奖池"
                    value={result.summary.initial_jackpot}
                    formatter={(value) => formatCurrency(value)}
                  />
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Statistic
                    title="最终奖池"
                    value={result.summary.final_jackpot}
                    formatter={(value) => formatCurrency(value)}
                  />
                </Col>
              </Row>
            </Card>
          )}

          {/* 图表展示 */}
          {charts.length > 0 && (
            <Row gutter={16} style={{ marginBottom: 24 }}>
              {charts.map((chart, index) => (
                <Col xs={24} lg={12} key={index}>
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
          )}

          {/* 奖级统计 */}
          {result.summary?.prize_summary && (
            <Card title="奖级统计详情" style={{ marginBottom: 24 }}>
              <Table
                dataSource={result.summary.prize_summary}
                columns={prizeColumns}
                rowKey="level"
                pagination={false}
                size="middle"
              />
            </Card>
          )}

          {/* 模拟信息 */}
          <Card title="模拟信息">
            <Row gutter={16}>
              <Col span={8}>
                <Text strong>模拟ID: </Text>
                <Text code>{result.simulation_id}</Text>
              </Col>
              <Col span={8}>
                <Text strong>游戏名称: </Text>
                <Text>{result.game_name}</Text>
              </Col>
              <Col span={8}>
                <Text strong>状态: </Text>
                <Text type={result.status === 'completed' ? 'success' : 'danger'}>
                  {result.status === 'completed' ? '已完成' : result.status}
                </Text>
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={8}>
                <Text strong>开始时间: </Text>
                <Text>{new Date(result.start_time).toLocaleString()}</Text>
              </Col>
              <Col span={8}>
                <Text strong>结束时间: </Text>
                <Text>{result.end_time ? new Date(result.end_time).toLocaleString() : '-'}</Text>
              </Col>
              <Col span={8}>
                <Text strong>耗时: </Text>
                <Text>{result.duration ? `${result.duration.toFixed(2)}秒` : '-'}</Text>
              </Col>
            </Row>
          </Card>
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
