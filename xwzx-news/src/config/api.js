/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
}

export const aiChatConfig = {
  // OpenAI API地址
  apiEndpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
  
  // 仅用于本地开发；生产环境应由后端代理 AI 请求，避免密钥暴露在浏览器中
  apiKey: import.meta.env.VITE_AI_API_KEY || '',
  
  // 使用的模型
  model: 'qwen3-max-preview'
}
