import React from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-6 h-6 text-red-500 mt-1 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-red-900 mb-2">
            오류가 발생했습니다
          </h3>
          <p className="text-red-700 mb-4">
            {message}
          </p>
          
          {onRetry && (
            <button
              onClick={onRetry}
              className="btn-primary flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              다시 시도
            </button>
          )}
        </div>
      </div>

      <div className="mt-4 p-4 bg-red-50 rounded-lg">
        <h4 className="font-medium text-red-800 mb-2">문제 해결 방법</h4>
        <ul className="text-red-700 text-sm space-y-1">
          <li>• 네이버플레이스 모바일 URL이 올바른지 확인해주세요</li>
          <li>• 인터넷 연결 상태를 확인해주세요</li>
          <li>• 잠시 후 다시 시도해주세요</li>
          <li>• 문제가 지속되면 수동으로 메뉴를 입력할 수 있습니다</li>
        </ul>
      </div>
    </div>
  )
}

export default ErrorMessage