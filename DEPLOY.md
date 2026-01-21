
## 部署 (Deployment)

### Vercel 部署

本项目支持直接部署到 Vercel。由于是前后端分离项目（Python Flask + Vue 3），我们已配置了 `vercel.json` 以支持混合部署。

1. **准备工作**:
   - 确保将项目推送到 GitHub/GitLab。
   - 在 Vercel 控制台导入项目。

2. **环境变量配置**:
   在 Vercel 项目设置 (Settings -> Environment Variables) 中添加以下变量：
   - `SUPABASE_URL`: 您的 Supabase 项目 URL
   - `SUPABASE_KEY`: 您的 Supabase Service Role Key (或 Anon Key，后端建议用 Service Key)

3. **部署**:
   - Vercel 会自动识别 `vercel.json` 并进行构建。
   - 前端静态文件将由 Vercel CDN 托管。
   - 后端 API 将作为 Serverless Functions 运行。

### 本地开发

参见上方 "快速开始" 章节。
