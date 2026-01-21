# AI Stock Assistant (AI 股票助手)

这是一个带有自反思能力的AI股票助手网页应用，集成了持仓分析、个股查询和经验库管理功能。

## 项目结构

```
stock_assistant/
├── backend/           # Flask 后端 (Python)
│   ├── app.py         # 主应用程序入口
│   ├── supabase_client.py # Supabase 客户端配置
│   ├── services.py    # 业务逻辑与Mock服务
│   ├── .env           # 环境变量 (Supabase 配置)
│   └── requirements.txt # Python依赖
├── frontend/          # Vue 3 前端 (Node.js)
│   ├── src/           # 源代码
│   ├── vite.config.js # Vite配置
│   └── package.json   # 前端依赖
├── supabase/          # Supabase 配置
│   └── migrations/    # 数据库迁移文件
├── data/              # 数据备份目录
├── vercel.json        # Vercel 部署配置
└── README.md          # 本文档
```

## 快速开始

### 1. 环境准备

确保您的系统已安装：
- **Node.js** (v16+)
- **Python** (v3.8+)

### 2. 后端启动 (Backend)

进入 `stock_assistant` 目录：

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 启动服务 (默认端口 5000)
python backend/app.py
```

注意：后端已配置为连接 Supabase 数据库。请确保 `backend/.env` 文件中包含正确的 `SUPABASE_URL` 和 `SUPABASE_KEY`。

### 3. 前端启动 (Frontend)

新开一个终端窗口，进入 `stock_assistant/frontend` 目录：

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问浏览器: `http://localhost:5173`

## 部署 (Vercel)

本项目已配置 `vercel.json`，支持一键部署到 Vercel。

1. **推送代码**: 将代码推送到 GitHub。
2. **导入项目**: 在 Vercel 中导入该仓库。
3. **配置变量**: 在 Vercel 项目设置 -> Environment Variables 中添加：
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
4. **重新部署**: 保存变量后，重新部署一次以生效。

详细部署说明请参考 [DEPLOY.md](DEPLOY.md)。

## 功能说明

1. **持仓分析**: 每日自动分析持仓股票（模拟数据），提供评分和建议。
2. **股票查询**: 输入股票代码查询实时分析结果。
3. **经验库**: 管理您的投资经验规则，系统会自动匹配并提示风险。
   - 数据存储于云端 Supabase 数据库。
   - 支持 JSON 格式的本地备份与导入。
