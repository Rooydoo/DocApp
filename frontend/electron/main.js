const { app, BrowserWindow } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let mainWindow
let pythonProcess

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  // 開発時はViteサーバーに接続、本番時はビルドされたファイルを読み込む
  if (process.env.NODE_ENV === 'development' || process.argv.includes('--dev')) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function startPythonBackend() {
  // Pythonバックエンドを起動
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3'
  const backendPath = path.join(__dirname, '../../backend/main.py')

  pythonProcess = spawn(pythonPath, [backendPath], {
    cwd: path.join(__dirname, '../../backend'),
  })

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`)
  })

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`)
  })
}

app.whenReady().then(() => {
  // 本番環境ではバックエンドも起動
  if (process.env.NODE_ENV !== 'development' && !process.argv.includes('--dev')) {
    startPythonBackend()
  }

  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill()
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
