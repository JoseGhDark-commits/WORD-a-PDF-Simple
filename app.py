"""
Conversor de Word a PDF - Servidor Flask
Autor: JoseGhDark-commits
"""

from flask import Flask, render_template, request, send_file, jsonify, flash
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename
from pathlib import Path
import webbrowser
import threading
import time

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'wordtopdf-dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def convert_docx_to_pdf(input_path, output_path):
    """Convertir DOCX a PDF usando el mejor método disponible"""
    try:
        try:
            from docx2pdf import convert
            convert(input_path, output_path)
            return True, "Conversión exitosa con docx2pdf"
        except ImportError:
            pass
        except Exception as e:
            print(f"Error con docx2pdf: {e}")
        
        try:
            import pypandoc
            pypandoc.convert_file(input_path, 'pdf', outputfile=output_path)
            return True, "Conversión exitosa con pypandoc"
        except ImportError:
            pass
        except Exception as e:
            print(f"Error con pypandoc: {e}")
        
        try:
            from docx import Document
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            
            doc = Document(input_path)
            pdf_doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    para = Paragraph(paragraph.text, styles['BodyText'])
                    story.append(para)
                    story.append(Spacer(1, 12))
            
            pdf_doc.build(story)
            return True, "Conversión exitosa con método básico"
            
        except ImportError as e:
            missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
            return False, f"Falta instalar: pip install python-docx reportlab (Error: {missing_module})"
        except Exception as e:
            return False, f"Error en conversión: {e}"
            
    except Exception as e:
        return False, f"Error general: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_file('static/w.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/convert', methods=['POST'])
def convert_file():
    ensure_upload_folder()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Solo se permiten archivos .docx'}), 400
    
    try:
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        temp_filename = f"{timestamp}_{filename}"
        input_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(input_path)
        
        pdf_filename = filename.rsplit('.', 1)[0] + '.pdf'
        output_path = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{pdf_filename}")
        
        success, message = convert_docx_to_pdf(input_path, output_path)
        
        if os.path.exists(input_path):
            os.remove(input_path)
        
        if success:
            return send_file(
                output_path,
                as_attachment=True,
                download_name=pdf_filename,
                mimetype='application/pdf'
            )
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error procesando archivo: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Verificar estado de las dependencias"""
    status = {
        'docx2pdf': False,
        'pypandoc': False,
        'basic': False
    }
    
    try:
        import docx2pdf
        status['docx2pdf'] = True
    except ImportError:
        pass
    
    try:
        import pypandoc
        status['pypandoc'] = True
    except ImportError:
        pass
    
    try:
        from docx import Document
        from reportlab.pdfgen import canvas
        status['basic'] = True
    except ImportError:
        pass
    
    return jsonify(status)

def cleanup_temp_files():
    """Limpiar archivos temporales antiguos"""
    if os.path.exists(UPLOAD_FOLDER):
        current_time = time.time()
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getctime(file_path)
                if file_age > 3600:  # 1 hora
                    try:
                        os.remove(file_path)
                    except:
                        pass

def open_browser():
    """Abrir navegador después de un breve delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

def check_dependencies():
    """Verificar dependencias al inicio"""
    missing = []
    
    try:
        import flask
        print("✅ Flask - OK")
    except ImportError:
        missing.append("Flask")
    
    try:
        import docx
        print("✅ python-docx - OK")
    except ImportError:
        missing.append("python-docx")
    
    try:
        import reportlab
        print("✅ reportlab - OK")
    except ImportError:
        missing.append("reportlab")
    
    try:
        import docx2pdf
        print("✅ python-docx2pdf - OK")
    except ImportError:
        print("⚠️  python-docx2pdf - No disponible (opcional)")
    
    try:
        import pypandoc
        print("✅ pypandoc - OK")
    except ImportError:
        print("⚠️  pypandoc - No disponible (opcional)")
    
    if missing:
        print(f"\n❌ Faltan dependencias: {', '.join(missing)}")
        print("💡 Ejecuta: pip install " + " ".join(missing))
        return False
    
    return True

if __name__ == '__main__':
    ensure_upload_folder()
    cleanup_temp_files()
    
    print("Iniciando Conversor Word a PDF...")
    print("Verificando dependencias...")
    
    if not check_dependencies():
        print("\n❌ No se puede iniciar el servidor sin las dependencias básicas")
        input("Presiona Enter para salir...")
        exit(1)
    
    print("\n Servidor ejecutándose en: http://localhost:5000")
    print("Presiona Ctrl+C para detener")
    
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=False, host='localhost', port=5000)