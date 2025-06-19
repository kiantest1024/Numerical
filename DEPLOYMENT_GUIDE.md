# @numericalTools 部署指南

## 🎯 部署概述

本指南提供了 @numericalTools 在不同环境下的完整部署方案，包括开发环境、测试环境和生产环境。

## 🐳 Docker部署（推荐）

### 前置要求
- Docker 20.0+
- Docker Compose 2.0+
- 至少4GB可用内存
- 至少2GB可用磁盘空间

### 快速部署
```bash
# 1. 克隆项目
git clone <repository-url>
cd numericalTools

# 2. 启动所有服务
docker-compose up -d

# 3. 检查服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

### 服务访问
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

## 💻 本地开发部署

### 后端部署

#### 1. 环境准备
```bash
# Python 3.8+ 环境
python --version

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

#### 2. 安装依赖
```bash
cd numericalTools/backend
pip install -r requirements.txt
```

#### 3. 启动服务
```bash
# 方法1: 使用启动脚本
python run.py

# 方法2: 直接使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 4. 验证部署
```bash
# 测试API
curl http://localhost:8001/health

# 运行测试
python test_backend.py
```

### 前端部署

#### 1. 环境准备
```bash
# Node.js 16+ 环境
node --version
npm --version
```

#### 2. 安装依赖
```bash
cd numericalTools/frontend
npm install
```

#### 3. 启动开发服务器
```bash
npm start
```

#### 4. 构建生产版本
```bash
npm run build
```

## 🏭 生产环境部署

### 系统要求
- **CPU**: 4核心以上
- **内存**: 8GB以上
- **存储**: 50GB以上SSD
- **网络**: 稳定的网络连接
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+

### 生产环境配置

#### 1. 环境变量配置
创建 `.env` 文件：
```bash
# 应用配置
APP_NAME=@numericalTools
APP_VERSION=1.0.0
DEBUG=False

# 服务器配置
HOST=0.0.0.0
PORT=8001

# 数据库配置（可选）
DATABASE_URL=postgresql://user:password@localhost:5432/numerical_tools

# 安全配置
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 性能配置
MAX_SIMULATION_ROUNDS=10000000
MAX_CONCURRENT_SIMULATIONS=10
DEFAULT_TIMEOUT=600

# 文件存储
UPLOAD_DIR=/app/data/uploads
REPORTS_DIR=/app/data/reports
TEMP_DIR=/app/data/temp
```

#### 2. Docker Compose生产配置
创建 `docker-compose.prod.yml`：
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: numerical-tools-backend-prod
    ports:
      - "8001:8001"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/numerical_tools
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: numerical-tools-frontend-prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped
    depends_on:
      - backend

  db:
    image: postgres:14
    container_name: numerical-tools-db
    environment:
      - POSTGRES_DB=numerical_tools
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: numerical-tools-redis
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: numerical-tools-prod-network
```

#### 3. Nginx配置
创建 `nginx/nginx.conf`：
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8001;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
        
        # API代理
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # 健康检查
        location /health {
            proxy_pass http://backend;
        }
    }
}
```

### 部署步骤

#### 1. 服务器准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 项目部署
```bash
# 克隆项目
git clone <repository-url>
cd numericalTools

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. SSL证书配置
```bash
# 使用Let's Encrypt（推荐）
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/key.pem
```

## 🔧 配置管理

### 环境配置
- **开发环境**: 启用调试，使用SQLite数据库
- **测试环境**: 模拟生产配置，使用PostgreSQL
- **生产环境**: 优化性能，启用所有安全特性

### 数据库配置
```python
# 开发环境
DATABASE_URL = "sqlite:///./numerical_tools.db"

# 生产环境
DATABASE_URL = "postgresql://user:password@localhost:5432/numerical_tools"
```

### 缓存配置
```python
# Redis缓存配置
REDIS_URL = "redis://localhost:6379/0"
CACHE_TTL = 3600  # 1小时
```

## 📊 监控和日志

### 应用监控
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### 日志配置
```python
# logging.conf
[loggers]
keys=root,numerical_tools

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_numerical_tools]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=numerical_tools
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=simpleFormatter
args=('/app/logs/numerical_tools.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🔒 安全配置

### 防火墙设置
```bash
# Ubuntu UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 应用安全
- 使用强密码和密钥
- 启用HTTPS
- 配置CORS策略
- 实施访问控制
- 定期更新依赖

## 🚀 性能优化

### 生产环境优化
```yaml
# docker-compose.prod.yml 性能配置
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    environment:
      - WORKERS=4
      - MAX_REQUESTS=1000
      - MAX_REQUESTS_JITTER=100
```

### 数据库优化
```sql
-- PostgreSQL优化
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
```

## 🔄 备份和恢复

### 数据备份
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"

# 数据库备份
docker exec numerical-tools-db pg_dump -U postgres numerical_tools > $BACKUP_DIR/db_$DATE.sql

# 文件备份
tar -czf $BACKUP_DIR/data_$DATE.tar.gz ./data

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 自动备份
```bash
# 添加到crontab
0 2 * * * /path/to/backup.sh
```

## 📋 部署检查清单

### 部署前检查
- [ ] 服务器资源充足
- [ ] 域名和DNS配置正确
- [ ] SSL证书准备就绪
- [ ] 环境变量配置完成
- [ ] 数据库连接测试通过

### 部署后验证
- [ ] 所有服务正常启动
- [ ] 健康检查通过
- [ ] API功能测试通过
- [ ] 前端界面正常访问
- [ ] 日志记录正常
- [ ] 监控指标正常

### 安全检查
- [ ] 防火墙配置正确
- [ ] HTTPS正常工作
- [ ] 敏感信息已保护
- [ ] 访问控制生效
- [ ] 备份策略已实施

---

通过以上部署指南，您可以在各种环境中成功部署 @numericalTools 系统。如有问题，请参考故障排除文档或联系技术支持。
