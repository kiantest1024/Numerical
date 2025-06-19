import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Select,
  Typography,
  message,
  Tag,
  Dropdown,
  Menu
} from 'antd';
import {
  DownloadOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  EyeOutlined,
  MoreOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;

const ReportsPage = () => {
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/simulation/list');
      setSimulations(response.data.simulations || []);
    } catch (error) {
      message.error('获取模拟列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async (simulationId, format) => {
    try {
      const response = await axios.get(
        `/api/v1/reports/download/${simulationId}?format=${format}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const extension = format === 'excel' ? 'xlsx' : format;
      link.setAttribute('download', `simulation_report_${simulationId}.${extension}`);
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success(`${format.toUpperCase()}报告下载成功`);
    } catch (error) {
      message.error('下载报告失败');
    }
  };

  const handlePreviewReport = async (simulationId) => {
    try {
      const response = await axios.get(`/api/v1/reports/generate/${simulationId}?format=html`);
      
      // 在新窗口中打开HTML报告
      const newWindow = window.open('', '_blank');
      newWindow.document.write(response.data);
      newWindow.document.close();
    } catch (error) {
      message.error('预览报告失败');
    }
  };

  const getStatusTag = (status) => {
    const statusConfig = {
      running: { color: 'processing', text: '运行中' },
      completed: { color: 'success', text: '已完成' },
      error: { color: 'error', text: '错误' },
      stopped: { color: 'warning', text: '已停止' }
    };
    
    const config = statusConfig[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getActionMenu = (record) => (
    <Menu>
      <Menu.Item
        key="preview"
        icon={<EyeOutlined />}
        onClick={() => handlePreviewReport(record.simulation_id)}
        disabled={record.status !== 'completed'}
      >
        预览报告
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item
        key="html"
        icon={<FileTextOutlined />}
        onClick={() => handleDownloadReport(record.simulation_id, 'html')}
        disabled={record.status !== 'completed'}
      >
        下载HTML
      </Menu.Item>
      <Menu.Item
        key="excel"
        icon={<FileExcelOutlined />}
        onClick={() => handleDownloadReport(record.simulation_id, 'excel')}
        disabled={record.status !== 'completed'}
      >
        下载Excel
      </Menu.Item>
      <Menu.Item
        key="json"
        icon={<FilePdfOutlined />}
        onClick={() => handleDownloadReport(record.simulation_id, 'json')}
        disabled={record.status !== 'completed'}
      >
        下载JSON
      </Menu.Item>
    </Menu>
  );

  const columns = [
    {
      title: '模拟ID',
      dataIndex: 'simulation_id',
      key: 'simulation_id',
      width: 120,
      render: (text) => (
        <Text code style={{ fontSize: '12px' }}>
          {text?.slice(0, 8)}...
        </Text>
      )
    },
    {
      title: '游戏名称',
      dataIndex: 'game_name',
      key: 'game_name',
      width: 150
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status)
    },
    {
      title: '轮数',
      dataIndex: 'total_rounds',
      key: 'total_rounds',
      width: 100,
      render: (value) => value?.toLocaleString()
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 160,
      render: (text) => text ? new Date(text).toLocaleString() : '-'
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
      width: 160,
      render: (text) => text ? new Date(text).toLocaleString() : '-'
    },
    {
      title: '耗时',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (duration) => {
        if (!duration) return '-';
        if (duration < 60) return `${duration.toFixed(1)}秒`;
        if (duration < 3600) return `${(duration / 60).toFixed(1)}分钟`;
        return `${(duration / 3600).toFixed(1)}小时`;
      }
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownloadReport(record.simulation_id, 'html')}
            disabled={record.status !== 'completed'}
          >
            下载
          </Button>
          <Dropdown
            overlay={getActionMenu(record)}
            trigger={['click']}
            disabled={record.status !== 'completed'}
          >
            <Button size="small" icon={<MoreOutlined />} />
          </Dropdown>
        </Space>
      )
    }
  ];

  const reportFormats = [
    {
      key: 'html',
      name: 'HTML报告',
      description: '包含图表的完整网页报告',
      icon: <FileTextOutlined style={{ fontSize: '24px', color: '#1890ff' }} />,
      features: ['交互式图表', '完整样式', '可直接查看']
    },
    {
      key: 'excel',
      name: 'Excel报告',
      description: '数据表格格式，便于进一步分析',
      icon: <FileExcelOutlined style={{ fontSize: '24px', color: '#52c41a' }} />,
      features: ['数据表格', '便于分析', '支持公式']
    },
    {
      key: 'json',
      name: 'JSON数据',
      description: '原始数据格式，便于程序处理',
      icon: <FilePdfOutlined style={{ fontSize: '24px', color: '#722ed1' }} />,
      features: ['原始数据', '程序友好', '结构化']
    }
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={1}>报告管理</Title>
        <Text>管理和下载模拟报告</Text>
      </div>

      {/* 报告格式说明 */}
      <Card title="报告格式" style={{ marginBottom: 24 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          {reportFormats.map(format => (
            <Card
              key={format.key}
              size="small"
              style={{ textAlign: 'center' }}
            >
              <Space direction="vertical" size="middle">
                {format.icon}
                <div>
                  <Title level={5} style={{ margin: 0 }}>
                    {format.name}
                  </Title>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {format.description}
                  </Text>
                </div>
                <div>
                  {format.features.map(feature => (
                    <Tag key={feature} size="small">
                      {feature}
                    </Tag>
                  ))}
                </div>
              </Space>
            </Card>
          ))}
        </div>
      </Card>

      {/* 模拟列表 */}
      <Card title="模拟记录">
        <Table
          dataSource={simulations}
          columns={columns}
          rowKey="simulation_id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`
          }}
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* 使用说明 */}
      <Card title="使用说明" style={{ marginTop: 24 }}>
        <div>
          <Title level={5}>报告内容</Title>
          <ul>
            <li><strong>汇总统计</strong>: 总投注金额、总派奖金额、平均RTP等关键指标</li>
            <li><strong>奖级分析</strong>: 各奖级中奖人数、奖金分布、概率统计</li>
            <li><strong>趋势图表</strong>: RTP变化趋势、奖池变化、中奖分布等可视化图表</li>
            <li><strong>详细数据</strong>: 每轮模拟的详细数据记录</li>
          </ul>
          
          <Title level={5}>下载建议</Title>
          <ul>
            <li><strong>HTML格式</strong>: 适合查看和展示，包含完整的图表和样式</li>
            <li><strong>Excel格式</strong>: 适合数据分析，可以进行进一步的计算和处理</li>
            <li><strong>JSON格式</strong>: 适合程序处理，包含完整的原始数据</li>
          </ul>
        </div>
      </Card>
    </div>
  );
};

export default ReportsPage;
