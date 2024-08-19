#!/usr/bin/env python3

import os
import sys
import json
import argparse
from collections import defaultdict
import re
import logging
import mimetypes

"""
Project Structure and Dependency Analyzer

This script analyzes the structure and dependencies of a project directory.

Usage:
    python project_analyzer.py [project_dir] [-o OUTPUT] [-d DEPTH]

Arguments:
    project_dir    Project directory to analyze (default: current directory)

Options:
    -o, --output   Output file name (default: project_name_analysis.txt)
    -d, --depth    Maximum depth for directory analysis

Examples:
    python project_analyzer.py /path/to/project
    python project_analyzer.py -o my_analysis.txt
    python project_analyzer.py /path/to/project -d 3

The script will generate a detailed analysis of the project structure,
including file types, dependencies, and configuration files. The analysis
is written to the specified output file or a default file named after the project.
"""

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of ignored directories
IGNORED_DIRS = {
    '.git', '.svn', '.hg',  # Version control
    '.terraform', 'terraform.tfstate.d',  # Terraform
    '__pycache__', '.pytest_cache', '.mypy_cache',  # Python
    'node_modules', 'bower_components',  # JavaScript
    '.venv', 'venv', 'env',  # Python virtual environments
    '.idea', '.vscode',  # IDEs
    'build', 'dist', 'target',  # Build outputs
    'logs', 'tmp', 'temp',  # Temporary and log files
}

# List of ignored files
IGNORED_FILES = {
    # General
    '.DS_Store', 'Thumbs.db', 'desktop.ini',
    '.gitignore', '.gitattributes',
    'LICENSE', 'CHANGELOG.md',
    
    # Terraform
    '.terraform.lock.hcl', '*.tfstate', '*.tfstate.backup', '*.tfvars',
    
    # Python
    '*.pyc', '*.pyo', '*.pyd', '*.egg-info',
    
    # JavaScript
    'package-lock.json', 'yarn.lock', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
    
    # Java
    '*.class', '*.jar', '*.war',
    
    # C#
    '*.suo', '*.user', '*.userosscache', '*.sln.docstates',
    
    # Visual Studio Code
    '.vscode/*',
    
    # JetBrains IDEs
    '.idea/*', '*.iml',
    
    # Logs
    '*.log',
    
    # OS generated
    '.DS_Store?', '._*', '.Spotlight-V100', '.Trashes', 'ehthumbs.db', 'Thumbs.db',
}

def is_ignored_file(file_name):
    """Check if a file should be ignored based on its name."""
    return any(file_name.endswith(pattern.lstrip('*')) or file_name == pattern for pattern in IGNORED_FILES)

def is_binary(file_path):
    """Check if a file is binary based on its content and extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and not mime_type.startswith('text'):
        return True

    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(8192)
            return b'\0' in chunk
    except IOError:
        logging.warning(f"Unable to read file: {file_path}")
        return True

def get_file_extension(file_path):
    """Get the file extension."""
    return os.path.splitext(file_path)[1].lower()

def read_file(file_path):
    """Read a file with proper encoding."""
    encodings = ['utf-8', 'latin-1', 'ascii']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                logging.info(f"Successfully read file: {file_path} with encoding: {encoding}")
                return content
        except UnicodeDecodeError:
            continue
    logging.warning(f"Unable to decode file: {file_path}")
    return None

def analyze_dependencies(file_path, content):
    """Analyze file dependencies."""
    dependencies = set()
    file_extension = get_file_extension(file_path)
    
    if file_extension == '.json' and 'package.json' in file_path:
        try:
            package_data = json.loads(content)
            dependencies.update(package_data.get('dependencies', {}).keys())
            dependencies.update(package_data.get('devDependencies', {}).keys())
        except json.JSONDecodeError:
            logging.warning(f"Unable to parse JSON in file: {file_path}")
    elif file_extension == '.txt' and 'requirements.txt' in file_path:
        dependencies.update(line.strip().split('==')[0] for line in content.splitlines() if line.strip())
    elif file_extension in ['.py', '.js', '.java', '.tf', '.sh']:
        if file_extension == '.py':
            dependencies.update(re.findall(r'^\s*(?:from|import)\s+(\w+)', content, re.MULTILINE))
        elif file_extension == '.js':
            dependencies.update(re.findall(r'(?:import|require)\s*\(\s*[\'"](.+?)[\'"]', content))
        elif file_extension == '.java':
            dependencies.update(re.findall(r'import\s+([\w.]+)', content))
        elif file_extension == '.tf':
            dependencies.update(re.findall(r'source\s*=\s*[\'"](.+?)[\'"]', content))
            dependencies.update(re.findall(r'module\s*"(.+?)"', content))
        elif file_extension == '.sh':
            dependencies.update(re.findall(r'(?:apt-get install|yum install)\s+(.+?)(?:\s|$)', content))
    
    logging.info(f"Found {len(dependencies)} dependencies in file: {file_path}")
    return dependencies

def parse_env_file(content):
    """Parse .env file content."""
    env_vars = {}
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    return env_vars

def analyze_config_file(file_path, content):
    """Analyze configuration files like package.json and .env."""
    config_info = {}
    file_name = os.path.basename(file_path)

    if file_name == 'package.json':
        try:
            package_data = json.loads(content)
            config_info['name'] = package_data.get('name')
            config_info['version'] = package_data.get('version')
            config_info['main'] = package_data.get('main')
            config_info['scripts'] = package_data.get('scripts')
            config_info['dependencies'] = package_data.get('dependencies')
            config_info['devDependencies'] = package_data.get('devDependencies')
        except json.JSONDecodeError:
            logging.warning(f"Unable to parse package.json: {file_path}")
    elif file_name == '.env':
        env_vars = parse_env_file(content)
        config_info['environment_variables'] = list(env_vars.keys())
    elif file_name.endswith('.tf'):
        # Basic Terraform file analysis
        config_info['resources'] = re.findall(r'resource\s*"(\w+)"\s*"', content)
        config_info['data_sources'] = re.findall(r'data\s*"(\w+)"\s*"', content)
        config_info['modules'] = re.findall(r'module\s*"(.+?)"', content)

    return config_info

def analyze_project(base_dir, max_depth=None, script_name=None, output_file=None):
    """Analyze the project structure and file contents."""
    project_structure = {'dirs': [], 'files': {}}
    all_dependencies = set()
    file_count = 0
    dir_count = 0
    language_stats = defaultdict(int)
    file_types = defaultdict(int)
    config_files = {}
    
    for root, dirs, files in os.walk(base_dir):
        if max_depth is not None:
            current_depth = root[len(base_dir):].count(os.path.sep)
            if current_depth > max_depth:
                logging.info(f"Reached max depth at {root}, skipping further subdirectories")
                dirs[:] = []
                continue
        
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith('.')]
        dir_count += len(dirs)
        
        relative_path = os.path.relpath(root, base_dir)
        current_level = project_structure
        if relative_path != '.':
            for part in relative_path.split(os.path.sep):
                if part not in current_level['dirs']:
                    current_level['dirs'].append(part)
                    current_level[part] = {'dirs': [], 'files': {}}
                current_level = current_level[part]
        
        for file in files:
            if is_ignored_file(file) or file == script_name or file == output_file:
                logging.info(f"Skipping ignored file: {file}")
                continue
            file_count += 1
            file_path = os.path.join(root, file)
            file_extension = get_file_extension(file_path)
            
            language_stats[file_extension] += 1
            file_types[file_extension] += 1
            
            if is_binary(file_path):
                logging.info(f"Skipping binary file content: {file_path}")
                current_level['files'][file] = "Binary file"
                continue
            
            content = read_file(file_path)
            if content is not None:
                current_level['files'][file] = content
                file_dependencies = analyze_dependencies(file_path, content)
                all_dependencies.update(file_dependencies)
                
                if file in ['package.json', '.env'] or file.endswith('.tf'):
                    config_files[file] = analyze_config_file(file_path, content)
            else:
                current_level['files'][file] = "Error reading file: Unable to decode"

    logging.info(f"Analyzed {file_count} files in {dir_count} directories")
    return project_structure, all_dependencies, file_count, dir_count, language_stats, file_types, config_files

def generate_tree_string(structure, prefix="", is_last=True):
    """Generate a string representation of the project tree."""
    lines = []
    if 'dirs' in structure:
        dirs = structure['dirs']
        files = structure['files'].keys()
        
        for i, item in enumerate(dirs + list(files)):
            is_last_item = i == len(dirs) + len(files) - 1
            connector = "└── " if is_last_item else "├── "
            lines.append(f"{prefix}{connector}{item}")
            
            if item in structure:
                extension = "    " if is_last_item else "│   "
                lines.extend(generate_tree_string(structure[item], prefix + extension, is_last_item))
    
    return lines

def generate_ai_prompt(project_name, file_count, dir_count, language_stats, dependencies, project_structure, file_types, config_files):
    """Generate a detailed AI prompt describing the project."""
    top_languages = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    language_summary = ", ".join(f"{ext[1:]} ({count} files)" for ext, count in top_languages if ext != '.')
    
    tree_structure = "\n".join(generate_tree_string(project_structure))

    file_type_summary = "\n".join(f"  {ext}: {count}" for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True))

    config_summary = ""
    if 'package.json' in config_files:
        pkg = config_files['package.json']
        config_summary += f"\npackage.json summary:\n"
        config_summary += f"  Name: {pkg.get('name')}\n"
        config_summary += f"  Version: {pkg.get('version')}\n"
        config_summary += f"  Main: {pkg.get('main')}\n"
        config_summary += f"  Scripts: {', '.join(pkg.get('scripts', {}).keys())}\n"
        config_summary += f"  Dependencies: {', '.join(pkg.get('dependencies', {}).keys())}\n"
        config_summary += f"  Dev Dependencies: {', '.join(pkg.get('devDependencies', {}).keys())}\n"

    if '.env' in config_files:
        env_vars = config_files['.env']['environment_variables']
        config_summary += f"\n.env file contains {len(env_vars)} environment variables:\n"
        config_summary += f"  {', '.join(env_vars)}\n"

    terraform_files = [f for f in config_files if f.endswith('.tf')]
    if terraform_files:
        config_summary += "\nTerraform configuration summary:\n"
        for tf_file in terraform_files:
            config_summary += f"  {tf_file}:\n"
            tf_config = config_files[tf_file]
            config_summary += f"    Resources: {', '.join(tf_config.get('resources', []))}\n"
            config_summary += f"    Data Sources: {', '.join(tf_config.get('data_sources', []))}\n"
            config_summary += f"    Modules: {', '.join(tf_config.get('modules', []))}\n"

    prompt = f"""Analyze the following project in depth:

PROJECT OVERVIEW:
Project Name: {project_name}
Total Files: {file_count}
Total Directories: {dir_count}
Main Languages/File Types: {language_summary}
Key Dependencies: {', '.join(sorted(dependencies)[:20])}

FILE TYPES:
{file_type_summary}

CONFIGURATION FILES:{config_summary}

DETAILED ANALYSIS INSTRUCTIONS:
You are an AI assistant specializing in code analysis and software architecture. Your task is to provide a comprehensive analysis of this project based on the information provided. Please consider the following aspects in your analysis:

1. Project Architecture:
   - Identify the overall architectural pattern (e.g., microservices, monolithic, serverless)
   - Analyze the project structure and how it reflects the architecture
   - Evaluate the separation of concerns and modularity

2. Technology Stack:
   - List the main technologies, frameworks, and languages used
   - Assess the choice of technologies and their suitability for the project

3. Infrastructure and Deployment:
   - Identify any infrastructure-as-code elements (e.g., Terraform files)
   - Analyze the deployment strategy and environment setup

4. Security Considerations:
   - Highlight any security measures implemented in the code
   - Identify potential security risks or areas for improvement

5. Scalability and Performance:
   - Evaluate how well the project is designed to scale
   - Identify any performance optimization techniques used

6. Code Quality and Best Practices:
   - Assess adherence to coding standards and best practices
   - Identify areas where code quality could be improved

7. Testing and Quality Assurance:
   - Analyze the testing approach (unit tests, integration tests, etc.)
   - Suggest improvements in the testing strategy if necessary

8. Documentation:
   - Evaluate the quality and completeness of documentation
   - Suggest areas where documentation could be improved

9. Dependencies and Third-party Integrations:
   - Analyze the use of external dependencies and their management
   - Identify any potential risks associated with third-party integrations

10. Unique Features or Patterns:
    - Highlight any unique or interesting code patterns or architectural decisions
    - Discuss their potential benefits or drawbacks

PROJECT STRUCTURE OVERVIEW:
{tree_structure}

Based on this information, please provide:
1. A comprehensive analysis of the project's architecture and codebase
2. Identification of the main functionalities and purpose of the project
3. Potential areas for improvement or optimization
4. Any security concerns or best practices that should be implemented
5. Suggestions for scaling this project
6. Overall strengths and weaknesses of the project

Your analysis should be detailed, insightful, and provide actionable recommendations for improving the project.
"""
    return prompt

def write_structure(structure, file, indent=""):
    """Write the project structure to the output file."""
    if 'dirs' in structure:
        for dir_name in structure['dirs']:
            file.write(f"{indent}{dir_name}/\n")
            write_structure(structure[dir_name], file, indent + "  ")
        
        for file_name, file_content in structure['files'].items():
            file.write(f"{indent}{file_name}\n")
            file.write(f"{indent}  File contents:\n")
            if file_content == "Binary file":
                file.write(f"{indent}    {file_content}\n")
            elif isinstance(file_content, str):
                for line in file_content.splitlines():
                    file.write(f"{indent}    {line}\n")
            file.write(f"{'-'*40}\n")

def write_project_analysis(project_structure, dependencies, output_file, project_name, file_count, dir_count, language_stats, file_types, config_files):
    """Write the project analysis to a file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            ai_prompt = generate_ai_prompt(project_name, file_count, dir_count, language_stats, dependencies, project_structure, file_types, config_files)
            out_file.write(ai_prompt)
            
            out_file.write("\n\nDETAILED PROJECT STRUCTURE:\n\n")
            write_structure(project_structure, out_file)
            
            out_file.write("\nPROJECT DEPENDENCIES:\n")
            for dep in sorted(dependencies):
                out_file.write(f"  {dep}\n")
            
            out_file.write("\nCONFIGURATION FILES:\n")
            for file_name, config_info in config_files.items():
                out_file.write(f"\n{file_name}:\n")
                for key, value in config_info.items():
                    out_file.write(f"  {key}: {value}\n")
        
        logging.info(f"Successfully wrote project analysis to {output_file}")
    except Exception as e:
        logging.error(f"Error writing project analysis: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Project Structure and Dependency Analyzer")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory to analyze (default: current directory)")
    parser.add_argument("-o", "--output", help="Output file name (default: project_name_analysis.txt)")
    parser.add_argument("-d", "--depth", type=int, help="Maximum depth for directory analysis")
    args = parser.parse_args()

    base_directory = os.path.abspath(args.project_dir)
    project_name = os.path.basename(base_directory)
    
    if args.output:
        output_filename = args.output
    else:
        output_filename = f"{project_name}_analysis.txt"
    
    script_name = os.path.basename(__file__)
    
    try:
        logging.info(f"Starting analysis of project: {base_directory}")
        project_structure, dependencies, file_count, dir_count, language_stats, file_types, config_files = analyze_project(base_directory, args.depth, script_name, output_filename)
        write_project_analysis(project_structure, dependencies, output_filename, project_name, file_count, dir_count, language_stats, file_types, config_files)
        logging.info(f"Project analysis has been written to: {output_filename}")
        logging.info(f"Total files analyzed: {file_count}")
        logging.info(f"Total directories analyzed: {dir_count}")
        logging.info("File types found:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            logging.info(f"  {ext}: {count}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        logging.info("The script will attempt to save partial results.")
        try:
            write_project_analysis(project_structure, dependencies, output_filename, project_name, file_count, dir_count, language_stats, file_types, config_files)
            logging.info(f"Partial analysis has been written to: {output_filename}")
        except Exception as write_error:
            logging.error(f"Failed to write partial results: {str(write_error)}")

if __name__ == "__main__":
    main()
