import React from 'react'
import { Loader2 } from 'lucide-react'

const LoadingSpinner = () => {
  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            영수증 생성 중...
          </h3>
          <p className="text-gray-600">
            네이버플레이스에서 메뉴 정보를 가져오고 있습니다.
          </p>
          <p className="text-gray-500 text-sm mt-2">
            잠시만 기다려주세요. 최대 30초가 소요될 수 있습니다.
          </p>
        </div>
      </div>

      <div className="mt-8 space-y-3">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-primary-500 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
        </div>
        
        <div className="flex justify-between text-xs text-gray-500">
          <span>네이버플레이스 접속 중</span>
          <span>60%</span>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner