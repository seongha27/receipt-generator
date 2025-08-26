import React, { useState } from 'react'
import Modal from 'react-modal'
import { Plus, Minus, Save, X } from 'lucide-react'

Modal.setAppElement('#root')

const ManualMenuModal = ({ isOpen, onSubmit, onCancel }) => {
  const [menuItems, setMenuItems] = useState([{ name: '', price: '', options: '' }])

  const addMenuItem = () => {
    setMenuItems([...menuItems, { name: '', price: '', options: '' }])
  }

  const removeMenuItem = (index) => {
    if (menuItems.length > 1) {
      const newItems = menuItems.filter((_, i) => i !== index)
      setMenuItems(newItems)
    }
  }

  const updateMenuItem = (index, field, value) => {
    const newItems = [...menuItems]
    newItems[index][field] = value
    setMenuItems(newItems)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const validItems = menuItems
      .filter(item => item.name.trim() && item.price)
      .map(item => ({
        name: item.name.trim(),
        price: parseInt(item.price.replace(/[^0-9]/g, '')),
        options: item.options.trim() || null
      }))

    if (validItems.length === 0) {
      alert('최소 1개의 메뉴를 입력해주세요')
      return
    }

    onSubmit(validItems)
  }

  const formatPrice = (value) => {
    const numbers = value.replace(/[^0-9]/g, '')
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  }

  const getTotalAmount = () => {
    return menuItems
      .filter(item => item.price)
      .reduce((total, item) => {
        const price = parseInt(item.price.replace(/[^0-9]/g, '')) || 0
        return total + price
      }, 0)
  }

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onCancel}
      className="max-w-2xl mx-auto mt-16 bg-white rounded-lg shadow-xl p-0 max-h-[80vh] overflow-hidden"
      overlayClassName="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center px-4"
    >
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">메뉴 수동 입력</h2>
            <p className="text-gray-600 text-sm mt-1">
              메뉴 정보를 찾을 수 없어 수동으로 입력이 필요합니다
            </p>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col h-full">
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {menuItems.map((item, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">메뉴 {index + 1}</h3>
                  {menuItems.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeMenuItem(index)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="label">메뉴명 *</label>
                    <input
                      type="text"
                      value={item.name}
                      onChange={(e) => updateMenuItem(index, 'name', e.target.value)}
                      className="input-field"
                      placeholder="예: 김치찌개"
                      required
                    />
                  </div>

                  <div>
                    <label className="label">가격 *</label>
                    <input
                      type="text"
                      value={item.price}
                      onChange={(e) => {
                        const formatted = formatPrice(e.target.value)
                        updateMenuItem(index, 'price', formatted)
                      }}
                      className="input-field"
                      placeholder="예: 8,000"
                      required
                    />
                  </div>
                </div>

                <div className="mt-3">
                  <label className="label">옵션 (선택사항)</label>
                  <input
                    type="text"
                    value={item.options}
                    onChange={(e) => updateMenuItem(index, 'options', e.target.value)}
                    className="input-field"
                    placeholder="예: 곱빼기, 매운맛"
                  />
                </div>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={addMenuItem}
            className="btn-secondary w-full mt-4 flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            메뉴 추가
          </button>

          {getTotalAmount() > 0 && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <div className="flex justify-between items-center text-lg font-semibold">
                <span>예상 총액:</span>
                <span className="text-blue-600">{getTotalAmount().toLocaleString()}원</span>
              </div>
              <p className="text-blue-800 text-sm mt-1">
                * 부가세 10%가 별도로 추가됩니다
              </p>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onCancel}
              className="btn-secondary flex-1"
            >
              취소
            </button>
            <button
              type="submit"
              className="btn-primary flex-1 flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              영수증 생성
            </button>
          </div>
        </div>
      </form>
    </Modal>
  )
}

export default ManualMenuModal