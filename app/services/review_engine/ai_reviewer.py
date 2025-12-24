# -*- coding: utf-8 -*-
"""
AI审核引擎
基于大语言模型进行智能审核
"""

import json
from typing import Dict, List, Optional
from app.core.review_point_library import ReviewPointLibrary


class AIReviewer:
    """AI审核引擎"""
    
    def __init__(self, llm_api_key: Optional[str] = None, llm_model: str = "gpt-3.5-turbo"):
        """
        初始化AI审核引擎
        
        Args:
            llm_api_key: 大语言模型API密钥
            llm_model: 使用的模型名称
        """
        self.llm_api_key = llm_api_key
        self.llm_model = llm_model
        self.review_library = ReviewPointLibrary()
        self.use_llm = llm_api_key is not None
    
    def review_document(self, document_content: Dict, project_info: Optional[Dict] = None) -> Dict:
        """
        审核文档
        
        Args:
            document_content: 解析后的文档内容
            project_info: 项目信息
            
        Returns:
            审核结果
        """
        content = document_content.get("content", "")
        chapters = document_content.get("chapters", [])
        
        # 1. 文档完整性审核
        completeness_result = self._review_completeness(chapters)
        
        # 2. 各章节内容审核
        chapter_reviews = []
        for chapter in chapters:
            chapter_name = chapter.get("title", "")
            chapter_content = self._extract_chapter_content(content, chapter)
            review_result = self._review_chapter(chapter_name, chapter_content)
            chapter_reviews.append(review_result)
        
        # 3. 综合评分
        score = self._calculate_score(completeness_result, chapter_reviews)
        
        # 4. 汇总问题和建议
        issues = self._collect_issues(completeness_result, chapter_reviews)
        suggestions = self._collect_suggestions(completeness_result, chapter_reviews)
        
        return {
            "score": score,
            "completeness": completeness_result,
            "chapter_reviews": chapter_reviews,
            "issues": issues,
            "suggestions": suggestions,
            "review_summary": self._generate_summary(score, issues, suggestions)
        }
    
    def _review_completeness(self, chapters: List[Dict]) -> Dict:
        """审核文档完整性"""
        required_chapters = self.review_library.get_review_points_by_chapter("文档完整性")
        required_titles = required_chapters.get("必含章节", [])
        
        found_chapters = []
        missing_chapters = []
        
        # 提取已找到的章节标题
        chapter_titles = [ch.get("title", "") for ch in chapters]
        
        # 检查必含章节
        for required in required_titles:
            # 简化匹配：检查章节编号或关键词
            found = False
            for title in chapter_titles:
                if self._match_chapter(required, title):
                    found = True
                    found_chapters.append(required)
                    break
            
            if not found:
                missing_chapters.append(required)
        
        return {
            "status": "通过" if len(missing_chapters) == 0 else "不通过",
            "found_chapters": found_chapters,
            "missing_chapters": missing_chapters,
            "completeness_rate": len(found_chapters) / len(required_titles) if required_titles else 0
        }
    
    def _match_chapter(self, required: str, actual: str) -> bool:
        """匹配章节"""
        # 提取章节编号
        import re
        required_num = re.search(r'(\d+)', required)
        actual_num = re.search(r'(\d+)', actual)
        
        if required_num and actual_num:
            return required_num.group(1) == actual_num.group(1)
        
        # 关键词匹配
        keywords = ["编制说明", "工程概况", "施工部署", "施工准备", "施工方法", 
                   "进度计划", "资源配置", "质量保证", "安全保证", "文明施工", 
                   "季节性", "应急预案", "附图"]
        
        for keyword in keywords:
            if keyword in required and keyword in actual:
                return True
        
        return False
    
    def _extract_chapter_content(self, full_content: str, chapter: Dict) -> str:
        """提取章节内容"""
        # 简化实现：返回章节标题附近的内容
        # 实际应该根据章节的行号范围提取
        return chapter.get("title", "")
    
    def _review_chapter(self, chapter_name: str, chapter_content: str) -> Dict:
        """审核单个章节"""
        # 获取该章节的审核要点
        review_points = self.review_library.get_review_points_by_chapter(chapter_name)
        
        if not review_points:
            # 尝试匹配章节
            all_points = self.review_library.get_all_review_points()
            for key, points in all_points.items():
                if self._match_chapter_name(chapter_name, key):
                    review_points = points
                    break
        
        if not review_points:
            return {
                "chapter_name": chapter_name,
                "status": "未找到审核要点",
                "issues": [],
                "suggestions": []
            }
        
        # 检查必含内容
        issues = []
        suggestions = []
        
        if isinstance(review_points, dict):
            for point_name, point_config in review_points.items():
                if isinstance(point_config, dict):
                    required_items = point_config.get("必含内容", [])
                    review_focus = point_config.get("审核重点", "")
                    severity = point_config.get("严重程度", "一般")
                    
                    # 检查必含内容是否存在
                    for item in required_items:
                        if not self._check_content_exists(chapter_content, item):
                            issue = {
                                "type": point_name,
                                "item": item,
                                "severity": severity,
                                "description": f"缺少必含内容：{item}",
                                "suggestion": review_focus
                            }
                            if severity == "严重":
                                issues.append(issue)
                            else:
                                suggestions.append(issue)
        
        return {
            "chapter_name": chapter_name,
            "status": "通过" if len(issues) == 0 else "不通过",
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _match_chapter_name(self, chapter_name: str, library_key: str) -> bool:
        """匹配章节名称"""
        keywords_map = {
            "编制说明": ["编制", "说明"],
            "工程概况": ["工程", "概况"],
            "施工部署": ["施工", "部署"],
            "施工准备": ["施工", "准备"],
            "主要施工方法": ["施工", "方法", "技术"],
            "施工进度计划": ["进度", "计划"],
            "资源配置计划": ["资源", "配置"],
            "质量保证措施": ["质量", "保证"],
            "安全保证措施": ["安全", "保证"],
            "文明施工环保": ["文明", "施工", "环保", "环境"],
            "季节性施工措施": ["季节", "施工"],
            "应急预案": ["应急", "预案"],
            "附图附表": ["附图", "附表", "图表"]
        }
        
        if library_key in keywords_map:
            keywords = keywords_map[library_key]
            return all(kw in chapter_name for kw in keywords)
        
        return False
    
    def _check_content_exists(self, content: str, keyword: str) -> bool:
        """检查内容是否存在"""
        # 简化实现：关键词匹配
        # 实际应该使用更智能的语义匹配
        return keyword in content
    
    def _calculate_score(self, completeness: Dict, chapter_reviews: List[Dict]) -> int:
        """计算审核得分"""
        base_score = 100
        
        # 完整性扣分
        completeness_rate = completeness.get("completeness_rate", 0)
        completeness_deduction = (1 - completeness_rate) * 30
        
        # 问题扣分
        issue_deduction = 0
        for review in chapter_reviews:
            issues = review.get("issues", [])
            for issue in issues:
                severity = issue.get("severity", "一般")
                if severity == "严重":
                    issue_deduction += 5
                elif severity == "一般":
                    issue_deduction += 2
        
        score = max(0, base_score - completeness_deduction - issue_deduction)
        return int(score)
    
    def _collect_issues(self, completeness: Dict, chapter_reviews: List[Dict]) -> List[Dict]:
        """收集所有问题"""
        issues = []
        
        # 完整性问题
        missing = completeness.get("missing_chapters", [])
        if missing:
            issues.append({
                "type": "文档完整性",
                "severity": "严重",
                "description": f"缺少必含章节：{', '.join(missing)}",
                "suggestion": "请补充缺失的章节内容"
            })
        
        # 章节问题
        for review in chapter_reviews:
            issues.extend(review.get("issues", []))
        
        return issues
    
    def _collect_suggestions(self, completeness: Dict, chapter_reviews: List[Dict]) -> List[Dict]:
        """收集所有建议"""
        suggestions = []
        
        for review in chapter_reviews:
            suggestions.extend(review.get("suggestions", []))
        
        return suggestions
    
    def _generate_summary(self, score: int, issues: List[Dict], suggestions: List[Dict]) -> str:
        """生成审核摘要"""
        severe_count = len([i for i in issues if i.get("severity") == "严重"])
        general_count = len([i for i in issues if i.get("severity") == "一般"])
        suggestion_count = len(suggestions)
        
        summary = f"审核得分：{score}分\n\n"
        summary += f"发现严重问题：{severe_count}项\n"
        summary += f"发现一般问题：{general_count}项\n"
        summary += f"优化建议：{suggestion_count}项\n\n"
        
        if score >= 80:
            summary += "总体评价：方案基本符合要求，建议根据审核意见进行优化。"
        elif score >= 60:
            summary += "总体评价：方案存在较多问题，需要重点整改。"
        else:
            summary += "总体评价：方案存在严重缺陷，必须进行重大修改。"
        
        return summary
    
    def _call_llm(self, prompt: str) -> str:
        """调用大语言模型（可选功能）"""
        if not self.use_llm:
            return ""
        
        try:
            # 这里可以集成OpenAI、文心一言等API
            # 示例代码（需要实际配置）
            pass
        except Exception as e:
            print(f"LLM调用失败: {str(e)}")
            return ""
