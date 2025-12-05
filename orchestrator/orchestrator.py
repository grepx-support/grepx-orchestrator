# orchestrator/orchestrator.py

#!/usr/bin/env python3
import sys
import subprocess
import yaml
import argparse
import logging
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SCRIPT_DIR / "orchestrator.yaml"
LIBS_DIR = ROOT_DIR / "libs"
LOG_DIR = ROOT_DIR / "logs"


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_DIR / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def run_cmd(cmd, cwd=None, quiet=False):
    if quiet:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0
    else:
        result = subprocess.run(cmd, shell=True, cwd=cwd)
        return result.returncode == 0


def clone_or_update(name, url, branch, target_dir, logger):
    if target_dir.exists():
        logger.info(f"Updating {name} from {branch}...")
        success = run_cmd(f"git pull origin {branch}", cwd=target_dir)
        if success:
            logger.info(f"{name} updated")
        return success
    else:
        logger.info(f"Cloning {name} from {url}...")
        success = run_cmd(f"git clone -b {branch} {url} {target_dir}")
        if success:
            logger.info(f"{name} cloned")
        return success


def install_dependency(dep_name, dep_config, logger):
    url = dep_config['url']
    branch = dep_config.get('branch', 'main')
    path = dep_config['path']
    has_req = dep_config.get('requirements', False)

    dep_path = LIBS_DIR / path
    dep_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing dependency: {dep_name}")

    if not clone_or_update(dep_name, url, branch, dep_path, logger):
        return False

    if has_req and (dep_path / 'requirements.txt').exists():
        logger.info(f"Installing requirements for {dep_name}...")
        run_cmd(f"pip install -r {dep_path}/requirements.txt", quiet=True)

    logger.info(f"Installing {dep_name} in editable mode...")
    run_cmd(f"pip install -e {dep_path}", quiet=True)
    logger.info(f"{dep_name} installed")
    return True


def install_all_libs(config, logger):
    logger.info("=" * 50)
    logger.info("Installing all libraries")
    logger.info("=" * 50)
    
    all_deps = config.get('dependencies', {})
    if not all_deps:
        logger.info("No dependencies to install")
        return True
    
    for dep_name, dep_config in all_deps.items():
        install_dependency(dep_name, dep_config, logger)
    
    logger.info("All libraries installed")
    return True


def deploy_project(project_name, config, logger):
    if project_name not in config.get('projects', {}):
        logger.error(f"Project '{project_name}' not found in config")
        return False

    logger.info("=" * 50)
    logger.info(f"Starting deployment: {project_name}")
    logger.info("=" * 50)

    project_config = config['projects'][project_name]
    url = project_config['url']
    branch = project_config.get('branch', 'main')
    deps = project_config.get('dependencies', [])

    project_path = ROOT_DIR / project_name

    logger.info(f"Step 1: Cloning/updating project repository")
    if not clone_or_update(project_name, url, branch, project_path, logger):
        return False

    if deps:
        logger.info(f"Step 2: Installing {len(deps)} dependencies")
        all_deps = config.get('dependencies', {})
        for i, dep in enumerate(deps, 1):
            if dep in all_deps:
                logger.info(f"[{i}/{len(deps)}]")
                install_dependency(dep, all_deps[dep], logger)

    pkg_file = project_path / 'repo_specific_packages.txt'
    if pkg_file.exists():
        logger.info("Step 3: Running project-specific commands")
        with open(pkg_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    logger.info(f"> {line}")
                    run_cmd(line, cwd=project_path)

    logger.info("=" * 50)
    logger.info(f"Deployment completed: {project_name}")
    logger.info("=" * 50)
    return True


def list_projects(config):
    print("\nConfigured Projects:")
    for name, proj in config.get('projects', {}).items():
        branch = proj.get('branch', 'main')
        status = "Deployed" if (ROOT_DIR / name).exists() else "Not Deployed"
        print(f"  - {name} (branch: {branch}) [{status}]")


def main():
    parser = argparse.ArgumentParser(description='Orchestrator')
    parser.add_argument('-p', '--project', help='Project name to deploy')
    parser.add_argument('-l', '--list', action='store_true', help='List all projects')
    parser.add_argument('-a', '--all', action='store_true', help='Deploy all projects')
    parser.add_argument('--install-libs', action='store_true', help='Install all libraries')

    args = parser.parse_args()

    if not CONFIG_FILE.exists():
        print(f"Error: Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)

    logger = setup_logging()

    if args.list:
        list_projects(config)
    elif args.install_libs:
        install_all_libs(config, logger)
    elif args.all:
        for project_name in config.get('projects', {}).keys():
            deploy_project(project_name, config, logger)
    elif args.project:
        deploy_project(args.project, config, logger)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()