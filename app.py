from flask import Flask, render_template, request, send_file
from docx2pdf import convert
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route('/')
def index():
    return render_template('index.html')  


@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    if 'file' not in request.files:
        return "No se ha subido ningún archivo", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No se ha seleccionado ningún archivo", 400
    
   
    word_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(word_path)
    
  
    pdf_path = word_path.replace('.docx', '.pdf')
    convert(word_path, pdf_path)
    
   
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)