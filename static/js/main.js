let selectedFile = null;
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeFile = document.getElementById("removeFile");
const convertBtn = document.getElementById("convertBtn");
const convertText = document.getElementById("convertText");
const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const messageContainer = document.getElementById("messageContainer");
const selectFileBtn = document.getElementById("selectFileBtn");

document.addEventListener("DOMContentLoaded", function () {
  initializeEventListeners();
  checkServerHealth();
});

function initializeEventListeners() {
  selectFileBtn.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    fileInput.click();
  });
  dropZone.addEventListener("click", function (e) {
    if (e.target !== selectFileBtn && !selectFileBtn.contains(e.target)) {
      fileInput.click();
    }
  });

  dropZone.addEventListener("dragover", handleDragOver);
  dropZone.addEventListener("dragleave", handleDragLeave);
  dropZone.addEventListener("drop", handleDrop);
  fileInput.addEventListener("change", handleFileSelect);
  removeFile.addEventListener("click", clearFile);
  convertBtn.addEventListener("click", convertFile);
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });
}
function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function handleDragOver(e) {
  dropZone.classList.add("drag-active");
}

function handleDragLeave(e) {
  dropZone.classList.remove("drag-active");
}

function handleDrop(e) {
  dropZone.classList.remove("drag-active");
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFile(files[0]);
  }
}

function handleFileSelect(e) {
  if (e.target.files.length > 0) {
    handleFile(e.target.files[0]);
  }
}

function handleFile(file) {
  if (!file.name.toLowerCase().endsWith(".docx")) {
    showMessage("Solo se permiten archivos .docx", "error");
    return;
  }

  if (file.size > 16 * 1024 * 1024) {
    showMessage("El archivo es demasiado grande. Máximo 16MB.", "error");
    return;
  }

  selectedFile = file;
  showFileInfo(file);
  enableConvertButton();
  clearMessages();
}

function showFileInfo(file) {
  fileName.textContent = file.name;
  fileSize.textContent = formatFileSize(file.size);
  fileInfo.classList.remove("hidden");
}

function clearFile() {
  selectedFile = null;
  fileInfo.classList.add("hidden");
  fileInput.value = "";
  disableConvertButton();
  clearMessages();
}

function enableConvertButton() {
  convertBtn.disabled = false;
  convertText.textContent = "Convertir a PDF";
  convertBtn.classList.remove("opacity-50", "cursor-not-allowed");
}

function disableConvertButton() {
  convertBtn.disabled = true;
  convertText.textContent = "Selecciona un archivo para continuar";
  convertBtn.classList.add("opacity-50", "cursor-not-allowed");
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function showMessage(message, type = "info") {
  const colors = {
    success: "bg-green-50 text-green-800 border-green-200",
    error: "bg-red-50 text-red-800 border-red-200",
    info: "bg-blue-50 text-blue-800 border-blue-200",
  };

  const icons = {
    success:
      '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
    error:
      '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
    info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>',
  };

  messageContainer.innerHTML = `
        <div class="flex items-center p-4 border rounded-lg ${colors[type]}">
            <div class="flex-shrink-0 mr-3">
                ${icons[type]}
            </div>
            <div class="text-sm font-medium">
                ${message}
            </div>
        </div>
    `;
}

function clearMessages() {
  messageContainer.innerHTML = "";
}

function updateProgress(percent, text) {
  progressBar.style.width = percent + "%";
  progressText.textContent = text;
}

async function convertFile() {
  if (!selectedFile) return;

  progressContainer.classList.remove("hidden");
  convertBtn.disabled = true;
  convertText.textContent = "Convirtiendo...";
  clearMessages();

  try {
    updateProgress(10, "Preparando archivo...");

    const formData = new FormData();
    formData.append("file", selectedFile);

    updateProgress(30, "Subiendo archivo...");

    const response = await fetch("/convert", {
      method: "POST",
      body: formData,
    });

    updateProgress(70, "Procesando conversión...");

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Error en el servidor");
    }

    updateProgress(90, "Preparando descarga...");

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = selectedFile.name.replace(/\.docx$/i, ".pdf");
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    updateProgress(100, "¡Conversión completada!");
    showMessage("¡PDF generado y descargado exitosamente!", "success");
    setTimeout(() => {
      progressContainer.classList.add("hidden");
      updateProgress(0, "Preparando...");
    }, 3000);
  } catch (error) {
    console.error("Error:", error);
    showMessage("Error al convertir: " + error.message, "error");
    progressContainer.classList.add("hidden");
  } finally {
    convertBtn.disabled = false;
    convertText.textContent = "Convertir a PDF";
  }
}
function checkServerHealth() {
  fetch("/health")
    .then((response) => response.json())
    .then((data) => {
      console.log("Estado del servidor:", data);
    })
    .catch((error) => {
      console.error("Error verificando servidor:", error);
    });
}
