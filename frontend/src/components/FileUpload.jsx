import { useState } from 'react'
import Papa from 'papaparse'
import { FileText, Trash2, UploadCloud } from 'lucide-react'

function FileUpload({ file, onChange, onError, disabled = false }) {
  const [dragging, setDragging] = useState(false)
  const [previewCount, setPreviewCount] = useState(0)

  function validateAndSet(nextFile) {
    if (!nextFile) {
      return
    }

    if (!nextFile.name.toLowerCase().endsWith('.csv')) {
      onError('Solo se permite subir archivos con extension .csv.')
      return
    }

    Papa.parse(nextFile, {
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        if (!result.meta.fields?.includes('comentario')) {
          onError("El CSV debe incluir una columna llamada 'comentario'.")
          return
        }

        setPreviewCount(result.data.length)
        onChange(nextFile)
      },
      error: () => onError('No se pudo leer el archivo CSV en el navegador.'),
    })
  }

  function handleDrop(event) {
    event.preventDefault()
    setDragging(false)
    validateAndSet(event.dataTransfer.files?.[0])
  }

  function clearFile() {
    setPreviewCount(0)
    onChange(null)
  }

  return (
    <div
      className={`dropzone ${dragging ? 'dragging' : ''}`}
      onDragOver={(event) => {
        event.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      <UploadCloud size={34} />
      <div>
        <strong>Arrastra un CSV aqui</strong>
        <p>Debe contener la columna comentario.</p>
      </div>

      <label className="secondary-button file-button">
        Seleccionar archivo
        <input
          type="file"
          accept=".csv,text/csv"
          disabled={disabled}
          onChange={(event) => validateAndSet(event.target.files?.[0])}
        />
      </label>

      {file ? (
        <div className="file-preview">
          <FileText size={18} />
          <span>{file.name}</span>
          <small>{previewCount} filas detectadas</small>
          <button type="button" onClick={clearFile} aria-label="Eliminar archivo">
            <Trash2 size={16} />
          </button>
        </div>
      ) : null}
    </div>
  )
}

export default FileUpload

