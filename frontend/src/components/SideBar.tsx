import { useState } from 'react'

function SideBar(){
  return (
    <nav className="fixed left-0 top-0 h-screen w-64 bg-white shadow-lg">
      <div className="flex flex-col h-full">
        {/* Logo or Brand */}
        <div className="p-6 border-b border-gray-200 flex justify-center">
          <span className="text-gray-800 text-xl font-bold">Borç Takip Sistemi</span>
        </div>

        {/* Navigation Links */}
        <div className="flex flex-col py-4 space-y-2">
          <a
            href="/send-message"
            className="px-6 py-4 text-gray-700 text-lg font-bold hover:bg-blue-500 hover:text-white transition-colors duration-200 rounded-lg text-center mx-2"
          >
            Mesaj Gönder
          </a>
          <a
            href="/view-responses"
            className="px-6 py-4 text-gray-700 text-lg font-bold hover:bg-blue-500 hover:text-white transition-colors duration-200 rounded-lg text-center mx-2"
          >
            Cevap Görüntüle
          </a>
        </div>
      </div>
    </nav>
  )
}

export default SideBar