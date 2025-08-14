@echo off
echo ========================================
echo    Conversor Word a PDF - Flask
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    echo 💡 Descarga Python desde: https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Actualizar pip primero
echo 🔧 Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias una por una para mejor control
echo Instalando dependencias esenciales...
pip install Flask==2.3.3
pip install python-docx==0.8.11
pip install reportlab==4.0.7
pip install Werkzeug==2.3.7
echo.

echo Instalando dependencias opcionales...
pip install python-docx2pdf==0.1.8
pip install pypandoc==1.12
echo.

REM Verificar instalación
echo Verificando instalación...
python -c "import flask; print('✅ Flask OK')"
python -c "import docx; print('✅ python-docx OK')"
python -c "import reportlab; print('✅ reportlab OK')"
echo.

echo  Iniciando servidor web...
echo  Se abrirá automáticamente en tu navegador
echo  Presiona Ctrl+C para detener
echo.
python app.py

pause