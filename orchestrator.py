#!/usr/bin/env python3
import os
import sys
import subprocess
import yaml
import argparse
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "orchestrator.yaml"
REPOS_DIR = SCRIPT_DIR / "repos"
LIBS_DIR = SCRIPT_DIR / "libs"
LOG_DIR = SCRIPT_DIR / "logs"


def log(level, msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    colors = {'INFO': '\033[0;34m', 'OK': '\033[0;32m', 'WARN': '\033[1;33m', 'ERROR': '\033[0;31m'}
    color = colors.get(level, '')

    print(f"[{timestamp}] {color}[{level}]\033[0m {msg}")

    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] [{level}] {msg}\n")

    sys.stdout.flush()


def run_cmd(cmd, cwd=None, quiet=False):
    if quiet:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0
    else:
        result = subprocess.run(cmd, shell=True, cwd=cwd)
        return result.returncode == 0


def clone_or_update(name, url, branch, target_dir):
    if target_dir.exists():
        log('INFO', f"Updating {name} from {branch}...")
        success = run_cmd(f"git pull origin {branch}", cwd=target_dir)
        if success:
            log('OK', f"{name} updated")
        return success
    else:
        log('INFO', f"Cloning {name} from {url}...")
        success = run_cmd(f"git clone -b {branch} {url} {target_dir}")
        if success:
            log('OK', f"{name} cloned")
        return success


def install_dependency(dep_name, dep_config):
    url = dep_config['url']
    branch = dep_config.get('branch', 'main')
    path = dep_config['path']
    has_req = dep_config.get('requirements', False)

    dep_path = LIBS_DIR / path
    dep_path.parent.mkdir(parents=True, exist_ok=True)

    log('INFO', f"Processing dependency: {dep_name}")

    if not clone_or_update(dep_name, url, branch, dep_path):
        return False

    if has_req and (dep_path / 'requirements.txt').exists():
        log('INFO', f"Installing requirements for {dep_name}...")
        run_cmd(f"pip install -r {dep_path}/requirements.txt", quiet=True)

    log('INFO', f"Installing {dep_name} in editable mode...")
    run_cmd(f"pip install -e {dep_path}", quiet=True)
    log('OK', f"{dep_name} installed")
    return True


def deploy_project(project_name, config):
    if project_name not in config.get('projects', {}):
        log('ERROR', f"Project '{project_name}' not found in config")
        return False

    print(f"\n{'=' * 50}")
    log('INFO', f"Starting deployment: {project_name}")
    print(f"{'=' * 50}\n")

    project_config = config['projects'][project_name]
    url = project_config['url']
    branch = project_config.get('branch', 'main')
    deps = project_config.get('dependencies', [])

    project_path = REPOS_DIR / project_name
    REPOS_DIR.mkdir(exist_ok=True)

    log('INFO', f"Step 1: Cloning/updating project repository")
    if not clone_or_update(project_name, url, branch, project_path):
        return False

    if deps:
        print()
        log('INFO', f"Step 2: Installing {len(deps)} dependencies")
        all_deps = config.get('dependencies', {})
        for i, dep in enumerate(deps, 1):
            if dep in all_deps:
                print(f"\n[{i}/{len(deps)}]")
                install_dependency(dep, all_deps[dep])

    pkg_file = project_path / 'repo_specific_packages.txt'
    if pkg_file.exists():
        print()
        log('INFO', "Step 3: Running project-specific commands")
        with open(pkg_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    log('INFO', f"> {line}")
                    run_cmd(line, cwd=project_path)

    print(f"\n{'=' * 50}")
    log('OK', f"Deployment completed: {project_name}")
    print(f"{'=' * 50}\n")
    return True


def list_projects(config):
    print("\nConfigured Projects:")
    for name, proj in config.get('projects', {}).items():
        branch = proj.get('branch', 'main')
        status = "Deployed" if (REPOS_DIR / name).exists() else "Not Deployed"
        print(f"  - {name} (branch: {branch}) [{status}]")


def main():
    parser = argparse.ArgumentParser(description='Orchestrator')
    parser.add_argument('-p', '--project', help='Project name to deploy')
    parser.add_argument('-l', '--list', action='store_true', help='List all projects')
    parser.add_argument('-a', '--all', action='store_true', help='Deploy all projects')

    args = parser.parse_args()

    if not CONFIG_FILE.exists():
        log('ERROR', f"Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)

    if args.list:
        list_projects(config)
    elif args.all:
        for project_name in config.get('projects', {}).keys():
            deploy_project(project_name, config)
    elif args.project:
        deploy_project(args.project, config)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()