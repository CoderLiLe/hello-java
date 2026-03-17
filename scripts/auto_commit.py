#!/usr/bin/env python3
"""
自动提交脚本 for hello-java
自动检测更改、提交并推送到GitHub
"""

import os
import sys
import subprocess
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class AutoCommit:
    """自动提交管理器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).absolute()
        self.config_file = self.repo_path / ".auto_commit_config.json"
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置"""
        default_config = {
            "auto_commit": True,
            "commit_message_prefix": "Auto commit: ",
            "branch": "main",
            "push_to_remote": True,
            "remote_name": "origin",
            "check_interval_minutes": 60,
            "max_commit_size_mb": 10,
            "exclude_patterns": [
                "*.log",
                "*.tmp",
                "*.bak",
                "__pycache__",
                ".git",
                ".idea",
                ".vscode",
                "node_modules"
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = {**default_config, **json.load(f)}
            except Exception as e:
                print(f"加载配置失败，使用默认配置: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self) -> None:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def check_git_status(self) -> Tuple[bool, str]:
        """检查Git状态"""
        try:
            # 检查是否有未提交的更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, f"Git状态检查失败: {result.stderr}"
            
            changes = result.stdout.strip()
            if not changes:
                return False, "没有需要提交的更改"
            
            # 统计更改
            lines = changes.split('\n')
            added = sum(1 for line in lines if line.startswith('A ') or line.startswith('?? '))
            modified = sum(1 for line in lines if line.startswith('M '))
            deleted = sum(1 for line in lines if line.startswith('D '))
            
            summary = f"检测到更改: 新增{added}个文件, 修改{modified}个文件, 删除{deleted}个文件"
            return True, summary
            
        except Exception as e:
            return False, f"检查Git状态时出错: {e}"
    
    def get_commit_message(self) -> str:
        """生成提交消息"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取更改摘要
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                changed_files = result.stdout.strip().split('\n')
                file_types = {}
                
                for file in changed_files:
                    if file:
                        ext = Path(file).suffix.lower()
                        file_types[ext] = file_types.get(ext, 0) + 1
                
                type_summary = ", ".join([f"{ext}:{count}" for ext, count in file_types.items()])
                return f"{self.config['commit_message_prefix']}{timestamp} [{type_summary}]"
        
        except Exception:
            pass
        
        return f"{self.config['commit_message_prefix']}{timestamp}"
    
    def stage_changes(self) -> Tuple[bool, str]:
        """暂存更改"""
        try:
            # 添加所有更改
            result = subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, f"暂存更改失败: {result.stderr}"
            
            return True, "更改已暂存"
            
        except Exception as e:
            return False, f"暂存更改时出错: {e}"
    
    def create_commit(self, message: str) -> Tuple[bool, str]:
        """创建提交"""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, f"创建提交失败: {result.stderr}"
            
            # 获取提交哈希
            hash_result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
            return True, f"提交创建成功: {commit_hash}"
            
        except Exception as e:
            return False, f"创建提交时出错: {e}"
    
    def push_to_remote(self) -> Tuple[bool, str]:
        """推送到远程仓库"""
        try:
            result = subprocess.run(
                ["git", "push", self.config["remote_name"], self.config["branch"]],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, f"推送失败: {result.stderr}"
            
            return True, "成功推送到远程仓库"
            
        except Exception as e:
            return False, f"推送时出错: {e}"
    
    def run_auto_commit(self, dry_run: bool = False) -> Dict:
        """运行自动提交流程"""
        print(f"开始自动提交检查: {self.repo_path}")
        print("=" * 50)
        
        result = {
            "timestamp": datetime.datetime.now().isoformat(),
            "dry_run": dry_run,
            "has_changes": False,
            "staged": False,
            "committed": False,
            "pushed": False,
            "messages": [],
            "errors": []
        }
        
        # 1. 检查状态
        has_changes, status_msg = self.check_git_status()
        result["has_changes"] = has_changes
        result["messages"].append(f"状态检查: {status_msg}")
        
        if not has_changes:
            print(f"✓ {status_msg}")
            return result
        
        print(f"📝 {status_msg}")
        
        if dry_run:
            result["messages"].append("干运行模式，不执行实际操作")
            print("干运行模式，不执行实际操作")
            return result
        
        # 2. 暂存更改
        staged, stage_msg = self.stage_changes()
        result["staged"] = staged
        result["messages"].append(f"暂存: {stage_msg}")
        
        if not staged:
            result["errors"].append(f"暂存失败: {stage_msg}")
            print(f"❌ {stage_msg}")
            return result
        
        print(f"✓ {stage_msg}")
        
        # 3. 创建提交
        commit_message = self.get_commit_message()
        committed, commit_msg = self.create_commit(commit_message)
        result["committed"] = committed
        result["messages"].append(f"提交: {commit_msg}")
        
        if not committed:
            result["errors"].append(f"提交失败: {commit_msg}")
            print(f"❌ {commit_msg}")
            return result
        
        print(f"✓ {commit_msg}")
        print(f"提交消息: {commit_message}")
        
        # 4. 推送到远程
        if self.config["push_to_remote"]:
            pushed, push_msg = self.push_to_remote()
            result["pushed"] = pushed
            result["messages"].append(f"推送: {push_msg}")
            
            if not pushed:
                result["errors"].append(f"推送失败: {push_msg}")
                print(f"❌ {push_msg}")
            else:
                print(f"✓ {push_msg}")
        else:
            result["messages"].append("推送已禁用")
            print("ℹ️ 推送已禁用")
        
        print("=" * 50)
        print("自动提交完成!")
        
        return result
    
    def create_scheduled_task(self) -> None:
        """创建定时任务"""
        print("创建定时任务...")
        
        # 创建cron任务
        cron_line = f"*/{self.config['check_interval_minutes']} * * * * cd {self.repo_path} && {sys.executable} {Path(__file__).absolute()} --run"
        
        print("\n请将以下行添加到crontab:")
        print("=" * 50)
        print(cron_line)
        print("=" * 50)
        print("\n添加方法:")
        print("1. 运行: crontab -e")
        print("2. 粘贴上面的行")
        print("3. 保存并退出")
        
        # 创建systemd服务文件（可选）
        service_content = f"""[Unit]
Description=Auto Commit Service for {self.repo_path.name}
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory={self.repo_path}
ExecStart={sys.executable} {Path(__file__).absolute()} --run
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
"""
        
        service_file = f"/tmp/{self.repo_path.name}-auto-commit.service"
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(service_content)
        
        print(f"\nSystemd服务文件已保存到: {service_file}")
        print("如需使用systemd，请运行:")
        print(f"sudo cp {service_file} /etc/systemd/system/")
        print(f"sudo systemctl enable {self.repo_path.name}-auto-commit")
        print(f"sudo systemctl start {self.repo_path.name}-auto-commit")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动提交脚本")
    parser.add_argument("--run", action="store_true", help="运行自动提交")
    parser.add_argument("--dry-run", action="store_true", help="干运行模式")
    parser.add_argument("--config", action="store_true", help="显示配置")
    parser.add_argument("--setup-cron", action="store_true", help="设置定时任务")
    parser.add_argument("--repo-path", default=".", help="仓库路径")
    
    args = parser.parse_args()
    
    auto_commit = AutoCommit(args.repo_path)
    
    if args.config:
        print("当前配置:")
        print(json.dumps(auto_commit.config, indent=2, ensure_ascii=False))
        return 0
    
    if args.setup_cron:
        auto_commit.create_scheduled_task()
        return 0
    
    if args.run or args.dry_run:
        result = auto_commit.run_auto_commit(dry_run=args.dry_run)
        
        # 保存结果
        log_file = auto_commit.repo_path / "auto_commit_log.json"
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(result)
            
            # 只保留最近100条记录
            if len(logs) > 100:
                logs = logs[-100:]
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存日志失败: {e}")
        
        return 0 if not result.get("errors") else 1
    
    # 交互模式
    print("自动提交脚本")
    print("=" * 50)
    
    while True:
        print("\n选项:")
        print("1. 运行自动提交")
        print("2. 干运行模式")
        print("3. 查看配置")
        print("4. 设置定时任务")
        print("5. 退出")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == "1":
            auto_commit.run_auto_commit(dry_run=False)
        elif choice == "2":
            auto_commit.run_auto_commit(dry_run=True)
        elif choice == "3":
            print(json.dumps(auto_commit.config, indent=2, ensure_ascii=False))
        elif choice == "4":
            auto_commit.create_scheduled_task()
        elif choice == "5":
            print("再见!")
            break
        else:
            print("无效选择，请重试")


if __name__ == "__main__":
    sys.exit(main())