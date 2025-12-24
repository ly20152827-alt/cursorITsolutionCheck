# -*- coding: utf-8 -*-
"""
审核报告生成模块
"""

from typing import Dict, List
from datetime import datetime
import json


class ReportGenerator:
    """审核报告生成器"""
    
    def __init__(self):
        self.template = self._load_template()
    
    def _load_template(self) -> Dict:
        """加载报告模板"""
        return {
            "title": "技术方案审核报告",
            "sections": [
                "报告基本信息",
                "审核结果概览",
                "文档完整性检查",
                "各章节审核详情",
                "问题清单",
                "修改建议",
                "审核结论"
            ]
        }
    
    def generate_report(self, review_result: Dict, project_info: Dict = None) -> Dict:
        """
        生成审核报告
        
        Args:
            review_result: 审核结果
            project_info: 项目信息
            
        Returns:
            报告内容
        """
        report = {
            "report_info": {
                "title": "技术方案审核报告",
                "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "project_name": project_info.get("name", "未知项目") if project_info else "未知项目",
                "project_type": project_info.get("project_type", "") if project_info else ""
            },
            "review_summary": {
                "score": review_result.get("score", 0),
                "total_issues": len(review_result.get("issues", [])),
                "severe_issues": len([i for i in review_result.get("issues", []) if i.get("severity") == "严重"]),
                "general_issues": len([i for i in review_result.get("issues", []) if i.get("severity") == "一般"]),
                "suggestions": len(review_result.get("suggestions", []))
            },
            "completeness_check": review_result.get("completeness", {}),
            "chapter_reviews": review_result.get("chapter_reviews", []),
            "issues_list": self._format_issues(review_result.get("issues", [])),
            "suggestions_list": self._format_suggestions(review_result.get("suggestions", [])),
            "conclusion": self._generate_conclusion(review_result)
        }
        
        return report
    
    def _format_issues(self, issues: List[Dict]) -> List[Dict]:
        """格式化问题列表"""
        formatted = []
        
        # 按严重程度分组
        severe_issues = [i for i in issues if i.get("severity") == "严重"]
        general_issues = [i for i in issues if i.get("severity") == "一般"]
        
        if severe_issues:
            formatted.append({
                "category": "严重问题",
                "items": severe_issues
            })
        
        if general_issues:
            formatted.append({
                "category": "一般问题",
                "items": general_issues
            })
        
        return formatted
    
    def _format_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """格式化建议列表"""
        return suggestions
    
    def _generate_conclusion(self, review_result: Dict) -> Dict:
        """生成审核结论"""
        score = review_result.get("score", 0)
        issues = review_result.get("issues", [])
        severe_count = len([i for i in issues if i.get("severity") == "严重"])
        
        if score >= 80 and severe_count == 0:
            conclusion = "通过"
            description = "方案基本符合要求，建议根据审核意见进行优化完善。"
        elif score >= 60:
            conclusion = "有条件通过"
            description = "方案存在一些问题，需要根据审核意见进行整改后重新提交审核。"
        else:
            conclusion = "不通过"
            description = "方案存在严重缺陷，必须进行重大修改后重新提交审核。"
        
        return {
            "conclusion": conclusion,
            "description": description,
            "next_steps": self._get_next_steps(conclusion, severe_count)
        }
    
    def _get_next_steps(self, conclusion: str, severe_count: int) -> List[str]:
        """获取后续步骤"""
        if conclusion == "通过":
            return [
                "根据审核建议进行方案优化",
                "准备相关支撑材料",
                "提交最终版本"
            ]
        elif conclusion == "有条件通过":
            return [
                "重点整改严重问题",
                "完善一般问题",
                "重新提交审核"
            ]
        else:
            return [
                "全面梳理方案内容",
                "补充缺失的关键章节",
                "完善安全、质量保证措施",
                "重新编制后提交审核"
            ]
    
    def export_to_json(self, report: Dict, file_path: str):
        """导出为JSON格式"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def export_to_text(self, report: Dict, file_path: str):
        """导出为文本格式"""
        lines = []
        
        # 报告标题
        lines.append("=" * 60)
        lines.append(report["report_info"]["title"])
        lines.append("=" * 60)
        lines.append("")
        
        # 基本信息
        lines.append("一、报告基本信息")
        lines.append(f"项目名称：{report['report_info']['project_name']}")
        lines.append(f"项目类型：{report['report_info']['project_type']}")
        lines.append(f"生成时间：{report['report_info']['generate_time']}")
        lines.append("")
        
        # 审核结果概览
        lines.append("二、审核结果概览")
        summary = report["review_summary"]
        lines.append(f"审核得分：{summary['score']}分")
        lines.append(f"严重问题：{summary['severe_issues']}项")
        lines.append(f"一般问题：{summary['general_issues']}项")
        lines.append(f"优化建议：{summary['suggestions']}项")
        lines.append("")
        
        # 问题清单
        lines.append("三、问题清单")
        for category_group in report["issues_list"]:
            lines.append(f"\n【{category_group['category']}】")
            for i, item in enumerate(category_group["items"], 1):
                lines.append(f"{i}. {item.get('description', '')}")
                if item.get('suggestion'):
                    lines.append(f"   建议：{item['suggestion']}")
        lines.append("")
        
        # 审核结论
        lines.append("四、审核结论")
        conclusion = report["conclusion"]
        lines.append(f"结论：{conclusion['conclusion']}")
        lines.append(f"说明：{conclusion['description']}")
        lines.append("\n后续步骤：")
        for step in conclusion["next_steps"]:
            lines.append(f"  - {step}")
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
