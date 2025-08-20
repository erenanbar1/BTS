import { useState } from 'react'
import ViewExcel from './ViewExcel'

function UploadExcel() {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDragIn = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragOut = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      setFile(files[0])
    }
  }

  return (
    <div>
      <div
        className={`w-full max-w-xl mx-auto p-8 border-2 border-dashed rounded-lg 
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'} 
          transition-colors duration-200`}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="text-center">
          {file ? (
            <p className="text-lg text-gray-700">
              Seçilen dosya: <span className="font-semibold">{file.name}</span>
            </p>
          ) : (
            <>
              <p className="text-xl text-gray-600 font-semibold mb-2">
                Excel dosyanızı buraya sürükleyip bırakın
              </p>
              <p className="text-gray-500">
                veya buraya tıklayarak dosya seçin
              </p>
            </>
          )}
        </div>
      </div>

      <ViewExcel file={file} />
    </div>
  )
}

export default UploadExcel