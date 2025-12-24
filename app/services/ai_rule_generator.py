# -*- coding: utf-8 -*-
"""
AI规则生成服务
基于大语言模型从审核规范中拆解生成审核规则
"""

import json
import re
from typing import List, Dict, Optional
import os


class AIRuleGenerator:
    """AI规则生成器"""
    
    # 支持的模型配置（参考Dify平台模式）
    MODEL_CONFIGS = {
        "deepseek-chat": {
            "name": "DeepSeek Chat",
            "provider": "deepseek",
            "api_base": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "max_tokens": 4000
        },
        "deepseek-coder": {
            "name": "DeepSeek Coder",
            "provider": "deepseek",
            "api_base": "https://api.deepseek.com/v1",
            "model": "deepseek-coder",
            "max_tokens": 4000
        },
        "gpt-4": {
            "name": "GPT-4",
            "provider": "openai",
            "api_base": "https://api.openai.com/v1",
            "model": "gpt-4",
            "max_tokens": 4000
        },
        "gpt-3.5-turbo": {
            "name": "GPT-3.5 Turbo",
            "provider": "openai",
            "api_base": "https://api.openai.com/v1",
            "model": "gpt-3.5-turbo",
            "max_tokens": 4000
        },
        "claude-3-opus": {
            "name": "Claude 3 Opus",
            "provider": "anthropic",
            "api_base": "https://api.anthropic.com/v1",
            "model": "claude-3-opus-20240229",
            "max_tokens": 4000
        }
    }
    
    def __init__(self, model_name: str = "deepseek-chat", api_key: Optional[str] = None):
        """
        初始化AI规则生成器
        
        Args:
            model_name: 模型名称
            api_key: API密钥
        """
        self.model_name = model_name
        self.model_config = self.MODEL_CONFIGS.get(model_name, self.MODEL_CONFIGS["deepseek-chat"])
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
    
    def generate_rules_from_standard(self, standard_content: str, category: str = "") -> List[Dict]:
        """
        从审核规范内容中生成审核规则
        
        Args:
            standard_content: 规范内容
            category: 规范分类
            
        Returns:
            生成的规则列表
        """
        if not self.api_key:
            # 如果没有API密钥，使用规则模板生成
            return self._generate_rules_without_ai(standard_content, category)
        
        try:
            # 构建提示词
            prompt = self._build_prompt(standard_content, category)
            
            # 调用AI模型
            response = self._call_llm(prompt)
            
            # 解析响应
            rules = self._parse_ai_response(response)
            
            return rules
        except Exception as e:
            print(f"AI生成规则失败: {str(e)}")
            # 降级到非AI生成
            return self._generate_rules_without_ai(standard_content, category)
    
    def _build_prompt(self, content: str, category: str) -> str:
        """构建AI提示词"""
        prompt = f"""你是一个专业的审核规则生成专家。请根据以下审核规范内容，拆解生成具体的审核规则。

规范分类：{category}
规范内容：
{content}

请按照以下JSON格式输出审核规则列表，每个规则包含以下字段：
- rule_name: 规则名称
- rule_type: 规则类型（内容检查/章节检查/格式检查）
- required_content: 必含内容列表（数组）
- review_focus: 审核重点描述
- severity: 严重程度（严重/一般/建议）
- rule_pattern: 规则匹配模式（正则表达式，可选）

输出格式示例：
```json
[
    {{
        "rule_name": "安全目标检查",
        "rule_type": "内容检查",
        "required_content": ["安全目标", "零事故", "零伤亡"],
        "review_focus": "必须明确安全目标，包含零事故、零伤亡等关键指标",
        "severity": "严重",
        "rule_pattern": "安全目标.*?(零事故|零伤亡|无事故)"
    }}
]
```

请生成至少5条规则，确保规则具体、可操作、可检测。只输出JSON数组，不要其他文字说明。"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用大语言模型"""
        import requests
        
        model_config = self.model_config
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if model_config["provider"] == "deepseek":
            url = f"{model_config['api_base']}/chat/completions"
            data = {
                "model": model_config["model"],
                "messages": [
                    {"role": "system", "content": "你是一个专业的审核规则生成专家。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": model_config["max_tokens"],
                "temperature": 0.3
            }
        elif model_config["provider"] == "openai":
            url = f"{model_config['api_base']}/chat/completions"
            data = {
                "model": model_config["model"],
                "messages": [
                    {"role": "system", "content": "你是一个专业的审核规则生成专家。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": model_config["max_tokens"],
                "temperature": 0.3
            }
        else:
            raise ValueError(f"不支持的模型提供商: {model_config['provider']}")
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _parse_ai_response(self, response: str) -> List[Dict]:
        """解析AI响应"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = response.strip()
                if json_str.startswith('['):
                    pass
                else:
                    # 查找第一个[
                    start = json_str.find('[')
                    end = json_str.rfind(']') + 1
                    if start >= 0 and end > start:
                        json_str = json_str[start:end]
                    else:
                        raise ValueError("无法找到JSON数组")
            
            rules = json.loads(json_str)
            
            # 验证和规范化规则
            normalized_rules = []
            for rule in rules:
                normalized_rule = {
                    "rule_name": rule.get("rule_name", "未命名规则"),
                    "rule_type": rule.get("rule_type", "内容检查"),
                    "required_content": rule.get("required_content", []),
                    "review_focus": rule.get("review_focus", ""),
                    "severity": rule.get("severity", "一般"),
                    "rule_pattern": rule.get("rule_pattern", "")
                }
                normalized_rules.append(normalized_rule)
            
            return normalized_rules
        except Exception as e:
            print(f"解析AI响应失败: {str(e)}")
            return []
    
    def _generate_rules_without_ai(self, content: str, category: str) -> List[Dict]:
        """不使用AI的规则生成（基于关键词和模板）"""
        rules = []
        
        # 基于关键词生成规则
        keywords_map = {
            "安全": {
                "rule_name": "安全措施检查",
                "rule_type": "内容检查",
                "required_content": ["安全措施", "安全管理制度", "安全防护"],
                "review_focus": "必须包含完整的安全措施和管理制度",
                "severity": "严重",
                "rule_pattern": "安全.*?(措施|制度|防护)"
            },
            "质量": {
                "rule_name": "质量保证检查",
                "rule_type": "内容检查",
                "required_content": ["质量保证", "质量管理", "质量控制"],
                "review_focus": "必须包含质量保证措施和质量管理体系",
                "severity": "严重",
                "rule_pattern": "质量.*?(保证|管理|控制)"
            },
            "进度": {
                "rule_name": "进度计划检查",
                "rule_type": "内容检查",
                "required_content": ["进度计划", "施工进度", "工期"],
                "review_focus": "必须包含详细的进度计划和工期安排",
                "severity": "一般",
                "rule_pattern": "进度.*?(计划|安排)"
            }
        }
        
        content_lower = content.lower()
        for keyword, rule_template in keywords_map.items():
            if keyword in content_lower:
                rules.append(rule_template.copy())
        
        # 如果没找到关键词，生成通用规则
        if not rules:
            rules.append({
                "rule_name": f"{category}规范检查",
                "rule_type": "内容检查",
                "required_content": [category],
                "review_focus": f"必须符合{category}相关规范要求",
                "severity": "一般",
                "rule_pattern": ""
            })
        
        return rules
    
    @classmethod
    def get_available_models(cls) -> List[Dict]:
        """获取可用的模型列表"""
        return [
            {
                "id": model_id,
                "name": config["name"],
                "provider": config["provider"]
            }
            for model_id, config in cls.MODEL_CONFIGS.items()
        ]
    
    def update_model(self, model_name: str):
        """更新使用的模型"""
        if model_name in self.MODEL_CONFIGS:
            self.model_name = model_name
            self.model_config = self.MODEL_CONFIGS[model_name]
        else:
            raise ValueError(f"不支持的模型: {model_name}")

