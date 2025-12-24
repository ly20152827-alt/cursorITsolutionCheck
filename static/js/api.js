// API调用模块
// 根据当前环境自动设置API基础URL
const API_BASE_URL = (() => {
    // 如果是Vercel部署环境，使用相对路径
    if (window.location.hostname.includes('vercel.app') || window.location.hostname.includes('vercel.com')) {
        return ''; // 使用相对路径，自动使用当前域名
    }
    // 本地开发环境
    return 'http://localhost:8000';
})();

class API {
    static async request(endpoint, options = {}) {
        // 确保endpoint以/开头
        const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        const url = API_BASE_URL ? `${API_BASE_URL}${normalizedEndpoint}` : normalizedEndpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            
            // 检查响应状态
            if (!response.ok) {
                // 尝试解析JSON错误响应
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    // 如果无法解析JSON，返回文本错误
                    const text = await response.text();
                    throw new Error(`服务器错误 (${response.status}): ${text.substring(0, 100)}`);
                }
                throw new Error(errorData.detail || errorData.message || `请求失败 (${response.status})`);
            }
            
            // 尝试解析JSON响应
            let data;
            try {
                data = await response.json();
            } catch (e) {
                // 如果响应不是JSON，返回文本
                const text = await response.text();
                throw new Error(`响应格式错误: ${text.substring(0, 100)}`);
            }
            
            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            console.error('请求URL:', url);
            console.error('请求配置:', config);
            throw error;
        }
    }

    // 创建项目
    static async createProject(name, projectType = '施工前期') {
        return await this.request('/api/projects', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                project_type: projectType
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    // 获取项目列表
    static async getProjects() {
        return await this.request('/api/projects');
    }

    // 上传文档
    static async uploadDocument(projectId, file) {
        const formData = new FormData();
        formData.append('file', file);
        
        return await this.request(`/api/projects/${projectId}/documents/upload`, {
            method: 'POST',
            body: formData,
            headers: {} // 让浏览器自动设置Content-Type
        });
    }

    // 解析文档
    static async parseDocument(documentId) {
        return await this.request(`/api/documents/${documentId}/parse`, {
            method: 'POST'
        });
    }

    // 审核文档
    static async reviewDocument(documentId, useAi = true) {
        const params = new URLSearchParams({
            use_ai: useAi
        });
        return await this.request(`/api/documents/${documentId}/review?${params}`, {
            method: 'POST'
        });
    }

    // 获取审核报告
    static async getReport(reviewId, format = 'json') {
        const params = new URLSearchParams({
            format: format
        });
        return await this.request(`/api/reviews/${reviewId}/report?${params}`);
    }

    // 获取项目的审核记录
    static async getProjectReviews(projectId) {
        return await this.request(`/api/projects/${projectId}/reviews`);
    }

    // 获取审核要点库
    static async getReviewPoints() {
        return await this.request('/api/review-points');
    }

    // 获取AI模型列表
    static async getAIModels() {
        return await this.request('/api/ai-models');
    }

    // 上传审核规范
    static async uploadStandard(file, name, category) {
        const formData = new FormData();
        formData.append('file', file);
        if (name) formData.append('name', name);
        if (category) formData.append('category', category);
        
        return await this.request('/api/review-standards/upload', {
            method: 'POST',
            body: formData,
            headers: {}
        });
    }

    // 获取审核规范列表
    static async getStandards() {
        return await this.request('/api/review-standards');
    }

    // 从规范生成规则
    static async generateRulesFromStandard(standardId, modelName, apiKey) {
        const params = new URLSearchParams({
            model_name: modelName
        });
        if (apiKey) params.append('api_key', apiKey);
        
        return await this.request(`/api/review-standards/${standardId}/generate-rules?${params}`, {
            method: 'POST'
        });
    }

    // 获取规范的规则列表
    static async getStandardRules(standardId) {
        return await this.request(`/api/review-standards/${standardId}/rules`);
    }

    // 创建规则
    static async createRule(ruleData) {
        return await this.request('/api/review-rules', {
            method: 'POST',
            body: JSON.stringify(ruleData),
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    // 更新规则
    static async updateRule(ruleId, ruleData) {
        return await this.request(`/api/review-rules/${ruleId}`, {
            method: 'PUT',
            body: JSON.stringify(ruleData),
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    // 删除规则
    static async deleteRule(ruleId) {
        return await this.request(`/api/review-rules/${ruleId}`, {
            method: 'DELETE'
        });
    }
}
