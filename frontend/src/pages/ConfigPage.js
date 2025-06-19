import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  Switch,
  Button,
  Space,
  Row,
  Col,
  Divider,
  message,
  Tabs,
  Table,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  SaveOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;
const { TabPane } = Tabs;

const ConfigPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState({});
  const [savedConfigs, setSavedConfigs] = useState([]);
  const [activeTab, setActiveTab] = useState('1');
  const [prizelevels, setPrizeLevels] = useState([
    {
      level: 1,
      name: '一等奖',
      match_condition: 6,
      fixed_prize: null,
      prize_percentage: 0.9
    }
  ]);

  useEffect(() => {
    fetchTemplates();
    fetchSavedConfigs();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await axios.get('/api/v1/config/templates');
      setTemplates(response.data.templates);
    } catch (error) {
      message.error('获取模板失败');
    }
  };

  const fetchSavedConfigs = async () => {
    try {
      const response = await axios.get('/api/v1/config/list');
      setSavedConfigs(response.data.configs);
    } catch (error) {
      message.error('获取配置列表失败');
    }
  };

  const handleTemplateSelect = (templateKey) => {
    const template = templates[templateKey];
    if (template) {
      form.setFieldsValue(template);
      setPrizeLevels(template.game_rules.prize_levels);
      message.success(`已加载模板: ${template.name}`);
    }
  };

  const handleAddPrizeLevel = () => {
    const newLevel = {
      level: prizelevels.length + 1,
      name: `${prizelevels.length + 1}等奖`,
      match_condition: Math.max(1, 6 - prizelevels.length),
      fixed_prize: 100,
      prize_percentage: null
    };
    setPrizeLevels([...prizelevels, newLevel]);
  };

  const handleRemovePrizeLevel = (index) => {
    const newLevels = prizelevels.filter((_, i) => i !== index);
    setPrizeLevels(newLevels);
  };

  const handlePrizeLevelChange = (index, field, value) => {
    const newLevels = [...prizelevels];
    newLevels[index] = { ...newLevels[index], [field]: value };
    setPrizeLevels(newLevels);
  };

  const handleSaveConfig = async (values) => {
    setLoading(true);
    try {
      const configData = {
        ...values,
        game_rules: {
          ...values.game_rules,
          prize_levels: prizelevels
        }
      };

      const configName = values.config_name || `config_${Date.now()}`;
      await axios.post(`/api/v1/config/save?config_name=${configName}`, configData);
      
      message.success('配置保存成功');
      fetchSavedConfigs();
    } catch (error) {
      message.error('保存配置失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleLoadConfig = async (configName) => {
    try {
      const response = await axios.get(`/api/v1/config/load/${configName}`);
      const config = response.data.config;

      form.setFieldsValue(config);
      setPrizeLevels(config.game_rules.prize_levels);

      // 切换到编辑标签页
      setActiveTab('1');

      message.success(`已加载配置: ${configName}，可以开始编辑`);
    } catch (error) {
      message.error('加载配置失败');
    }
  };

  const handleDeleteConfig = async (configName) => {
    try {
      await axios.delete(`/api/v1/config/delete/${configName}`);
      message.success('配置删除成功');
      fetchSavedConfigs();
    } catch (error) {
      message.error('删除配置失败');
    }
  };

  const prizeColumns = [
    {
      title: '等级',
      dataIndex: 'level',
      width: 80,
      render: (_, record, index) => (
        <InputNumber
          min={1}
          value={record.level}
          onChange={(value) => handlePrizeLevelChange(index, 'level', value)}
        />
      )
    },
    {
      title: '名称',
      dataIndex: 'name',
      render: (_, record, index) => (
        <Input
          value={record.name}
          onChange={(e) => handlePrizeLevelChange(index, 'name', e.target.value)}
        />
      )
    },
    {
      title: '匹配条件',
      dataIndex: 'match_condition',
      width: 120,
      render: (_, record, index) => (
        <InputNumber
          min={0}
          value={record.match_condition}
          onChange={(value) => handlePrizeLevelChange(index, 'match_condition', value)}
        />
      )
    },
    {
      title: '固定奖金',
      dataIndex: 'fixed_prize',
      width: 120,
      render: (_, record, index) => (
        <InputNumber
          min={0}
          value={record.fixed_prize}
          onChange={(value) => handlePrizeLevelChange(index, 'fixed_prize', value)}
          placeholder="留空使用奖池"
        />
      )
    },
    {
      title: '奖池比例',
      dataIndex: 'prize_percentage',
      width: 120,
      render: (_, record, index) => (
        <InputNumber
          min={0}
          max={1}
          step={0.1}
          value={record.prize_percentage}
          onChange={(value) => handlePrizeLevelChange(index, 'prize_percentage', value)}
          placeholder="仅最高奖级"
        />
      )
    },
    {
      title: '操作',
      width: 80,
      render: (_, record, index) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleRemovePrizeLevel(index)}
          disabled={prizelevels.length <= 1}
        />
      )
    }
  ];

  const configColumns = [
    {
      title: '配置名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '显示名称',
      dataIndex: 'display_name',
      key: 'display_name'
    },
    {
      title: '游戏类型',
      dataIndex: 'game_type',
      key: 'game_type'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => text ? new Date(text).toLocaleString() : '-'
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            onClick={() => handleLoadConfig(record.name)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此配置吗？"
            onConfirm={() => handleDeleteConfig(record.name)}
          >
            <Button type="link" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div className="page-header">
        <h1>游戏配置</h1>
        <p>设置游戏规则、奖级配置和模拟参数</p>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="配置编辑" key="1">
          <Card title="配置模板" style={{ marginBottom: 24 }}>
            <Space wrap>
              {Object.entries(templates).map(([key, template]) => (
                <Button
                  key={key}
                  onClick={() => handleTemplateSelect(key)}
                >
                  {template.name}
                </Button>
              ))}
            </Space>
          </Card>

          <Form
            form={form}
            layout="vertical"
            onFinish={handleSaveConfig}
            initialValues={{
              game_rules: {
                game_type: 'lottery',
                number_range: [1, 42],
                selection_count: 6,
                ticket_price: 20
              },
              simulation_config: {
                rounds: 1000,
                players_range: [50000, 100000],
                bets_range: [5, 15]
              }
            }}
          >
            <Card title="基本信息" style={{ marginBottom: 24 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="config_name"
                    label="配置名称"
                    rules={[{ required: true, message: '请输入配置名称' }]}
                  >
                    <Input placeholder="输入配置名称" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name={['game_rules', 'game_type']}
                    label="游戏类型"
                    rules={[{ required: true }]}
                  >
                    <Select>
                      <Option value="lottery">彩票</Option>
                      <Option value="scratch">刮刮乐</Option>
                      <Option value="slot">老虎机</Option>
                      <Option value="custom">自定义</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name={['game_rules', 'name']}
                    label="游戏名称"
                    rules={[{ required: true }]}
                  >
                    <Input placeholder="输入游戏名称" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name={['game_rules', 'ticket_price']}
                    label="单注价格"
                    rules={[{ required: true }]}
                  >
                    <InputNumber
                      min={0.01}
                      step={0.01}
                      style={{ width: '100%' }}
                      placeholder="单注价格"
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            <Card title="游戏规则" style={{ marginBottom: 24 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name={['game_rules', 'number_range', 0]}
                    label="数字范围 - 最小值"
                    rules={[{ required: true }]}
                  >
                    <InputNumber min={1} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name={['game_rules', 'number_range', 1]}
                    label="数字范围 - 最大值"
                    rules={[{ required: true }]}
                  >
                    <InputNumber min={1} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name={['game_rules', 'selection_count']}
                    label="选择数量"
                    rules={[{ required: true }]}
                  >
                    <InputNumber min={1} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            <Card 
              title="奖级配置" 
              style={{ marginBottom: 24 }}
              extra={
                <Button
                  type="dashed"
                  icon={<PlusOutlined />}
                  onClick={handleAddPrizeLevel}
                >
                  添加奖级
                </Button>
              }
            >
              <Table
                dataSource={prizelevels}
                columns={prizeColumns}
                pagination={false}
                rowKey="level"
                size="small"
              />
            </Card>

            <Card title="奖池设置" style={{ marginBottom: 24 }}>
              <Form.Item
                name={['game_rules', 'jackpot', 'enabled']}
                label="启用奖池"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Row gutter={16}>
                <Col span={6}>
                  <Form.Item
                    name={['game_rules', 'jackpot', 'initial_amount']}
                    label="初始奖池金额"
                  >
                    <InputNumber
                      min={0}
                      style={{ width: '100%' }}
                      placeholder="初始奖池金额"
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    name={['game_rules', 'jackpot', 'contribution_rate']}
                    label="第一阶段注入比例"
                    tooltip="销售方返还期间的奖池注入比例"
                  >
                    <InputNumber
                      min={0}
                      max={1}
                      step={0.01}
                      style={{ width: '100%' }}
                      placeholder="0.15"
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    name={['game_rules', 'jackpot', 'post_return_contribution_rate']}
                    label="第二阶段注入比例"
                    tooltip="销售方返还完成后的奖池注入比例"
                  >
                    <InputNumber
                      min={0}
                      max={1}
                      step={0.01}
                      style={{ width: '100%' }}
                      placeholder="0.3"
                    />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    name={['game_rules', 'jackpot', 'return_rate']}
                    label="销售方返还比例"
                  >
                    <InputNumber
                      min={0}
                      max={1}
                      step={0.01}
                      style={{ width: '100%' }}
                      placeholder="0.9"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name={['game_rules', 'jackpot', 'jackpot_fixed_prize']}
                    label="头奖固定奖金（可选）"
                  >
                    <InputNumber
                      min={0}
                      style={{ width: '100%' }}
                      placeholder="留空则只分配奖池"
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name={['game_rules', 'jackpot', 'min_jackpot']}
                    label="最小奖池保底金额"
                  >
                    <InputNumber
                      min={0}
                      style={{ width: '100%' }}
                      placeholder="最小奖池金额"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <div style={{ background: '#f6f8fa', padding: '12px', borderRadius: '6px', marginTop: '16px' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#24292e' }}>奖池规则说明：</h4>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#586069' }}>
                  <li><strong>第一阶段（销售方返还期间）</strong>：</li>
                  <ul style={{ paddingLeft: '20px' }}>
                    <li>总下注金额 = 奖池注入 + 销售方返还 + 销售金额</li>
                    <li>奖池注入：每注投注金额 × 第一阶段注入比例</li>
                    <li>销售方返还：每注投注金额 × 销售方返还比例（补偿垫付的初始奖池）</li>
                    <li>销售金额：剩余部分（总下注金额 - 奖池注入 - 销售方返还）</li>
                  </ul>
                  <li><strong>阶段转换</strong>：当累计返还给销售方的金额达到初始奖池金额后，停止返还，进入第二阶段</li>
                  <li><strong>第二阶段（返还完成后）</strong>：</li>
                  <ul style={{ paddingLeft: '20px' }}>
                    <li>总下注金额 = 奖池注入 + 销售金额</li>
                    <li>奖池注入：每注投注金额 × 第二阶段注入比例</li>
                    <li>销售金额：剩余部分（总下注金额 - 奖池注入）</li>
                  </ul>
                  <li><strong>头奖分配</strong>：如果设置了固定奖金，则为(奖池金额÷中奖人数)+固定奖金；如果未设置固定奖金，则为奖池金额÷中奖人数</li>
                  <li><strong>奖池重置</strong>：每次有玩家中头奖后，奖池会重新初始化为初始奖池金额，销售方返还状态也会重置，重新开始分阶段逻辑</li>
                </ul>
              </div>
            </Card>

            <Card title="模拟配置" style={{ marginBottom: 24 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name={['simulation_config', 'rounds']}
                    label="模拟轮数"
                    rules={[{ required: true }]}
                  >
                    <InputNumber
                      min={1}
                      max={10000000}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name={['simulation_config', 'players_range', 0]}
                    label="玩家数 - 最小值"
                    rules={[{ required: true }]}
                  >
                    <InputNumber min={1} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name={['simulation_config', 'players_range', 1]}
                    label="玩家数 - 最大值"
                    rules={[{ required: true }]}
                  >
                    <InputNumber min={1} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name={['simulation_config', 'bets_range', 0]}
                    label="投注数 - 最小值"
                    rules={[{ required: true }]}
                  >
                    <InputNumber min={1} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name={['simulation_config', 'bets_range', 1]}
                    label="投注数 - 最大值"
                    rules={[{ required: true }]}
                  >
                    <InputNumber min={1} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name={['simulation_config', 'seed']}
                    label="随机种子（可选）"
                  >
                    <InputNumber style={{ width: '100%' }} placeholder="留空随机" />
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            <div style={{ textAlign: 'center' }}>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
                size="large"
              >
                保存配置
              </Button>
            </div>
          </Form>
        </TabPane>

        <TabPane tab="已保存配置" key="2">
          <Card>
            <Table
              dataSource={savedConfigs}
              columns={configColumns}
              rowKey="name"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ConfigPage;
