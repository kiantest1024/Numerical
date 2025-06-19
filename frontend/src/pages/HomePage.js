import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Typography, Space, Alert } from 'antd';
import {
  PlayCircleOutlined,
  SettingOutlined,
  BarChartOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const { Title, Paragraph } = Typography;

const HomePage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalSimulations: 0,
    runningSimulations: 0,
    completedSimulations: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/v1/simulation/list');
      const simulations = response.data.simulations || [];
      
      const running = simulations.filter(s => s.status === 'running').length;
      const completed = simulations.filter(s => s.status === 'completed').length;
      
      setStats({
        totalSimulations: simulations.length,
        runningSimulations: running,
        completedSimulations: completed
      });
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: '配置游戏',
      description: '设置游戏规则和参数',
      icon: <SettingOutlined style={{ fontSize: '24px', color: '#1890ff' }} />,
      action: () => navigate('/config'),
      color: '#1890ff'
    },
    {
      title: '运行模拟',
      description: '开始数值模拟验证',
      icon: <PlayCircleOutlined style={{ fontSize: '24px', color: '#52c41a' }} />,
      action: () => navigate('/simulation'),
      color: '#52c41a'
    },
    {
      title: '查看结果',
      description: '分析模拟结果数据',
      icon: <BarChartOutlined style={{ fontSize: '24px', color: '#722ed1' }} />,
      action: () => navigate('/results'),
      color: '#722ed1'
    }
  ];

  const features = [
    {
      title: '灵活配置',
      description: '支持多种游戏类型，包括彩票、刮刮乐等，可自定义游戏规则和奖级设置'
    },
    {
      title: '高性能模拟',
      description: '基于NumPy和Pandas优化，支持百万级轮次的大规模数值模拟'
    },
    {
      title: 'RTP精确计算',
      description: '精确计算普通奖金和Jackpot奖金的返奖率，支持复杂的奖池机制'
    },
    {
      title: '可视化分析',
      description: '提供丰富的图表和统计数据，支持一键导出HTML报告'
    }
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={1}>
          <RocketOutlined style={{ marginRight: '12px', color: '#1890ff' }} />
          欢迎使用 @numericalTools
        </Title>
        <Paragraph>
          通用数值模拟验证工具，专为游戏RTP验证需求设计，支持各种游戏类型的精确模拟和分析。
        </Paragraph>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总模拟次数"
              value={stats.totalSimulations}
              loading={loading}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="运行中"
              value={stats.runningSimulations}
              loading={loading}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completedSimulations}
              loading={loading}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 快速操作 */}
      <Card title="快速开始" style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          {quickActions.map((action, index) => (
            <Col xs={24} sm={8} key={index}>
              <Card
                hoverable
                style={{ textAlign: 'center', height: '160px' }}
                onClick={action.action}
              >
                <Space direction="vertical" size="middle">
                  {action.icon}
                  <Title level={4} style={{ margin: 0 }}>
                    {action.title}
                  </Title>
                  <Paragraph style={{ margin: 0, color: '#666' }}>
                    {action.description}
                  </Paragraph>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 功能特性 */}
      <Card title="核心功能">
        <Row gutter={[16, 16]}>
          {features.map((feature, index) => (
            <Col xs={24} sm={12} key={index}>
              <Card size="small" style={{ height: '120px' }}>
                <Title level={5} style={{ marginBottom: '8px' }}>
                  {feature.title}
                </Title>
                <Paragraph style={{ margin: 0, fontSize: '14px', color: '#666' }}>
                  {feature.description}
                </Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 使用提示 */}
      <Alert
        message="使用提示"
        description={
          <div>
            <p>1. 首先在"游戏配置"页面创建或选择一个配置</p>
            <p>2. 在"运行模拟"页面选择配置并启动模拟</p>
            <p>3. 模拟过程中可以实时查看进度</p>
            <p>4. 模拟完成后可以在"结果分析"页面查看详细结果</p>
          </div>
        }
        type="info"
        showIcon
        style={{ marginTop: '24px' }}
      />
    </div>
  );
};

export default HomePage;
