import React from 'react';
import { Layout as AntLayout, Menu, Typography } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  BarChartOutlined,
  FileTextOutlined
} from '@ant-design/icons';

const { Header, Content, Sider } = AntLayout;
const { Title } = Typography;

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/config',
      icon: <SettingOutlined />,
      label: '游戏配置',
    },
    {
      key: '/simulation',
      icon: <PlayCircleOutlined />,
      label: '运行模拟',
    },
    {
      key: '/results',
      icon: <BarChartOutlined />,
      label: '结果分析',
    },
    {
      key: '/reports',
      icon: <FileTextOutlined />,
      label: '报告管理',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: '#001529', 
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center'
      }}>
        <Title 
          level={3} 
          style={{ 
            color: 'white', 
            margin: 0,
            fontWeight: 'bold'
          }}
        >
          @numericalTools
        </Title>
        <span style={{ 
          color: '#8c8c8c', 
          marginLeft: '16px',
          fontSize: '14px'
        }}>
          通用数值模拟验证工具
        </span>
      </Header>
      
      <AntLayout>
        <Sider 
          width={200} 
          style={{ background: '#fff' }}
          breakpoint="lg"
          collapsedWidth="0"
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>
        
        <AntLayout style={{ padding: '0' }}>
          <Content className="main-content">
            {children}
          </Content>
        </AntLayout>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
