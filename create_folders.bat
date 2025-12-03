@echo off
echo Creating project folder structure...

REM Main directories
mkdir config\credentials
mkdir database\models
mkdir repositories
mkdir schemas
mkdir services
mkdir ui\components
mkdir ui\dashboard
mkdir ui\personnel\hospital
mkdir ui\personnel\staff
mkdir ui\personnel\assignment
mkdir ui\personnel\history
mkdir ui\outpatient\slot_management
mkdir ui\outpatient\assignment
mkdir ui\mail\draft
mkdir ui\mail\template
mkdir ui\document\create
mkdir ui\document\template
mkdir ui\settings
mkdir ui\copilot
mkdir llm\prompts
mkdir ga
mkdir utils
mkdir tests\test_repositories
mkdir tests\test_services
mkdir tests\test_ga
mkdir tests\fixtures
mkdir alembic\versions
mkdir logs
mkdir backups
mkdir data

REM Create __init__.py files for Python packages
type nul > config\__init__.py
type nul > database\__init__.py
type nul > database\models\__init__.py
type nul > repositories\__init__.py
type nul > schemas\__init__.py
type nul > services\__init__.py
type nul > ui\__init__.py
type nul > ui\components\__init__.py
type nul > ui\dashboard\__init__.py
type nul > ui\personnel\__init__.py
type nul > ui\personnel\hospital\__init__.py
type nul > ui\personnel\staff\__init__.py
type nul > ui\personnel\assignment\__init__.py
type nul > ui\personnel\history\__init__.py
type nul > ui\outpatient\__init__.py
type nul > ui\outpatient\slot_management\__init__.py
type nul > ui\outpatient\assignment\__init__.py
type nul > ui\mail\__init__.py
type nul > ui\mail\draft\__init__.py
type nul > ui\mail\template\__init__.py
type nul > ui\document\__init__.py
type nul > ui\document\create\__init__.py
type nul > ui\document\template\__init__.py
type nul > ui\settings\__init__.py
type nul > ui\copilot\__init__.py
type nul > llm\__init__.py
type nul > ga\__init__.py
type nul > utils\__init__.py
type nul > tests\__init__.py

REM Create .gitignore
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo venv/
echo ENV/
echo .venv
echo 
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo 
echo # Environment
echo .env
echo 
echo # Database
echo data/*.db
echo data/*.db-journal
echo 
echo # Logs
echo logs/*.log
echo 
echo # Backups
echo backups/*.zip
echo backups/*.sql
echo 
echo # Google API Credentials
echo config/credentials/*.json
echo 
echo # Testing
echo .pytest_cache/
echo .coverage
echo htmlcov/
) > .gitignore

echo.
echo Folder structure created successfully!
echo.
echo Next steps:
echo 1. Copy .env.example to .env and configure
echo 2. Place Google API credentials in config/credentials/
echo 3. Start coding!
pause