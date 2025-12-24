# -*- coding: utf-8 -*-
"""
Web界面测试脚本
验证系统是否可以正常启动和访问
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_server():
    """测试服务器是否运行"""
    print("=" * 60)
    print("Web界面测试")
    print("=" * 60)
    
    print("\n1. 检查服务器状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code == 200:
            print("   ✓ 服务器运行正常")
            print(f"   {response.json()}")
        else:
            print(f"   ✗ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到服务器")
        print("   请确保服务已启动: python run.py")
        return False
    except Exception as e:
        print(f"   ✗ 测试失败: {str(e)}")
        return False
    
    print("\n2. 检查Web界面...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("   ✓ Web界面可访问")
            if "技术方案审核AI助手" in response.text:
                print("   ✓ 页面内容正确")
            else:
                print("   ⚠ 页面内容可能不完整")
        else:
            print(f"   ✗ Web界面响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 测试失败: {str(e)}")
        return False
    
    print("\n3. 检查静态文件...")
    static_files = [
        "/static/css/style.css",
        "/static/js/api.js",
        "/static/js/app.js"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{BASE_URL}{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"   ✓ {file_path} 可访问")
            else:
                print(f"   ✗ {file_path} 无法访问")
        except Exception as e:
            print(f"   ✗ {file_path} 测试失败: {str(e)}")
    
    print("\n4. 检查API接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/projects", timeout=5)
        if response.status_code == 200:
            print("   ✓ API接口正常")
        else:
            print(f"   ⚠ API接口响应: {response.status_code}")
    except Exception as e:
        print(f"   ✗ API测试失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n访问地址:")
    print(f"  Web界面: {BASE_URL}")
    print(f"  API文档: {BASE_URL}/docs")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    if test_server():
        sys.exit(0)
    else:
        sys.exit(1)
