#!/usr/bin/env python3
"""
BDD集成测试运行脚本
提供便捷的测试执行和报告生成功能
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Optional

class BDDTestRunner:
    """BDD测试运行器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_dir = self.project_root / "tests" / "bdd"
        self.backend_dir = self.project_root / "backend"
        
    def run_critical_path_tests(
        self, 
        markers: Optional[List[str]] = None,
        verbose: bool = True,
        generate_report: bool = True
    ) -> int:
        """
        运行关键路径测试
        
        Args:
            markers: 测试标记过滤器
            verbose: 详细输出
            generate_report: 生成测试报告
            
        Returns:
            退出码
        """
        print("🚀 开始运行AI路线规划关键路径测试...")
        
        # 构建pytest命令
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-v" if verbose else "-q",
            "--tb=short",
            "--color=yes",
            "--durations=10"
        ]
        
        # 添加标记过滤器
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # 添加报告生成
        if generate_report:
            report_dir = self.test_dir / "reports"
            report_dir.mkdir(exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            html_report = report_dir / f"test_report_{timestamp}.html"
            
            cmd.extend([
                "--html", str(html_report),
                "--self-contained-html"
            ])
        
        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        
        print(f"📋 执行命令: {' '.join(cmd)}")
        print(f"📁 工作目录: {self.test_dir}")
        
        # 运行测试
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                env=env,
                capture_output=False
            )
            
            if result.returncode == 0:
                print("✅ 所有测试通过！")
                if generate_report:
                    print(f"📊 测试报告已生成: {html_report}")
            else:
                print(f"❌ 测试失败，退出码: {result.returncode}")
            
            return result.returncode
            
        except KeyboardInterrupt:
            print("\n⚠️  测试被用户中断")
            return 130
        except Exception as e:
            print(f"❌ 运行测试时发生错误: {e}")
            return 1
    
    def run_smoke_tests(self) -> int:
        """运行冒烟测试"""
        print("💨 运行冒烟测试...")
        return self.run_critical_path_tests(
            markers=["smoke"],
            verbose=False,
            generate_report=False
        )
    
    def run_performance_tests(self) -> int:
        """运行性能测试"""
        print("⚡ 运行性能测试...")
        return self.run_critical_path_tests(
            markers=["performance"],
            verbose=True,
            generate_report=True
        )
    
    def run_integration_tests(self) -> int:
        """运行集成测试"""
        print("🔗 运行集成测试...")
        return self.run_critical_path_tests(
            markers=["integration"],
            verbose=True,
            generate_report=True
        )
    
    def run_all_tests(self) -> int:
        """运行所有测试"""
        print("🎯 运行所有关键路径测试...")
        return self.run_critical_path_tests(
            markers=["critical_path"],
            verbose=True,
            generate_report=True
        )
    
    def check_backend_status(self) -> bool:
        """检查后端服务状态"""
        try:
            import httpx
            
            print("🔍 检查后端服务状态...")
            
            with httpx.Client(timeout=5.0) as client:
                response = client.get("http://localhost:8000/api/v1/ai/health")
                
                if response.status_code == 200:
                    print("✅ 后端服务运行正常")
                    return True
                else:
                    print(f"⚠️  后端服务响应异常: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 无法连接到后端服务: {e}")
            print("💡 请确保后端服务已启动: cd backend && python3 main.py")
            return False
    
    def setup_test_environment(self) -> bool:
        """设置测试环境"""
        print("🛠️  设置测试环境...")
        
        # 检查必要的依赖
        required_packages = ["pytest", "httpx", "pytest-asyncio"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ 缺少必要的测试依赖: {', '.join(missing_packages)}")
            print("💡 请安装: pip install " + " ".join(missing_packages))
            return False
        
        # 创建必要的目录
        (self.test_dir / "reports").mkdir(exist_ok=True)
        (self.test_dir / "logs").mkdir(exist_ok=True)
        
        print("✅ 测试环境设置完成")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI路线规划BDD集成测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
测试类型说明:
  smoke      - 冒烟测试，快速验证基本功能
  performance - 性能测试，验证响应时间和吞吐量  
  integration - 集成测试，验证API端点集成
  all        - 所有关键路径测试
  
示例用法:
  python run_tests.py smoke                    # 运行冒烟测试
  python run_tests.py all                      # 运行所有测试
  python run_tests.py --markers llm_integration # 运行LLM集成测试
  python run_tests.py --check-backend          # 仅检查后端状态
        """
    )
    
    parser.add_argument(
        "test_type",
        nargs="?",
        choices=["smoke", "performance", "integration", "all"],
        default="all",
        help="测试类型 (默认: all)"
    )
    
    parser.add_argument(
        "--markers",
        nargs="+",
        help="指定测试标记过滤器"
    )
    
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="不生成测试报告"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式，减少输出"
    )
    
    parser.add_argument(
        "--check-backend",
        action="store_true",
        help="仅检查后端服务状态"
    )
    
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="仅设置测试环境"
    )
    
    args = parser.parse_args()
    
    runner = BDDTestRunner()
    
    # 仅检查后端状态
    if args.check_backend:
        backend_ok = runner.check_backend_status()
        return 0 if backend_ok else 1
    
    # 仅设置环境
    if args.setup_only:
        setup_ok = runner.setup_test_environment()
        return 0 if setup_ok else 1
    
    # 设置测试环境
    if not runner.setup_test_environment():
        return 1
    
    # 检查后端服务
    if not runner.check_backend_status():
        print("⚠️  后端服务未运行，某些测试可能失败")
        response = input("是否继续运行测试? (y/N): ")
        if response.lower() != 'y':
            return 1
    
    # 运行指定的测试
    if args.markers:
        # 使用自定义标记
        return runner.run_critical_path_tests(
            markers=args.markers,
            verbose=not args.quiet,
            generate_report=not args.no_report
        )
    elif args.test_type == "smoke":
        return runner.run_smoke_tests()
    elif args.test_type == "performance":
        return runner.run_performance_tests()
    elif args.test_type == "integration":
        return runner.run_integration_tests()
    else:  # all
        return runner.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())