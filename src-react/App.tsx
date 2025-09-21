/**
 * 旅游路线图工具 - 主应用组件
 */

import LocationParser from './components/LocationParser'
import './App.css'

function App() {
  const handleLocationParsed = (result: any) => {
    console.log('地名解析结果:', result)
  }

  const handleError = (error: string) => {
    console.error('解析错误:', error)
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🗺️ 旅游路线图工具</h1>
        <p>智能地名解析，轻松规划旅游路线</p>
      </header>

      <main className="App-main">
        <LocationParser
          onLocationParsed={handleLocationParsed}
          onError={handleError}
          placeholder="请输入地名，如：北京市朝阳区、上海外滩、西湖"
          showHistory={true}
          showBatchMode={true}
        />
      </main>

      <footer className="App-footer">
        <p>
          基于高德地图API · 支持单个和批量地名解析 · 
          <a 
            href="https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            API文档
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App