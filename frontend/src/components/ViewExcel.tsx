import { useEffect, useState } from 'react'
import * as XLSX from 'xlsx'

interface ExcelData {
  headers: string[];
  rows: any[];
}

interface ViewExcelProps {
  file: File | null;
}

function ViewExcel({ file }: ViewExcelProps) {
  const [excelData, setExcelData] = useState<ExcelData | null>(null)

  useEffect(() => {
    const readExcelFile = async () => {
      if (!file) {
        setExcelData(null)
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        const data = new Uint8Array(e.target?.result as ArrayBuffer)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
        const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 })
        
        const headers = jsonData[0] as string[]
        const rows = jsonData.slice(1)
        
        setExcelData({ headers, rows })
      }
      reader.readAsArrayBuffer(file)
    }

    readExcelFile()
  }, [file])

  if (!excelData) return null

  return (
    <div className="mt-8 overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-300">
        <thead>
          <tr>
            {excelData.headers.map((header, index) => (
              <th key={index} className="px-6 py-3 border-b border-gray-300 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {excelData.rows.slice(0, 5).map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell: any, cellIndex: number) => (
                <td key={cellIndex} className="px-6 py-4 border-b border-gray-300 text-sm">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-sm text-gray-500 text-center">
        İlk 5 satır gösteriliyor
      </p>
    </div>
  )
}

export default ViewExcel