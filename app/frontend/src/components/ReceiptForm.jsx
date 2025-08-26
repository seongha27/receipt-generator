import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import DatePicker from 'react-datepicker'
import { Calendar, MapPin, Building, User, CreditCard, Hash } from 'lucide-react'
import 'react-datepicker/dist/react-datepicker.css'

const ReceiptForm = ({ onSubmit }) => {
  const { register, handleSubmit, formState: { errors }, setValue, watch } = useForm({
    defaultValues: {
      payment_datetime: new Date()
    }
  })
  
  const [paymentDate, setPaymentDate] = useState(new Date())
  const [validatingUrl, setValidatingUrl] = useState(false)

  const validateNaverUrl = async (url) => {
    if (!url.startsWith('https://m.place.naver.com/')) {
      return '네이버플레이스 모바일 URL을 입력해주세요'
    }

    try {
      setValidatingUrl(true)
      const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'
      
      const response = await fetch(`${API_BASE}/validate-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })
      
      const result = await response.json()
      return result.valid ? true : result.message
    } catch (error) {
      return 'URL 검증 중 오류가 발생했습니다'
    } finally {
      setValidatingUrl(false)
    }
  }

  const onFormSubmit = (data) => {
    const formattedData = {
      ...data,
      payment_datetime: paymentDate.toISOString()
    }
    onSubmit(formattedData)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">영수증 정보 입력</h2>
        <p className="text-gray-600">네이버플레이스 정보와 결제 정보를 입력해주세요</p>
      </div>

      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* 네이버플레이스 URL */}
        <div>
          <label className="label flex items-center gap-2">
            <MapPin className="w-4 h-4" />
            네이버플레이스 모바일 URL
          </label>
          <input
            {...register('naver_place_url', {
              required: '네이버플레이스 URL을 입력해주세요',
              validate: validateNaverUrl
            })}
            type="url"
            className="input-field"
            placeholder="https://m.place.naver.com/place/..."
            disabled={validatingUrl}
          />
          {validatingUrl && <p className="text-blue-600 text-sm mt-1">URL 검증 중...</p>}
          {errors.naver_place_url && <p className="error-text">{errors.naver_place_url.message}</p>}
          <p className="text-gray-500 text-xs mt-1">
            예시: https://m.place.naver.com/place/1234567890
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 사업자등록번호 */}
          <div>
            <label className="label flex items-center gap-2">
              <Building className="w-4 h-4" />
              사업자등록번호
            </label>
            <input
              {...register('business_number', {
                required: '사업자등록번호를 입력해주세요',
                pattern: {
                  value: /^\d{3}-\d{2}-\d{5}$/,
                  message: 'XXX-XX-XXXXX 형식으로 입력해주세요'
                }
              })}
              type="text"
              className="input-field"
              placeholder="123-45-67890"
              maxLength={12}
            />
            {errors.business_number && <p className="error-text">{errors.business_number.message}</p>}
          </div>

          {/* 상호명 */}
          <div>
            <label className="label flex items-center gap-2">
              <Building className="w-4 h-4" />
              상호명
            </label>
            <input
              {...register('business_name', {
                required: '상호명을 입력해주세요',
                minLength: { value: 2, message: '상호명은 2글자 이상이어야 합니다' }
              })}
              type="text"
              className="input-field"
              placeholder="음식점명"
            />
            {errors.business_name && <p className="error-text">{errors.business_name.message}</p>}
          </div>

          {/* 대표자명 */}
          <div>
            <label className="label flex items-center gap-2">
              <User className="w-4 h-4" />
              대표자명
            </label>
            <input
              {...register('owner_name', {
                required: '대표자명을 입력해주세요',
                minLength: { value: 2, message: '대표자명은 2글자 이상이어야 합니다' }
              })}
              type="text"
              className="input-field"
              placeholder="홍길동"
            />
            {errors.owner_name && <p className="error-text">{errors.owner_name.message}</p>}
          </div>

          {/* 결제수단 */}
          <div>
            <label className="label flex items-center gap-2">
              <CreditCard className="w-4 h-4" />
              결제수단
            </label>
            <select
              {...register('payment_method', {
                required: '결제수단을 선택해주세요'
              })}
              className="input-field"
            >
              <option value="">결제수단 선택</option>
              <option value="신용카드">신용카드</option>
              <option value="체크카드">체크카드</option>
              <option value="현금">현금</option>
              <option value="계좌이체">계좌이체</option>
              <option value="페이">간편결제</option>
            </select>
            {errors.payment_method && <p className="error-text">{errors.payment_method.message}</p>}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 결제일시 */}
          <div>
            <label className="label flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              결제일시
            </label>
            <DatePicker
              selected={paymentDate}
              onChange={(date) => {
                setPaymentDate(date)
                setValue('payment_datetime', date)
              }}
              showTimeSelect
              dateFormat="yyyy-MM-dd HH:mm"
              className="input-field"
              placeholderText="결제일시 선택"
            />
          </div>

          {/* 승인번호 */}
          <div>
            <label className="label flex items-center gap-2">
              <Hash className="w-4 h-4" />
              승인번호
            </label>
            <input
              {...register('approval_number', {
                required: '승인번호를 입력해주세요',
                minLength: { value: 4, message: '승인번호는 4자리 이상이어야 합니다' }
              })}
              type="text"
              className="input-field"
              placeholder="12345678"
            />
            {errors.approval_number && <p className="error-text">{errors.approval_number.message}</p>}
          </div>
        </div>

        <div className="pt-6 border-t">
          <button
            type="submit"
            className="btn-primary w-full py-3 text-lg"
            disabled={validatingUrl}
          >
            영수증 생성하기
          </button>
        </div>
      </form>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">사용 방법</h3>
        <ol className="text-blue-800 text-sm space-y-1">
          <li>1. 네이버플레이스에서 음식점을 검색합니다</li>
          <li>2. 모바일 버전 URL을 복사해 붙여넣습니다</li>
          <li>3. 결제 정보를 입력합니다</li>
          <li>4. 메뉴 정보가 자동으로 추출되어 영수증이 생성됩니다</li>
        </ol>
      </div>
    </div>
  )
}

export default ReceiptForm