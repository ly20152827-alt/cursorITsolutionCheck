# -*- coding: utf-8 -*-
"""
使用示例脚本
演示如何使用技术方案审核AI助手系统
"""

import requests
import json
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8000"


def create_project(name: str, project_type: str = "施工前期"):
    """创建项目"""
    print(f"\n1. 创建项目: {name}")
    response = requests.post(
        f"{BASE_URL}/api/projects",
        params={"name": name, "project_type": project_type}
    )
    result = response.json()
    if result.get("code") == 200:
        project_id = result["data"]["project_id"]
        print(f"   项目创建成功，ID: {project_id}")
        return project_id
    else:
        print(f"   项目创建失败: {result.get('message')}")
        return None


def upload_document(project_id: int, file_path: str):
    """上传文档"""
    print(f"\n2. 上传文档: {file_path}")
    if not Path(file_path).exists():
        print(f"   文件不存在: {file_path}")
        return None
    
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/documents/upload",
            files=files
        )
    
    result = response.json()
    if result.get("code") == 200:
        document_id = result["data"]["document_id"]
        print(f"   文档上传成功，ID: {document_id}")
        return document_id
    else:
        print(f"   文档上传失败: {result.get('message')}")
        return None


def parse_document(document_id: int):
    """解析文档"""
    print(f"\n3. 解析文档: {document_id}")
    response = requests.post(f"{BASE_URL}/api/documents/{document_id}/parse")
    result = response.json()
    if result.get("code") == 200:
        print(f"   文档解析成功")
        print(f"   章节数量: {result['data']['chapters_count']}")
        print(f"   内容长度: {result['data']['content_length']} 字符")
        return True
    else:
        print(f"   文档解析失败: {result.get('message')}")
        return False


def review_document(document_id: int, use_ai: bool = True):
    """审核文档"""
    print(f"\n4. 审核文档: {document_id}")
    response = requests.post(
        f"{BASE_URL}/api/documents/{document_id}/review",
        params={"use_ai": use_ai}
    )
    result = response.json()
    if result.get("code") == 200:
        data = result["data"]
        print(f"   审核完成")
        print(f"   审核得分: {data['score']} 分")
        print(f"   问题数量: {data['issues_count']} 项")
        print(f"   建议数量: {data['suggestions_count']} 项")
        return data.get("review_id")
    else:
        print(f"   审核失败: {result.get('message')}")
        return None


def get_report(review_id: int, format: str = "json"):
    """获取审核报告"""
    print(f"\n5. 获取审核报告: {review_id}")
    response = requests.get(
        f"{BASE_URL}/api/reviews/{review_id}/report",
        params={"format": format}
    )
    result = response.json()
    if result.get("code") == 200:
        if format == "json":
            report = result["data"]
            print(f"   报告生成成功")
            print(f"\n   审核摘要:")
            print(f"   {report['review_summary']}")
            print(f"\n   审核结论:")
            print(f"   {report['conclusion']['conclusion']}")
            print(f"   {report['conclusion']['description']}")
            
            # 保存报告
            report_file = f"data/reports/report_{review_id}_example.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n   报告已保存至: {report_file}")
        else:
            print(f"   报告文件: {result['data']['report_file']}")
        return result["data"]
    else:
        print(f"   获取报告失败: {result.get('message')}")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("技术方案审核AI助手系统 - 使用示例")
    print("=" * 60)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("错误: API服务未运行，请先启动服务")
            print("启动命令: python run.py")
            return
    except Exception as e:
        print(f"错误: 无法连接到API服务 ({str(e)})")
        print("请确保服务已启动: python run.py")
        return
    
    # 示例：使用本地文档
    # 注意：需要将实际的文档路径替换为您的文档路径
    document_path = "机场场道工程施工组织设计范本.docx"
    
    if not Path(document_path).exists():
        print(f"\n提示: 文档文件不存在 ({document_path})")
        print("请将文档放在项目根目录，或修改 document_path 变量")
        print("\n您可以手动测试API接口:")
        print("1. 访问 http://localhost:8000/docs 查看API文档")
        print("2. 使用Postman或其他工具测试接口")
        return
    
    # 执行完整流程
    project_id = create_project("测试项目-机场场道工程", "施工前期")
    if not project_id:
        return
    
    document_id = upload_document(project_id, document_path)
    if not document_id:
        return
    
    if not parse_document(document_id):
        return
    
    review_id = review_document(document_id)
    if not review_id:
        return
    
    get_report(review_id)
    
    print("\n" + "=" * 60)
    print("示例执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
