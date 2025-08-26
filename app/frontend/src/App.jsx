import React, { useState } from 'react'
import ReceiptForm from './components/ReceiptForm'
import ManualMenuModal from './components/ManualMenuModal'
import ResultDisplay from './components/ResultDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorMessage from './components/ErrorMessage'
import { FileText, Receipt } from 'lucide-react'

function App() {
  const [step, setStep] = useState('form') // 'form', 'manual', 'result'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [formData, setFormData] = useState(null)
  const [result, setResult] = useState(null)

  const handleFormSubmit = async (data) => {
    setFormData(data)
    setLoading(true)
    setError(null)

    try {
      const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'
      
      const response = await fetch(`${API_BASE}/generate-receipt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      const result = await response.json()

      if (!response.ok) {
        if (result.detail?.code === 'MANUAL_INPUT_REQUIRED') {
          setStep('manual')
          return
        }
        throw new Error(result.detail?.message || '영수증 생성에 실패했습니다.')
      }

      setResult(result)
      setStep('result')
    } catch (err) {
      setError(err.message || '네트워크 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleManualSubmit = async (menuItems) => {
    if (!formData) return
    
    setLoading(true)
    setError(null)

    try {
      const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'
      
      const response = await fetch(`${API_BASE}/generate-receipt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          manual_menu: { menu_items: menuItems }
        }),
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.detail?.message || '영수증 생성에 실패했습니다.')
      }

      setResult(result)
      setStep('result')
    } catch (err) {
      setError(err.message || '네트워크 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const resetApp = () => {
    setStep('form')
    setFormData(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <Receipt className="w-8 h-8 text-primary-500" />
            <h1 className="text-2xl font-bold text-gray-900">영수증 생성기</h1>
          </div>
          <p className="text-gray-600 mt-2">네이버플레이스 정보로 영수증을 자동 생성합니다</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {loading && <LoadingSpinner />}
        
        {error && (
          <ErrorMessage 
            message={error} 
            onRetry={step === 'form' ? null : () => setError(null)}
          />
        )}

        {step === 'form' && !loading && (
          <ReceiptForm onSubmit={handleFormSubmit} />
        )}

        {step === 'manual' && (
          <ManualMenuModal
            isOpen={true}
            onSubmit={handleManualSubmit}
            onCancel={() => setStep('form')}
          />
        )}

        {step === 'result' && result && (
          <ResultDisplay 
            result={result} 
            onReset={resetApp}
          />
        )}
      </main>

      <footer className="bg-white border-t mt-16">
        <div className="max-w-4xl mx-auto px-4 py-6 text-center text-gray-500 text-sm">
          <p>&copy; 2024 AdSketch. 모든 권리 보유.</p>
        </div>
      </footer>
    </div>
  )
}

export default App