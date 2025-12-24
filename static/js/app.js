// 主应用逻辑
let currentProjectId = null;
let currentReviewId = null;
let projects = [];

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    loadProjects();
    setupEventListeners();
});

// 设置事件监听
function setupEventListeners() {
    // 上传表单提交
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    // 创建项目表单提交
    const createProjectForm = document.getElementById('create-project-form');
    if (createProjectForm) {
        createProjectForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createProject();
        });
    }
}

// 显示首页
function showHome() {
    hideAllSections();
    document.getElementById('home-section').classList.remove('d-none');
    updateNavActive('home');
}

// 显示项目管理
function showProjects() {
    hideAllSections();
    document.getElementById('projects-section').classList.remove('d-none');
    loadProjects();
    updateNavActive('projects');
}

// 显示上传页面
function showUpload() {
    hideAllSections();
    document.getElementById('upload-section').classList.remove('d-none');
    loadProjectsForSelect();
    updateNavActive('upload');
}

// 显示审核要点库
function showReviewPoints() {
    hideAllSections();
    document.getElementById('review-points-section').classList.remove('d-none');
    loadReviewPoints();
    loadAIModels();
    loadStandards();
    updateNavActive('review-points');
}

// 隐藏所有内容区
function hideAllSections() {
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('d-none');
    });
}

// 更新导航激活状态
function updateNavActive(active) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.textContent.includes(getNavText(active))) {
            link.classList.add('active');
        }
    });
}

function getNavText(active) {
    const map = {
        'home': '首页',
        'projects': '项目管理',
        'upload': '上传文档',
        'review-points': '审核要点库'
    };
    return map[active] || '';
}

// 加载项目列表
async function loadProjects() {
    const tbody = document.getElementById('projects-table-body');
    if (!tbody) {
        console.error('项目表格元素未找到');
        return;
    }
    
    tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="loading-spinner"></div> 加载中...</td></tr>';
    
    try {
        const result = await API.getProjects();
        console.log('获取项目列表结果:', result);
        
        if (result && result.code === 200) {
            projects = result.data || [];
            console.log('项目数量:', projects.length);
            
            // 同时更新本地存储
            const projectsForStorage = projects.map(p => ({
                id: p.project_id,
                name: p.name,
                type: p.project_type,
                status: p.status,
                createTime: p.create_time ? new Date(p.create_time).toLocaleString('zh-CN') : '-'
            }));
            localStorage.setItem('projects', JSON.stringify(projectsForStorage));
            
            if (projects.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">暂无项目，请创建新项目</td></tr>';
            } else {
                tbody.innerHTML = projects.map(project => {
                    const createTime = project.create_time ? 
                        new Date(project.create_time).toLocaleString('zh-CN') : '-';
                    return `
                        <tr>
                            <td>${project.project_id}</td>
                            <td>${project.name}</td>
                            <td>${project.project_type || '施工前期'}</td>
                            <td><span class="status-badge status-pending">${project.status || '待审核'}</span></td>
                            <td>${createTime}</td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="selectProject(${project.project_id})">
                                    <i class="bi bi-check"></i> 选择
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('');
            }
        } else {
            console.error('获取项目列表失败:', result);
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">获取项目列表失败</td></tr>';
        }
    } catch (error) {
        console.error('加载项目失败:', error);
        showAlert('加载项目失败: ' + error.message, 'danger');
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">加载失败: ' + error.message + '</td></tr>';
    }
}

// 加载项目到选择框
async function loadProjectsForSelect() {
    const select = document.getElementById('project-select');
    select.innerHTML = '<option value="">请选择项目...</option>';
    
    try {
        const result = await API.getProjects();
        if (result.code === 200) {
            projects = result.data || [];
            projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project.project_id;
                option.textContent = `${project.name} (${project.project_type || '施工前期'})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载项目失败:', error);
        // 如果API失败，尝试使用本地存储
        const storedProjects = localStorage.getItem('projects');
        if (storedProjects) {
            const localProjects = JSON.parse(storedProjects);
            localProjects.forEach(project => {
                const option = document.createElement('option');
                option.value = project.id;
                option.textContent = `${project.name} (${project.type || '施工前期'})`;
                select.appendChild(option);
            });
        }
    }
}

// 显示创建项目模态框
function showCreateProjectModal() {
    const modal = new bootstrap.Modal(document.getElementById('createProjectModal'));
    modal.show();
}

// 创建项目
async function createProject() {
    const name = document.getElementById('project-name').value.trim();
    const type = document.getElementById('project-type').value;
    
    if (!name) {
        showAlert('请输入项目名称', 'warning');
        return;
    }
    
    try {
        const result = await API.createProject(name, type);
        if (result.code === 200) {
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('createProjectModal'));
            modal.hide();
            
            // 重置表单
            document.getElementById('create-project-form').reset();
            
            // 显示成功消息
            showAlert('项目创建成功！', 'success');
            
            // 等待一下再刷新，确保数据已保存
            setTimeout(async () => {
                // 刷新项目列表（从服务器获取最新数据）
                await loadProjects();
                await loadProjectsForSelect();
            }, 300);
        }
    } catch (error) {
        showAlert('创建项目失败: ' + error.message, 'danger');
    }
}

// 选择项目
function selectProject(projectId) {
    currentProjectId = projectId;
    document.getElementById('project-select').value = projectId;
    showUpload();
}

// 处理文档上传
async function handleUpload(e) {
    e.preventDefault();
    
    const projectId = document.getElementById('project-select').value;
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!projectId) {
        showAlert('请先选择项目', 'warning');
        return;
    }
    
    if (!file) {
        showAlert('请选择要上传的文件', 'warning');
        return;
    }
    
    // 显示进度
    document.getElementById('review-progress').classList.remove('d-none');
    document.getElementById('review-result').classList.add('d-none');
    updateProgress(0, '上传文档中...');
    
    try {
        // 1. 上传文档
        updateProgress(20, '上传文档中...');
        const uploadResult = await API.uploadDocument(projectId, file);
        const documentId = uploadResult.data.document_id;
        
        // 2. 解析文档
        updateProgress(40, '解析文档中...');
        await API.parseDocument(documentId);
        
        // 3. 审核文档
        updateProgress(60, '审核文档中...');
        const reviewResult = await API.reviewDocument(documentId, true);
        currentReviewId = reviewResult.data.review_id;
        
        // 4. 显示结果
        updateProgress(100, '审核完成！');
        setTimeout(() => {
            showReviewResult(reviewResult.data);
        }, 500);
        
    } catch (error) {
        updateProgress(0, '审核失败: ' + error.message);
        showAlert('审核失败: ' + error.message, 'danger');
    }
}

// 更新进度
function updateProgress(percent, status) {
    const progressBar = document.getElementById('progress-bar');
    const statusText = document.getElementById('progress-status');
    
    progressBar.style.width = percent + '%';
    progressBar.textContent = percent + '%';
    statusText.textContent = status;
    
    if (percent === 100) {
        progressBar.classList.remove('progress-bar-animated');
    }
}

// 显示审核结果
function showReviewResult(data) {
    const score = data.score || 0;
    const issues = data.report.issues_list || [];
    
    // 统计问题
    let severeCount = 0;
    let generalCount = 0;
    let suggestionsCount = data.report.suggestions_list ? data.report.suggestions_list.length : 0;
    
    issues.forEach(category => {
        if (category.category === '严重问题') {
            severeCount = category.items.length;
        } else if (category.category === '一般问题') {
            generalCount = category.items.length;
        }
    });
    
    // 更新显示
    document.getElementById('review-score').textContent = score;
    document.getElementById('severe-issues').textContent = severeCount;
    document.getElementById('general-issues').textContent = generalCount;
    document.getElementById('suggestions-count').textContent = suggestionsCount;
    
    // 设置分数颜色
    const scoreElement = document.getElementById('review-score');
    scoreElement.className = 'text-primary';
    if (score >= 80) {
        scoreElement.className = 'text-success';
    } else if (score >= 60) {
        scoreElement.className = 'text-warning';
    } else {
        scoreElement.className = 'text-danger';
    }
    
    // 显示摘要
    const summary = data.report.review_summary || {};
    const summaryHtml = `
        <div class="alert alert-info">
            <h6><i class="bi bi-info-circle"></i> 审核摘要</h6>
            <p class="mb-0">${data.report.conclusion ? data.report.conclusion.description : '审核完成'}</p>
        </div>
    `;
    document.getElementById('review-summary').innerHTML = summaryHtml;
    
    // 显示结果区域
    document.getElementById('review-result').classList.remove('d-none');
}

// 查看完整报告
async function viewFullReport() {
    if (!currentReviewId) {
        showAlert('没有可查看的报告', 'warning');
        return;
    }
    
    try {
        const result = await API.getReport(currentReviewId, 'json');
        const report = result.data;
        
        // 生成报告HTML
        let reportHtml = `
            <div class="report-section">
                <h5><i class="bi bi-info-circle"></i> 报告基本信息</h5>
                <p><strong>项目名称：</strong>${report.report_info.project_name}</p>
                <p><strong>项目类型：</strong>${report.report_info.project_type}</p>
                <p><strong>生成时间：</strong>${report.report_info.generate_time}</p>
            </div>
            
            <div class="report-section">
                <h5><i class="bi bi-bar-chart"></i> 审核结果概览</h5>
                <div class="row">
                    <div class="col-md-3">
                        <p><strong>审核得分：</strong><span class="text-primary">${report.review_summary.score}分</span></p>
                    </div>
                    <div class="col-md-3">
                        <p><strong>严重问题：</strong><span class="text-danger">${report.review_summary.severe_issues}项</span></p>
                    </div>
                    <div class="col-md-3">
                        <p><strong>一般问题：</strong><span class="text-warning">${report.review_summary.general_issues}项</span></p>
                    </div>
                    <div class="col-md-3">
                        <p><strong>优化建议：</strong><span class="text-info">${report.review_summary.suggestions}项</span></p>
                    </div>
                </div>
            </div>
        `;
        
        // 问题清单
        if (report.issues_list && report.issues_list.length > 0) {
            reportHtml += `
                <div class="report-section">
                    <h5><i class="bi bi-exclamation-triangle"></i> 问题清单</h5>
            `;
            
            report.issues_list.forEach(category => {
                reportHtml += `<h6 class="mt-3">${category.category}</h6><ul class="issue-list">`;
                category.items.forEach((item, index) => {
                    const severityClass = item.severity === '严重' ? 'issue-severe' : 'issue-general';
                    reportHtml += `
                        <li class="${severityClass}">
                            <strong>${index + 1}. ${item.description || item.item || ''}</strong>
                            ${item.suggestion ? `<br><small class="text-muted">建议：${item.suggestion}</small>` : ''}
                        </li>
                    `;
                });
                reportHtml += `</ul>`;
            });
            
            reportHtml += `</div>`;
        }
        
        // 审核结论
        if (report.conclusion) {
            reportHtml += `
                <div class="report-section">
                    <h5><i class="bi bi-check-circle"></i> 审核结论</h5>
                    <p><strong>结论：</strong>${report.conclusion.conclusion}</p>
                    <p><strong>说明：</strong>${report.conclusion.description}</p>
                    ${report.conclusion.next_steps ? `
                        <h6>后续步骤：</h6>
                        <ul>
                            ${report.conclusion.next_steps.map(step => `<li>${step}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
        }
        
        // 显示模态框
        document.getElementById('report-content').innerHTML = reportHtml;
        const modal = new bootstrap.Modal(document.getElementById('reportModal'));
        modal.show();
        
    } catch (error) {
        showAlert('加载报告失败: ' + error.message, 'danger');
    }
}

// 显示提示消息
function showAlert(message, type = 'info') {
    // 创建提示元素
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 3秒后自动关闭
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// 审核要点库相关函数
let reviewPointsData = {};

// 加载审核要点库
async function loadReviewPoints() {
    try {
        const result = await API.getReviewPoints();
        if (result.code === 200) {
            reviewPointsData = result.data;
            renderChaptersList();
        }
    } catch (error) {
        console.error('加载审核要点库失败:', error);
        showAlert('加载审核要点库失败: ' + error.message, 'danger');
    }
}

// 渲染章节列表
function renderChaptersList() {
    const chaptersList = document.getElementById('chapters-list');
    if (!chaptersList) return;
    
    chaptersList.innerHTML = '';
    const chapters = Object.keys(reviewPointsData);
    
    chapters.forEach((chapterName, index) => {
        const button = document.createElement('button');
        button.className = 'list-group-item list-group-item-action';
        button.type = 'button';
        button.setAttribute('data-bs-toggle', 'list');
        button.setAttribute('role', 'tab');
        button.id = `chapter-${index}`;
        button.textContent = chapterName;
        button.onclick = () => showChapterPoints(chapterName);
        
        if (index === 0) {
            button.classList.add('active');
            showChapterPoints(chapterName);
        }
        
        chaptersList.appendChild(button);
    });
}

// 显示章节审核要点
function showChapterPoints(chapterName) {
    const contentDiv = document.getElementById('points-content');
    if (!contentDiv) return;
    
    const points = reviewPointsData[chapterName];
    if (!points) {
        contentDiv.innerHTML = '<div class="alert alert-warning">该章节暂无审核要点</div>';
        return;
    }
    
    let html = `
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="bi bi-file-text"></i> ${chapterName}</h5>
            </div>
            <div class="card-body">
    `;
    
    // 处理不同类型的审核要点结构
    if (Array.isArray(points)) {
        // 如果是数组格式
        points.forEach((point, index) => {
            html += renderPointItem(point, index);
        });
    } else if (typeof points === 'object') {
        // 如果是对象格式
        if (points.必含章节) {
            // 文档完整性类型
            html += `
                <div class="mb-4">
                    <h6><i class="bi bi-list-check"></i> 必含章节</h6>
                    <ul class="list-group">
                        ${points.必含章节.map(chapter => `
                            <li class="list-group-item">
                                <i class="bi bi-check-circle text-success"></i> ${chapter}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
            if (points.审核标准) {
                html += `
                    <div class="alert alert-info">
                        <strong>审核标准：</strong>${points.审核标准}
                    </div>
                `;
            }
            if (points.严重程度) {
                html += `
                    <div class="mb-3">
                        <span class="badge bg-${points.严重程度 === '严重' ? 'danger' : points.严重程度 === '一般' ? 'warning' : 'info'}">
                            严重程度：${points.严重程度}
                        </span>
                    </div>
                `;
            }
        } else {
            // 其他对象格式
            Object.keys(points).forEach((key, index) => {
                const pointData = points[key];
                if (typeof pointData === 'object' && pointData !== null) {
                    html += `
                        <div class="card mb-3">
                            <div class="card-header">
                                <h6 class="mb-0">${key}</h6>
                            </div>
                            <div class="card-body">
                                ${renderPointDetails(pointData)}
                            </div>
                        </div>
                    `;
                }
            });
        }
    }
    
    html += `
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

// 渲染审核要点详情
function renderPointDetails(pointData) {
    let html = '';
    
    if (pointData.必含内容 && Array.isArray(pointData.必含内容)) {
        html += `
            <div class="mb-3">
                <strong><i class="bi bi-list-ul"></i> 必含内容：</strong>
                <ul class="mt-2">
                    ${pointData.必含内容.map(item => `<li>${item}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (pointData.审核重点) {
        html += `
            <div class="mb-3">
                <strong><i class="bi bi-eye"></i> 审核重点：</strong>
                <p class="text-muted mb-0">${pointData.审核重点}</p>
            </div>
        `;
    }
    
    if (pointData.严重程度) {
        const severityClass = pointData.严重程度 === '严重' ? 'danger' : 
                             pointData.严重程度 === '一般' ? 'warning' : 'info';
        html += `
            <div class="mb-3">
                <span class="badge bg-${severityClass}">
                    严重程度：${pointData.严重程度}
                </span>
            </div>
        `;
    }
    
    if (pointData.参考标准) {
        html += `
            <div class="mb-3">
                <strong><i class="bi bi-book"></i> 参考标准：</strong>
                <p class="text-muted mb-0">${pointData.参考标准}</p>
            </div>
        `;
    }
    
    return html;
}

// 搜索审核要点
function searchReviewPoints() {
    const searchTerm = document.getElementById('search-points').value.toLowerCase().trim();
    
    if (!searchTerm) {
        renderChaptersList();
        return;
    }
    
    const chaptersList = document.getElementById('chapters-list');
    const contentDiv = document.getElementById('points-content');
    
    if (!chaptersList || !contentDiv) return;
    
    // 清空列表
    chaptersList.innerHTML = '';
    contentDiv.innerHTML = '';
    
    let foundResults = false;
    
    // 搜索所有章节
    Object.keys(reviewPointsData).forEach((chapterName, index) => {
        const points = reviewPointsData[chapterName];
        const chapterLower = chapterName.toLowerCase();
        
        // 检查章节名称是否匹配
        if (chapterLower.includes(searchTerm)) {
            const button = document.createElement('button');
            button.className = 'list-group-item list-group-item-action';
            button.textContent = chapterName;
            button.onclick = () => showChapterPoints(chapterName);
            chaptersList.appendChild(button);
            
            if (!foundResults) {
                showChapterPoints(chapterName);
                foundResults = true;
            }
        } else {
            // 检查内容是否匹配
            const pointsStr = JSON.stringify(points).toLowerCase();
            if (pointsStr.includes(searchTerm)) {
                const button = document.createElement('button');
                button.className = 'list-group-item list-group-item-action';
                button.textContent = chapterName;
                button.onclick = () => showChapterPoints(chapterName);
                chaptersList.appendChild(button);
                
                if (!foundResults) {
                    showChapterPoints(chapterName);
                    foundResults = true;
                }
            }
        }
    });
    
    if (!foundResults) {
        contentDiv.innerHTML = `
            <div class="alert alert-warning text-center">
                <i class="bi bi-search"></i> 未找到匹配的审核要点
            </div>
        `;
    }
}

// 审核规范管理相关函数
let currentStandardId = null;
let aiModels = [];


// 加载AI模型列表
async function loadAIModels() {
    try {
        const result = await API.getAIModels();
        if (result.code === 200) {
            aiModels = result.data;
            const select = document.getElementById('ai-model-select');
            select.innerHTML = '<option value="">请选择AI模型...</option>';
            aiModels.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = `${model.name} (${model.provider})`;
                if (model.id === 'deepseek-chat') {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载AI模型失败:', error);
    }
}

// 上传审核规范
async function uploadStandard() {
    const fileInput = document.getElementById('standard-file-input');
    const nameInput = document.getElementById('standard-name');
    const categoryInput = document.getElementById('standard-category');
    
    if (!fileInput.files[0]) {
        showAlert('请选择要上传的文件', 'warning');
        return;
    }
    
    try {
        const result = await API.uploadStandard(
            fileInput.files[0],
            nameInput.value.trim() || fileInput.files[0].name,
            categoryInput.value.trim() || '通用规范'
        );
        
        if (result.code === 200) {
            showAlert('审核规范上传成功！', 'success');
            fileInput.value = '';
            nameInput.value = '';
            categoryInput.value = '';
            loadStandards();
        }
    } catch (error) {
        showAlert('上传失败: ' + error.message, 'danger');
    }
}

// 加载审核规范列表
async function loadStandards() {
    try {
        const result = await API.getStandards();
        if (result.code === 200) {
            const container = document.getElementById('standards-list-container');
            if (!container) return;
            
            const standards = result.data;
            if (standards.length === 0) {
                container.innerHTML = '<div class="alert alert-info">暂无审核规范，请先上传</div>';
                return;
            }
            
            let html = '<div class="table-responsive"><table class="table table-hover"><thead><tr>';
            html += '<th>规范名称</th><th>分类</th><th>文件</th><th>规则数</th><th>状态</th><th>操作</th>';
            html += '</tr></thead><tbody>';
            
            standards.forEach(standard => {
                html += `
                    <tr>
                        <td>${standard.name}</td>
                        <td><span class="badge bg-secondary">${standard.category}</span></td>
                        <td>${standard.file_name}</td>
                        <td><span class="badge bg-info">${standard.rules_count}</span></td>
                        <td><span class="badge bg-success">${standard.status}</span></td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="viewStandard(${standard.id})">
                                <i class="bi bi-eye"></i> 查看
                            </button>
                            <button class="btn btn-sm btn-success" onclick="generateRules(${standard.id})">
                                <i class="bi bi-robot"></i> 生成规则
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        }
    } catch (error) {
        console.error('加载规范列表失败:', error);
        showAlert('加载规范列表失败: ' + error.message, 'danger');
    }
}

// 查看规范详情
async function viewStandard(standardId) {
    currentStandardId = standardId;
    try {
        const rulesResult = await API.getStandardRules(standardId);
        const standardsResult = await API.getStandards();
        
        const standard = standardsResult.data.find(s => s.id === standardId);
        const rules = rulesResult.data || [];
        
        let html = `
            <div class="mb-4">
                <h5>${standard.name}</h5>
                <p class="text-muted">分类：${standard.category} | 文件：${standard.file_name}</p>
            </div>
            <div class="mb-3">
                <h6>规则列表（${rules.length}条）</h6>
                <button class="btn btn-sm btn-success" onclick="generateRules(${standardId})">
                    <i class="bi bi-robot"></i> AI生成规则
                </button>
                <button class="btn btn-sm btn-primary" onclick="showCreateRuleModal(${standardId})">
                    <i class="bi bi-plus-circle"></i> 人工编写规则
                </button>
            </div>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>规则名称</th>
                            <th>类型</th>
                            <th>严重程度</th>
                            <th>来源</th>
                            <th>状态</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        rules.forEach(rule => {
            const sourceBadge = rule.is_ai_generated 
                ? `<span class="badge bg-info">AI (${rule.ai_model || '未知'})</span>`
                : '<span class="badge bg-secondary">人工</span>';
            const statusBadge = rule.is_active 
                ? '<span class="badge bg-success">启用</span>'
                : '<span class="badge bg-secondary">禁用</span>';
            
            html += `
                <tr>
                    <td>${rule.rule_name}</td>
                    <td>${rule.rule_type}</td>
                    <td><span class="badge bg-${rule.severity === '严重' ? 'danger' : rule.severity === '一般' ? 'warning' : 'info'}">${rule.severity}</span></td>
                    <td>${sourceBadge}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editRule(${rule.id})">
                            <i class="bi bi-pencil"></i> 编辑
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteRule(${rule.id})">
                            <i class="bi bi-trash"></i> 删除
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        
        document.getElementById('standard-content').innerHTML = html;
        const modal = new bootstrap.Modal(document.getElementById('standardModal'));
        modal.show();
    } catch (error) {
        showAlert('加载规范详情失败: ' + error.message, 'danger');
    }
}

// 生成规则
async function generateRules(standardId) {
    const modelSelect = document.getElementById('ai-model-select');
    const apiKeyInput = document.getElementById('ai-api-key');
    
    const modelName = modelSelect.value;
    const apiKey = apiKeyInput.value.trim() || null;
    
    if (!modelName) {
        showAlert('请先选择AI模型', 'warning');
        return;
    }
    
    if (!confirm('确定要使用AI生成规则吗？这将基于审核规范内容自动拆解生成审核规则。')) {
        return;
    }
    
    try {
        showAlert('正在生成规则，请稍候...', 'info');
        const result = await API.generateRulesFromStandard(standardId, modelName, apiKey);
        
        if (result.code === 200) {
            showAlert(`成功生成${result.data.rules_count}条规则！`, 'success');
            if (currentStandardId === standardId) {
                viewStandard(standardId);
            } else {
                loadStandards();
            }
        }
    } catch (error) {
        showAlert('生成规则失败: ' + error.message, 'danger');
    }
}

// 从规范生成规则（模态框中的按钮）
async function generateRulesFromStandard() {
    if (currentStandardId) {
        await generateRules(currentStandardId);
    }
}

// 显示创建规则模态框
function showCreateRuleModal(standardId = null) {
    document.getElementById('rule-id').value = '';
    document.getElementById('rule-standard-id').value = standardId || currentStandardId || '';
    document.getElementById('rule-modal-title').textContent = '创建审核规则';
    document.getElementById('rule-form').reset();
    document.getElementById('rule-active').checked = true;
    
    const modal = new bootstrap.Modal(document.getElementById('ruleModal'));
    modal.show();
}

// 编辑规则
async function editRule(ruleId) {
    try {
        const standardsResult = await API.getStandards();
        let rule = null;
        
        for (const standard of standardsResult.data) {
            const rulesResult = await API.getStandardRules(standard.id);
            rule = rulesResult.data.find(r => r.id === ruleId);
            if (rule) {
                document.getElementById('rule-standard-id').value = standard.id;
                break;
            }
        }
        
        if (!rule) {
            showAlert('规则不存在', 'warning');
            return;
        }
        
        document.getElementById('rule-id').value = rule.id;
        document.getElementById('rule-standard-id').value = rule.standard_id || '';
        document.getElementById('rule-modal-title').textContent = '编辑审核规则';
        document.getElementById('rule-name').value = rule.rule_name;
        document.getElementById('rule-type').value = rule.rule_type;
        document.getElementById('rule-severity').value = rule.severity;
        document.getElementById('rule-required-content').value = Array.isArray(rule.required_content) 
            ? rule.required_content.join('\n') 
            : '';
        document.getElementById('rule-pattern').value = rule.rule_pattern || '';
        document.getElementById('rule-focus').value = rule.review_focus || '';
        document.getElementById('rule-active').checked = rule.is_active;
        
        const modal = new bootstrap.Modal(document.getElementById('ruleModal'));
        modal.show();
    } catch (error) {
        showAlert('加载规则失败: ' + error.message, 'danger');
    }
}

// 保存规则
async function saveRule() {
    const ruleId = document.getElementById('rule-id').value;
    const standardId = document.getElementById('rule-standard-id').value;
    const requiredContent = document.getElementById('rule-required-content').value
        .split('\n')
        .map(line => line.trim())
        .filter(line => line);
    
    const ruleData = {
        standard_id: standardId ? parseInt(standardId) : null,
        rule_name: document.getElementById('rule-name').value.trim(),
        rule_type: document.getElementById('rule-type').value,
        rule_content: JSON.stringify({
            rule_name: document.getElementById('rule-name').value.trim(),
            rule_type: document.getElementById('rule-type').value,
            required_content: requiredContent,
            review_focus: document.getElementById('rule-focus').value.trim(),
            severity: document.getElementById('rule-severity').value
        }, ensure_ascii=False),
        rule_pattern: document.getElementById('rule-pattern').value.trim(),
        required_content: requiredContent,
        review_focus: document.getElementById('rule-focus').value.trim(),
        severity: document.getElementById('rule-severity').value,
        is_active: document.getElementById('rule-active').checked
    };
    
    try {
        let result;
        if (ruleId) {
            result = await API.updateRule(parseInt(ruleId), ruleData);
        } else {
            result = await API.createRule(ruleData);
        }
        
        if (result.code === 200) {
            showAlert(ruleId ? '规则更新成功！' : '规则创建成功！', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('ruleModal'));
            modal.hide();
            
            if (currentStandardId) {
                viewStandard(currentStandardId);
            } else {
                loadStandards();
            }
        }
    } catch (error) {
        showAlert('保存规则失败: ' + error.message, 'danger');
    }
}

// 删除规则
async function deleteRule(ruleId) {
    if (!confirm('确定要删除这条规则吗？')) {
        return;
    }
    
    try {
        const result = await API.deleteRule(ruleId);
        if (result.code === 200) {
            showAlert('规则删除成功！', 'success');
            if (currentStandardId) {
                viewStandard(currentStandardId);
            } else {
                loadStandards();
            }
        }
    } catch (error) {
        showAlert('删除规则失败: ' + error.message, 'danger');
    }
}
