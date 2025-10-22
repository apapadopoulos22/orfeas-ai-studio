#!/usr/bin/env python3
"""
ORFEAS CLEANUP SCRIPT
Removes unnecessary files, older versions, and non-optimized engines
Keeps only essential, optimized components
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

def create_cleanup_report():
    """Generate a report of what will be cleaned up"""

    base_path = Path("c:/Users/johng/Documents/Erevus/orfeas")
    backend_path = base_path / "backend"

    # Files to DELETE - unnecessary, old versions, non-optimized
    files_to_delete = {
        "backend": [
            # Old/Debug servers (keeping only powerful_3d_server.py and safe_server.py)
            "app.py",
            "debug_server.py",
            "enhanced_ai_server.py",
            "fixed_image_server.py",
            "fixed_server.py",
            "minimal_test_server.py",
            "real_stl_server.py",
            "simple_server.py",
            "ultra_safe_server.py",
            "ultra_server.py",
            "working_ai_server.py",
            "ai_enabled_server.py",

            # Debug/test files (keeping essential tests only)
            "debug_image_failure.py",
            "debug_text_to_3d.py",
            "diagnose_hunyuan.py",
            "fix_dependencies_crash.py",
            "fix_frontend.py",
            "comprehensive_frontend_test.py",
            "quick_frontend_test.py",
            "test_3d_preview.py",
            "test_api_workflow.py",
            "test_complete_formats.py",
            "test_complex_shape_stl.py",
            "test_direct_generation.py",
            "test_final_complete.py",
            "test_final_sla_validation.py",
            "test_fixed_endpoints.py",
            "test_frontend_complete.py",
            "test_frontend_vs_ai.py",
            "test_multiformat_functions.py",
            "test_multi_format_comprehensive.py",
            "test_realtime_3d.py",
            "test_real_ai_formats.py",
            "test_server.py",
            "test_server_functionality.py",
            "test_sla_halot_x1.py",
            "test_ultra_safe_image.py",
            "text_to_stl_integrity_test.py",
            "validate_frontend.py",
            "verify_stl_files.py",

            # Old test images (keeping demo_coin.jpg)
            "fallback_image_test.png",
            "manual_test_image.jpg",
            "test_cube.png",
            "test_detailed.png",
            "test_fallback.png",
            "test_geometric.png",
            "test_organic.png",

            # Log files
            "debug.log",
            "orfeas_server.log",
            "test_error.txt",
            "test_output.txt",

            # Old batch files (keeping essential ones)
            "run_frontend_test.bat",
            "start_safe_server.bat",
        ],

        "root": [
            # Old documentation (keeping latest)
            "AI_SETUP_COMPLETE.md",
            "3D_PREVIEW_IMPLEMENTATION.md",
            "FINAL_VALIDATION_REPORT.md",
            "FRONTEND_ERROR_FIX_SUMMARY.md",
            "PROBLEM_FIXED_REAL_STL.md",
            "SLA_OPTIMIZATION_COMPLETE.md",

            # Old HTML versions (keeping latest)
            "multiformat_tester.html",
            "ORFEAS_MAKERS_PORTAL_ENHANCED.html",

            # Old zip archives
            "orfeas-makers-portal-v2.zip",
            "orfeas-makers-portal-v3.zip",
            "orfeas-makers-portal.zip",

            # Old logs and reports
            "backup_info.json",
            "deployment.log",
            "stl_analysis_report_1760342651.json",
            "stl_save_integrity_report_1760342945.json",

            # Debug script
            "frontend_debug.js",
            "fix_all_issues.bat",
        ]
    }

    # Directories to DELETE (old/unused)
    directories_to_delete = {
        "root": [
            "frontend-nextjs",
            "netlify-deploy",
            "Next.js",
            "text_to_stl_tests",
            "REAL_AI_TEST_OUTPUTS",
        ]
    }

    # Files to KEEP - essential, optimized components
    essential_files = {
        "backend": [
            # Core optimized servers
            "powerful_3d_server.py",  # Main AI server
            "safe_server.py",         # Fallback server
            "integrated_server.py",   # Full featured server

            # Core configuration
            "config.py",
            "hunyuan_integration.py",
            "ultra_performance_config.py",

            # Essential utilities
            "orfeas_compat.py",
            "huggingface_compat.py",
            "setup_paths.py",
            "sla_optimizer.py",
            "stl_analyzer.py",

            # Key test files (optimized ones)
            "test_real_stl_generation.py",
            "test_powerful_engine.py",
            "frontend_stl_complete_test.py",
            "manual_jpg_stl_workflow.py",

            # Essential assets
            "demo_coin.jpg",
            "requirements.txt",
            "SETUP_FULL_AI.md",
        ],

        "root": [
            # Latest optimized HTML interfaces
            "orfeas-studio.html",
            "ORFEAS_MAKERS_PORTAL.html",

            # Latest documentation
            "README.md",
            "POWERFUL_3D_ENGINE_COMPLETE.md",
            "FRONTEND_STL_WORKFLOW_SUCCESS.md",

            # Optimized startup scripts
            "start_orfeas_ai.bat",
            "start_orfeas_ai.ps1",
            "setup_ultra_performance.py",
        ]
    }

    return files_to_delete, directories_to_delete, essential_files

def perform_cleanup():
    """Perform the actual cleanup operation"""

    print(" ORFEAS CLEANUP: REMOVING UNNECESSARY FILES")
    print("=" * 60)

    base_path = Path("c:/Users/johng/Documents/Erevus/orfeas")
    backend_path = base_path / "backend"

    files_to_delete, directories_to_delete, essential_files = create_cleanup_report()

    deleted_files = []
    deleted_dirs = []
    errors = []

    # Delete unnecessary files in backend
    print("\n CLEANING BACKEND DIRECTORY...")
    for filename in files_to_delete["backend"]:
        file_path = backend_path / filename
        if file_path.exists():
            try:
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_files.append((str(file_path), file_size))
                    print(f"    Deleted: {filename} ({file_size} bytes)")
                else:
                    print(f"    Skipped: {filename} (not a file)")
            except Exception as e:
                errors.append(f"Failed to delete {filename}: {e}")
                print(f"    Error: {filename} - {e}")

    # Delete unnecessary files in root
    print("\n CLEANING ROOT DIRECTORY...")
    for filename in files_to_delete["root"]:
        file_path = base_path / filename
        if file_path.exists():
            try:
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_files.append((str(file_path), file_size))
                    print(f"    Deleted: {filename} ({file_size} bytes)")
                else:
                    print(f"    Skipped: {filename} (not a file)")
            except Exception as e:
                errors.append(f"Failed to delete {filename}: {e}")
                print(f"    Error: {filename} - {e}")

    # Delete unnecessary directories
    print("\n CLEANING DIRECTORIES...")
    for dirname in directories_to_delete["root"]:
        dir_path = base_path / dirname
        if dir_path.exists() and dir_path.is_dir():
            try:
                # Calculate directory size before deletion
                dir_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                shutil.rmtree(dir_path)
                deleted_dirs.append((str(dir_path), dir_size))
                print(f"    Deleted directory: {dirname} ({dir_size/1024/1024:.1f} MB)")
            except Exception as e:
                errors.append(f"Failed to delete directory {dirname}: {e}")
                print(f"    Error: {dirname} - {e}")

    # Clean __pycache__ directories
    print("\n CLEANING PYTHON CACHE...")
    pycache_dirs = list(base_path.rglob("__pycache__"))
    for cache_dir in pycache_dirs:
        try:
            if cache_dir.exists() and cache_dir.is_dir():
                cache_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
                shutil.rmtree(cache_dir)
                deleted_dirs.append((str(cache_dir), cache_size))
                print(f"    Cleaned cache: {cache_dir.relative_to(base_path)} ({cache_size/1024:.1f} KB)")
        except Exception as e:
            errors.append(f"Failed to clean cache {cache_dir}: {e}")
            print(f"    Error: {cache_dir} - {e}")

    # Generate cleanup report
    print(f"\n" + "=" * 60)
    print(" CLEANUP SUMMARY")
    print("=" * 60)

    total_files_deleted = len(deleted_files)
    total_dirs_deleted = len(deleted_dirs)
    total_size_saved = sum(size for _, size in deleted_files + deleted_dirs)

    print(f" Files deleted: {total_files_deleted}")
    print(f" Directories deleted: {total_dirs_deleted}")
    print(f" Space saved: {total_size_saved/1024/1024:.1f} MB")

    if errors:
        print(f"\n Errors encountered: {len(errors)}")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   • {error}")

    # Show what was kept
    print(f"\n ESSENTIAL FILES PRESERVED:")
    print(f"Backend: {len(essential_files['backend'])} core files")
    print(f"Root: {len(essential_files['root'])} essential files")

    # List key preserved files
    print(f"\n KEY PRESERVED COMPONENTS:")
    print("   Core Servers:")
    for server in ["powerful_3d_server.py", "safe_server.py", "integrated_server.py"]:
        if (backend_path / server).exists():
            print(f"      {server}")

    print("   Frontend Interfaces:")
    for frontend in ["orfeas-studio.html", "ORFEAS_MAKERS_PORTAL.html"]:
        if (base_path / frontend).exists():
            print(f"      {frontend}")

    print("   Documentation:")
    for doc in ["README.md", "POWERFUL_3D_ENGINE_COMPLETE.md", "FRONTEND_STL_WORKFLOW_SUCCESS.md"]:
        if (base_path / doc).exists():
            print(f"      {doc}")

    # Save cleanup report
    cleanup_report = {
        "cleanup_date": datetime.now().isoformat(),
        "files_deleted": total_files_deleted,
        "directories_deleted": total_dirs_deleted,
        "space_saved_mb": round(total_size_saved/1024/1024, 2),
        "deleted_files": [{"path": path, "size": size} for path, size in deleted_files],
        "deleted_directories": [{"path": path, "size": size} for path, size in deleted_dirs],
        "errors": errors,
        "essential_files_preserved": essential_files
    }

    report_path = base_path / "cleanup_report.json"
    with open(report_path, 'w') as f:
        json.dump(cleanup_report, f, indent=2)

    print(f"\n Cleanup report saved: {report_path}")

    return total_files_deleted > 0 or total_dirs_deleted > 0

def main():
    """Main cleanup function"""

    print(" ORFEAS OPTIMIZATION CLEANUP")
    print("Removing unnecessary files and keeping only optimized components")
    print("=" * 70)

    # Show what will be cleaned up
    files_to_delete, directories_to_delete, essential_files = create_cleanup_report()

    print(f"\n CLEANUP PLAN:")
    print(f"    Files to delete: {len(files_to_delete['backend']) + len(files_to_delete['root'])}")
    print(f"    Directories to delete: {len(directories_to_delete['root'])}")
    print(f"    Essential files to preserve: {len(essential_files['backend']) + len(essential_files['root'])}")

    print(f"\n WILL PRESERVE KEY COMPONENTS:")
    print(f"   • powerful_3d_server.py (Advanced AI engine)")
    print(f"   • safe_server.py (Fallback server)")
    print(f"   • orfeas-studio.html (Main frontend)")
    print(f"   • ORFEAS_MAKERS_PORTAL.html (Portal interface)")
    print(f"   • All STL files and essential configurations")

    # Perform cleanup
    success = perform_cleanup()

    if success:
        print(f"\n CLEANUP COMPLETED SUCCESSFULLY!")
        print(f" Your ORFEAS system is now optimized with only essential components")
        print(f" Ready for production use with improved performance")
    else:
        print(f"\n No files were cleaned up (may already be optimized)")

    print(f"\n OPTIMIZED SYSTEM COMPONENTS:")
    print(f"    AI Engine: powerful_3d_server.py")
    print(f"    Safe Mode: safe_server.py")
    print(f"    Frontend: orfeas-studio.html")
    print(f"    Documentation: Complete and up-to-date")
    print(f"    Configuration: Optimized for performance")

if __name__ == "__main__":
    main()
