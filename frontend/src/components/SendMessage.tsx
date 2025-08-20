import { useState } from 'react'
import UploadExcel from './UploadExcel'

function SendMessage() {
  const [file, setFile] = useState<File | null>(null)

  const handleSendMessage = () => {
    // Handle sending message logic here
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        {/* Step Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            <div className={`flex items-center ${!file ? 'text-blue-500' : 'text-green-500'}`}>
              <span className="w-8 h-8 flex items-center justify-center rounded-full border-2 border-current font-bold">
                1
              </span>
              <span className="ml-2 font-semibold">Excel Yükle</span>
            </div>
            <div className="w-16 h-0.5 bg-gray-300"></div>
            <div className={`flex items-center ${file ? 'text-blue-500' : 'text-gray-400'}`}>
              <span className="w-8 h-8 flex items-center justify-center rounded-full border-2 border-current font-bold">
                2
              </span>
              <span className="ml-2 font-semibold">Mesaj Gönder</span>
            </div>
          </div>
        </div>

        {/* Upload Excel Component */}
        <UploadExcel onFileSelect={setFile} />

        {/* Send Message Button */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={handleSendMessage}
            disabled={!file}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors duration-200
              ${file 
                ? 'bg-blue-500 hover:bg-blue-600' 
                : 'bg-gray-400 cursor-not-allowed'
              }`}
          >
            Mesaj Gönder
          </button>
        </div>
      </div>
    </div>
  )
}

export default SendMessage