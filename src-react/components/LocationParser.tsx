/**
 * 地名解析组件
 * 提供地名解析的用户界面
 */

import React, { useState, useCallback } from 'react'
import type { LocationInput } from '../types/location'
import { useLocationParser, useLocationAutoComplete, useLocationHistory } from '../hooks/useLocationParser'

// 组件属性类型
interface LocationParserProps {
  onLocationParsed?: (result: any) => void
  onError?: (error: string) => void
  placeholder?: string
  className?: string
  showHistory?: boolean
  showBatchMode?: boolean
}

/**
 * 地名解析主组件
 */
export function LocationParser({
  onLocationParsed,
  onError,
  placeholder = '请输入地名，如：北京市朝阳区',
  className = '',
  showHistory = true,
  showBatchMode = true
}: LocationParserProps) {
  const [mode, setMode] = useState<'single' | 'batch'>('single')
  const [batchInput, setBatchInput] = useState('')
  
  // 使用地名解析 Hook
  const {
    isLoading,
    error,
    result,
    batchResult,
    parseLocation,
    parseBatch,
    retry
  } = useLocationParser()
  
  // 使用自动完成 Hook
  const {
    input,
    setInput,
    correctedInput,
    suggestions,
    selectSuggestion,
    clearInput
  } = useLocationAutoComplete()
  
  // 使用历史记录 Hook
  const { history, addToHistory, clearHistory } = useLocationHistory()
  
  // 处理单个地名解析
  const handleSingleParse = useCallback(async () => {
    if (!input.trim()) return
    
    const locationInput: LocationInput = {
      name: correctedInput || input,
      timeout: 5000,
      useCache: true
    }
    
    await parseLocation(locationInput)
  }, [input, correctedInput, parseLocation])
  
  // 处理批量地名解析
  const handleBatchParse = useCallback(async () => {
    if (!batchInput.trim()) return
    
    await parseBatch(batchInput)
  }, [batchInput, parseBatch])
  
  // 处理解析结果
  React.useEffect(() => {
    if (result?.success && result.location) {
      addToHistory(result.location)
      onLocationParsed?.(result)
    }
    
    if (batchResult && batchResult.summary && batchResult.summary.successful > 0) {
      // 将成功解析的地名添加到历史记录
      batchResult.results.forEach(item => {
        if (item.success && item.location) {
          addToHistory(item.location)
        }
      })
      onLocationParsed?.(batchResult)
    }
  }, [result, batchResult, addToHistory, onLocationParsed])
  
  // 处理错误
  React.useEffect(() => {
    if (error) {
      onError?.(error)
    }
  }, [error, onError])
  
  return (
    <div className={`location-parser ${className}`}>
      {/* 模式切换 */}
      {showBatchMode && (
        <div className="mode-switcher">
          <button
            className={`mode-btn ${mode === 'single' ? 'active' : ''}`}
            onClick={() => setMode('single')}
          >
            单个解析
          </button>
          <button
            className={`mode-btn ${mode === 'batch' ? 'active' : ''}`}
            onClick={() => setMode('batch')}
          >
            批量解析
          </button>
        </div>
      )}
      
      {/* 单个地名解析 */}
      {mode === 'single' && (
        <div className="single-mode">
          <div className="input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={placeholder}
              className="location-input"
              onKeyPress={(e) => e.key === 'Enter' && handleSingleParse()}
            />
            
            {/* 输入建议 */}
            {suggestions.length > 0 && (
              <div className="suggestions">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="suggestion-item"
                    onClick={() => selectSuggestion(suggestion)}
                  >
                    {suggestion}
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* 输入修正提示 */}
          {correctedInput && correctedInput !== input && (
            <div className="correction-hint">
              建议修正为: <span className="corrected-text">{correctedInput}</span>
            </div>
          )}
          
          <div className="action-buttons">
            <button
              onClick={handleSingleParse}
              disabled={isLoading || !input.trim()}
              className="parse-btn primary"
            >
              {isLoading ? '解析中...' : '解析地名'}
            </button>
            
            <button
              onClick={clearInput}
              className="clear-btn"
            >
              清空
            </button>
          </div>
        </div>
      )}
      
      {/* 批量地名解析 */}
      {mode === 'batch' && (
        <div className="batch-mode">
          <textarea
            value={batchInput}
            onChange={(e) => setBatchInput(e.target.value)}
            placeholder="请输入多个地名，每行一个：&#10;北京市朝阳区&#10;上海市浦东新区&#10;广州市天河区"
            className="batch-input"
            rows={6}
          />
          
          <div className="action-buttons">
            <button
              onClick={handleBatchParse}
              disabled={isLoading || !batchInput.trim()}
              className="parse-btn primary"
            >
              {isLoading ? '批量解析中...' : '批量解析'}
            </button>
            
            <button
              onClick={() => setBatchInput('')}
              className="clear-btn"
            >
              清空
            </button>
          </div>
        </div>
      )}
      
      {/* 错误显示 */}
      {error && (
        <div className="error-message">
          <span className="error-text">{error}</span>
          <button onClick={retry} className="retry-btn">
            重试
          </button>
        </div>
      )}
      
      {/* 解析结果 */}
      {result?.success && result.location && (
        <LocationResult location={result.location} />
      )}
      
      {/* 批量解析结果 */}
      {batchResult && (
        <BatchLocationResult result={batchResult} />
      )}
      
      {/* 历史记录 */}
      {showHistory && history.length > 0 && (
        <LocationHistory
          history={history}
          onClearHistory={clearHistory}
          onSelectLocation={(location) => {
            setInput(location.name)
            setMode('single')
          }}
        />
      )}
    </div>
  )
}

/**
 * 单个地名解析结果组件
 */
function LocationResult({ location }: { location: any }) {
  return (
    <div className="location-result">
      <h3>解析结果</h3>
      <div className="result-content">
        <div className="location-info">
          <div className="location-name">{location.name}</div>
          <div className="location-address">{location.address}</div>
          <div className="location-coords">
            经度: {location.coordinate.longitude.toFixed(6)}, 
            纬度: {location.coordinate.latitude.toFixed(6)}
          </div>
          {location.level && (
            <div className="location-level">级别: {location.level}</div>
          )}
        </div>
        
        {location.district && (
          <div className="district-info">
            <h4>行政区划</h4>
            <div>省份: {location.district.province}</div>
            <div>城市: {location.district.city}</div>
            <div>区县: {location.district.district}</div>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * 批量解析结果组件
 */
function BatchLocationResult({ result }: { result: any }) {
  const successCount = result.results.filter((r: any) => r.success).length
  const totalCount = result.results.length
  
  return (
    <div className="batch-result">
      <h3>批量解析结果</h3>
      <div className="result-summary">
        成功: {successCount} / {totalCount}
      </div>
      
      <div className="result-list">
        {result.results.map((item: any, index: number) => (
          <div key={index} className={`result-item ${item.success ? 'success' : 'error'}`}>
            <div className="query-text">{item.query}</div>
            {item.success ? (
              <div className="location-brief">
                {item.data.name} - {item.data.coordinate.longitude.toFixed(4)}, {item.data.coordinate.latitude.toFixed(4)}
              </div>
            ) : (
              <div className="error-text">{item.error?.message}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * 历史记录组件
 */
function LocationHistory({ 
  history, 
  onClearHistory, 
  onSelectLocation 
}: { 
  history: any[]
  onClearHistory: () => void
  onSelectLocation: (location: any) => void
}) {
  return (
    <div className="location-history">
      <div className="history-header">
        <h3>解析历史</h3>
        <button onClick={onClearHistory} className="clear-history-btn">
          清空历史
        </button>
      </div>
      
      <div className="history-list">
        {history.map((location, index) => (
          <div
            key={index}
            className="history-item"
            onClick={() => onSelectLocation(location)}
          >
            <div className="history-name">{location.name}</div>
            <div className="history-coords">
              {location.coordinate.longitude.toFixed(4)}, {location.coordinate.latitude.toFixed(4)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default LocationParser