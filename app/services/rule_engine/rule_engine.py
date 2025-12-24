# -*- coding: utf-8 -*-
"""
规则引擎模块
基于配置的规则进行审核
"""

from typing import Dict, List, Any
import re


class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules = []
        self.load_default_rules()
    
    def load_default_rules(self):
        """加载默认规则"""
        self.rules = [
            {
                "name": "安全目标检查",
                "type": "内容检查",
                "pattern": r"安全目标.*?(零事故|零伤亡|无事故)",
                "severity": "严重",
                "description": "必须明确安全目标"
            },
            {
                "name": "质量目标检查",
                "type": "内容检查",
                "pattern": r"质量目标.*?(合格率|优良率|100%)",
                "severity": "严重",
                "description": "必须明确质量目标"
            },
            {
                "name": "应急预案检查",
                "type": "章节检查",
                "pattern": r"应急.*?预案",
                "severity": "严重",
                "description": "必须包含应急预案"
            },
            {
                "name": "重大危险源检查",
                "type": "内容检查",
                "pattern": r"重大危险源.*?(识别|清单|监控)",
                "severity": "严重",
                "description": "必须包含重大危险源管理内容"
            }
        ]
    
    def add_rule(self, rule: Dict):
        """添加规则"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str):
        """移除规则"""
        self.rules = [r for r in self.rules if r.get("name") != rule_name]
    
    def check_rules(self, content: str, chapters: List[Dict] = None) -> List[Dict]:
        """
        检查规则
        
        Args:
            content: 文档内容
            chapters: 章节列表
            
        Returns:
            检查结果列表
        """
        results = []
        
        for rule in self.rules:
            if rule.get("type") == "内容检查":
                result = self._check_content_rule(rule, content)
                if result:
                    results.append(result)
            elif rule.get("type") == "章节检查":
                result = self._check_chapter_rule(rule, chapters or [])
                if result:
                    results.append(result)
        
        return results
    
    def _check_content_rule(self, rule: Dict, content: str) -> Dict:
        """检查内容规则"""
        pattern = rule.get("pattern", "")
        if not pattern:
            return None
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return {
                "rule_name": rule.get("name"),
                "status": "不通过",
                "severity": rule.get("severity", "一般"),
                "description": rule.get("description", ""),
                "suggestion": f"请检查是否包含：{rule.get('description', '')}"
            }
        
        return None
    
    def _check_chapter_rule(self, rule: Dict, chapters: List[Dict]) -> Dict:
        """检查章节规则"""
        pattern = rule.get("pattern", "")
        if not pattern:
            return None
        
        found = False
        for chapter in chapters:
            title = chapter.get("title", "")
            if re.search(pattern, title, re.IGNORECASE):
                found = True
                break
        
        if not found:
            return {
                "rule_name": rule.get("name"),
                "status": "不通过",
                "severity": rule.get("severity", "一般"),
                "description": rule.get("description", ""),
                "suggestion": f"请添加章节：{rule.get('description', '')}"
            }
        
        return None
    
    def get_active_rules(self) -> List[Dict]:
        """获取所有激活的规则"""
        return [r for r in self.rules if r.get("is_active", True)]
