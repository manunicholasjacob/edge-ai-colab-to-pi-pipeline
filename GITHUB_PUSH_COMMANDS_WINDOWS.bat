@echo off
REM GitHub Push Commands for SoftwareX Repository (Windows)
REM Repository: https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline

echo ==========================================
echo GitHub Repository Setup and Push
echo ==========================================
echo.

REM Navigate to project directory
cd /d "c:\Users\manun\Downloads\Adaptive_Edge_Cloud_Inference_with_ONNX_Deployment__A_Reproducible_Colab_Raspberry_Pi_Pipeline_on_CIFAR_100_and_SVHN (2)"

echo Step 1: Creating directory structure...
if not exist "paper" mkdir paper
if not exist "src" mkdir src
if not exist "experiments" mkdir experiments
if not exist "models" mkdir models
if not exist "results" mkdir results
if not exist "figures" mkdir figures
if not exist "environment" mkdir environment
if not exist "docs" mkdir docs
if not exist "examples" mkdir examples
if not exist "tests" mkdir tests
echo   Done creating directories

echo.
echo Step 2: Moving files to proper locations...

REM Move paper
if exist "main_softwarex.pdf" (
    move /Y main_softwarex.pdf paper\
    echo   Moved main_softwarex.pdf to paper/
)

REM Move environment files (if not already moved)
if exist "requirements.txt" (
    if not exist "environment\requirements.txt" (
        move /Y requirements.txt environment\
        echo   Moved requirements.txt to environment/
    )
)

if exist "environment.yml" (
    if not exist "environment\environment.yml" (
        move /Y environment.yml environment\
        echo   Moved environment.yml to environment/
    )
)

echo.
echo Step 3: Initializing Git repository...

REM Check if .git exists
if not exist ".git" (
    git init
    echo   Git repository initialized
) else (
    echo   Git repository already exists
)

REM Add remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline.git
    echo   Remote 'origin' added
) else (
    echo   Remote 'origin' already exists
)

echo.
echo Step 4: Staging files...
git add .
echo   All files staged

echo.
echo Step 5: Creating commit...
git commit -m "Initial commit: SoftwareX submission-ready repository" -m "- Add comprehensive README with installation and usage" -m "- Add MIT License" -m "- Add architecture and reproducibility documentation" -m "- Add example scripts for running experiments" -m "- Add paper PDF (main_softwarex.pdf)" -m "- Add environment specifications (requirements.txt, environment.yml)" -m "- Structure repository for SoftwareX compliance" -m "- Add .gitignore for Python projects" -m "- Include cover letter and submission materials"

echo.
echo Step 6: Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ==========================================
echo Repository pushed to GitHub successfully!
echo ==========================================
echo.
echo Repository URL: https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline
echo.
echo Next steps:
echo 1. Verify repository on GitHub web interface
echo 2. Check that all files are visible
echo 3. Test clone and installation
echo 4. Submit to SoftwareX portal
echo.
pause
