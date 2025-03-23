#!/usr/bin/env python
# backend/refresh_metadata_cli.py

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

# Ensure we can import from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.services.refresh_metadata import refresh_metadata, refresh_using_service, generate_project_manifest

# Get base directories
base_dir = current_dir  # backend directory
root_dir = parent_dir   # root project directory

# Default paths
default_projects_dir = os.path.join(root_dir, "dbt_projects_2")
default_output_dir = os.path.join(base_dir, "exports")


def check_manifest_files(projects_dir):
    """Check if manifest files exist in each project's target directory"""
    projects_dir = os.path.abspath(projects_dir)
    
    # Get all dbt project directories
    project_dirs = [d for d in os.listdir(projects_dir) 
                   if os.path.isdir(os.path.join(projects_dir, d)) 
                   and os.path.exists(os.path.join(projects_dir, d, "dbt_project.yml")) 
                   and not d.startswith('.')]
    
    result = {
        "projects": {},
        "all_exist": True
    }
    
    for project_dir in project_dirs:
        project_path = os.path.join(projects_dir, project_dir)
        manifest_path = os.path.join(project_path, "target", "manifest.json")
        manifest_exists = os.path.exists(manifest_path)
        
        result["projects"][project_dir] = {
            "exists": manifest_exists,
            "location": manifest_path if manifest_exists else None
        }
        
        if not manifest_exists:
            result["all_exist"] = False
    
    return result


def generate_manifests_for_projects(projects_dir, run_individual_script=False):
    """Generate manifest files for each project by running dbt commands"""
    projects_dir = os.path.abspath(projects_dir)
    
    if run_individual_script:
        # Run the individual projects script
        script_path = os.path.join(projects_dir, "run_individual_projects.sh")
        if os.path.exists(script_path) and os.access(script_path, os.X_OK):
            print(f"Running individual projects script: {script_path}")
            try:
                result = subprocess.run(
                    [script_path], 
                    cwd=projects_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("✅ Script executed successfully")
                    return True
                else:
                    print(f"❌ Script execution failed with return code {result.returncode}")
                    print(f"Error output: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Error running script: {str(e)}")
                return False
        else:
            print(f"❌ Individual projects script not found or not executable: {script_path}")
            # Fall back to the regular script
            regular_script_path = os.path.join(projects_dir, "run_all_projects.sh")
            if os.path.exists(regular_script_path) and os.access(regular_script_path, os.X_OK):
                print(f"Falling back to regular script: {regular_script_path}")
                try:
                    result = subprocess.run(
                        [regular_script_path], 
                        cwd=projects_dir,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print("✅ Regular script executed successfully")
                        return True
                    else:
                        print(f"❌ Regular script execution failed with return code {result.returncode}")
                        print(f"Error output: {result.stderr}")
                        return False
                except Exception as e:
                    print(f"❌ Error running regular script: {str(e)}")
                    return False
            else:
                print(f"❌ No scripts found to generate manifests")
                return False
    
    # Otherwise generate manifests for each project individually using dbt commands
    project_dirs = [d for d in os.listdir(projects_dir) 
                   if os.path.isdir(os.path.join(projects_dir, d)) 
                   and os.path.exists(os.path.join(projects_dir, d, "dbt_project.yml")) 
                   and not d.startswith('.')]
    
    if not project_dirs:
        print("No valid DBT projects found in the directory")
        return False
    
    success = True
    for project_dir in project_dirs:
        project_path = os.path.join(projects_dir, project_dir)
        print(f"Generating manifest for project: {project_dir}")
        
        # First install dependencies
        deps_command = ["dbt", "deps", "--profiles-dir", projects_dir]
        try:
            print(f"Installing dependencies for {project_dir}...")
            subprocess.run(
                deps_command,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to install dependencies for {project_dir}: {e}")
            print(f"Continuing anyway, as the dependencies might already be installed")
        
        # Then run dbt parse to generate manifest.json
        parse_command = ["dbt", "parse", "--profiles-dir", projects_dir]
        try:
            print(f"Running dbt parse for {project_dir}...")
            result = subprocess.run(
                parse_command,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            manifest_path = os.path.join(project_path, "target", "manifest.json")
            if os.path.exists(manifest_path):
                print(f"✅ Successfully generated manifest for {project_dir}")
            else:
                print(f"❌ Failed to generate manifest for {project_dir} (file not found)")
                success = False
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to run dbt parse for {project_dir}: {e}")
            success = False
    
    return success


def main():
    """Main entry point for the metadata refresh CLI"""
    parser = argparse.ArgumentParser(
        description="Refresh dbt project metadata and store it in uni_metadata.json"
    )
    
    parser.add_argument(
        "--projects-dir", 
        default=default_projects_dir, 
        help=f"Directory containing dbt projects (default: {default_projects_dir})"
    )
    
    parser.add_argument(
        "--output-dir", 
        default=default_output_dir, 
        help=f"Directory to store the exported metadata (default: {default_output_dir})"
    )
    
    parser.add_argument(
        "--use-service", 
        action="store_true", 
        help="Use MetadataService instead of direct functions"
    )
    
    parser.add_argument(
        "--force-generate", 
        action="store_true", 
        help="Force generation of manifest files (runs dbt commands)"
    )
    
    parser.add_argument(
        "--run-script",
        action="store_true",
        help="Run the run_individual_projects.sh script to generate manifests"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check if manifest files exist, don't refresh metadata"
    )
    
    args = parser.parse_args()
    
    print(f"🔄 DBT Metadata Refresh Tool")
    
    # Check if manifest files exist
    manifest_status = check_manifest_files(args.projects_dir)
    
    print(f"\nManifest Status:")
    for project_dir, status in manifest_status["projects"].items():
        icon = "✅" if status["exists"] else "❌"
        location = status["location"] if status["exists"] else "not found"
        print(f"- {project_dir}: {icon} {location}")
    
    if args.check_only:
        if manifest_status["all_exist"]:
            print("\n✅ All manifest files are present and ready for metadata refresh.")
            sys.exit(0)
        else:
            missing_projects = [p for p, status in manifest_status["projects"].items() 
                              if not status["exists"]]
            print(f"\n❌ Missing manifest files for projects: {', '.join(missing_projects)}")
            print("\nTry running with --run-script to generate manifest files properly.")
            sys.exit(1)
    
    if args.verbose:
        print(f"\nSettings:")
        print(f"- Projects directory: {os.path.abspath(args.projects_dir)}")
        print(f"- Output directory: {os.path.abspath(args.output_dir)}")
        print(f"- Using service: {args.use_service}")
        print(f"- Force generate manifests: {args.force_generate}")
        print(f"- Run script: {args.run_script}")
    
    # Generate manifest files if needed
    if not manifest_status["all_exist"] or args.force_generate:
        print("\nGenerating missing manifest files...")
        if generate_manifests_for_projects(args.projects_dir, run_individual_script=args.run_script):
            print("✅ Manifest generation completed successfully")
        else:
            print("⚠️ Some manifests may not have been generated correctly")
    
    print("\nRefreshing metadata...")
    if args.use_service:
        success = refresh_using_service()
    else:
        success = refresh_metadata(args.projects_dir, args.output_dir)
    
    if success:
        print("\n✅ Metadata refresh completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Metadata refresh failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 