import React from 'react'
import { Download, FileText, Image, RotateCcw, CheckCircle } from 'lucide-react'

const ResultDisplay = ({ result, onReset }) => {
  const { data } = result

  const handleDownload = (url, filename) => {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* 성공 메시지 */}
      <div className="flex items-center gap-3 mb-6 text-green-600">
        <CheckCircle className="w-6 h-6" />
        <div>
          <h2 className="text-xl font-semibold">영수증 생성 완료!</h2>
          <p className="text-green-700">{result.message}</p>
        </div>
      </div>

      {/* 영수증 정보 */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-gray-900 mb-3">영수증 정보</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-600">업체명:</span>
            <p className="font-medium">{data.receipt_info.business_name}</p>
          </div>
          <div>
            <span className="text-gray-600">총 금액:</span>
            <p className="font-medium text-lg text-blue-600">
              {data.receipt_info.total_amount.toLocaleString()}원
            </p>
          </div>
          <div>
            <span className="text-gray-600">메뉴 개수:</span>
            <p className="font-medium">{data.receipt_info.item_count}개</p>
          </div>
        </div>
      </div>

      {/* 다운로드 버튼들 */}
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">다운로드</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* PDF 다운로드 */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <FileText className="w-8 h-8 text-red-500" />
              <div>
                <h4 className="font-medium">PDF 파일</h4>
                <p className="text-sm text-gray-600">텍스트 검색 가능, 인쇄용</p>
              </div>
            </div>
            <button
              onClick={() => handleDownload(data.pdf_download_url, 'receipt.pdf')}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              PDF 다운로드
            </button>
          </div>

          {/* PNG 다운로드 */}
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <Image className="w-8 h-8 text-green-500" />
              <div>
                <h4 className="font-medium">PNG 이미지</h4>
                <p className="text-sm text-gray-600">300DPI, 고화질 이미지</p>
              </div>
            </div>
            <button
              onClick={() => handleDownload(data.png_download_url, 'receipt.png')}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              PNG 다운로드
            </button>
          </div>
        </div>
      </div>

      {/* 새로운 영수증 생성 */}
      <div className="mt-8 pt-6 border-t">
        <button
          onClick={onReset}
          className="btn-secondary w-full flex items-center justify-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          새로운 영수증 생성하기
        </button>
      </div>

      {/* 안내 메시지 */}
      <div className="mt-6 p-4 bg-amber-50 rounded-lg">
        <h4 className="font-medium text-amber-800 mb-2">참고사항</h4>
        <ul className="text-amber-700 text-sm space-y-1">
          <li>• 생성된 파일은 임시 파일로 일정 시간 후 자동 삭제됩니다</li>
          <li>• PDF 파일은 텍스트 검색과 복사가 가능합니다</li>
          <li>• PNG 파일은 300DPI 고화질로 인쇄에 적합합니다</li>
          <li>• 영수증에는 QR코드가 포함되어 있습니다</li>
        </ul>
      </div>
    </div>
  )
}

export default ResultDisplay