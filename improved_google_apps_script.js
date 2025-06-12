
function doPost(e) {
  try {
    // Детальное логирование
    console.log('=== NEW REQUEST ===');
    console.log('Timestamp:', new Date().toISOString());
    console.log('Request parameters:', e.parameter);
    console.log('Content length:', e.postData ? e.postData.length : 'No postData');
    
    const data = e.parameter;
    
    // Проверяем токен
    const expectedToken = "mySecret123"; // Ваш секретный токен
    if (data.token !== expectedToken) {
      console.log('❌ Unauthorized access attempt with token:', data.token);
      return createJsonResponse({
        ok: false, 
        error: "Unauthorized - invalid token"
      });
    }
    
    console.log('✅ Token verified successfully');
    
    // Если это ping тест
    if (data.test === "ping") {
      console.log('📡 Ping test request received');
      return createJsonResponse({
        ok: true, 
        message: "Webhook is working perfectly",
        timestamp: new Date().toISOString(),
        script_version: "1.2"
      });
    }
    
    // Если это простой тест
    if (data.test === "hello") {
      console.log('👋 Hello test request received');
      return createJsonResponse({
        ok: true, 
        message: "Hello from Google Apps Script",
        received_data: data
      });
    }
    
    // ВАЖНО: Замените на ID вашей таблицы Google Sheets
    // ID можно найти в URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
    const SPREADSHEET_ID = "12kdk6h4cEs7q31ZjoUMvpAIhF3OC384XRRg6LtZKVdo"; // ЗАМЕНИТЕ НА ВАШ ID!
    
    console.log('📊 Opening spreadsheet with ID:', SPREADSHEET_ID);
    
    let spreadsheet;
    try {
      spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
      console.log('✅ Spreadsheet opened successfully');
    } catch (error) {
      console.log('❌ Failed to open spreadsheet:', error.toString());
      return createJsonResponse({
        ok: false, 
        error: "Failed to open spreadsheet. Check SPREADSHEET_ID: " + error.toString()
      });
    }
    
    // Получаем первый лист или создаем если нет
    let sheet;
    try {
      sheet = spreadsheet.getActiveSheet();
      if (!sheet) {
        sheet = spreadsheet.getSheetByName('Sheet1');
      }
      if (!sheet) {
        sheet = spreadsheet.insertSheet('Sheet1');
        console.log('📄 Created new sheet: Sheet1');
      }
      console.log('✅ Sheet accessed:', sheet.getName());
    } catch (error) {
      console.log('❌ Failed to access sheet:', error.toString());
      return createJsonResponse({
        ok: false, 
        error: "Failed to access sheet: " + error.toString()
      });
    }
    
    // Проверяем и создаем заголовки если нужно
    try {
      const firstRow = sheet.getRange(1, 1, 1, 8).getValues()[0];
      if (!firstRow[0] || firstRow[0] === '') {
        const headers = ['Date', 'Ticker', 'FIGI', 'Side', 'Price', 'Qty', 'Fees', 'Timestamp'];
        sheet.getRange(1, 1, 1, 8).setValues([headers]);
        console.log('✅ Headers added to sheet');
      }
    } catch (error) {
      console.log('⚠️ Warning: Could not check/add headers:', error.toString());
    }
    
    // Подготавливаем данные для записи
    const rowData = [
      data.date || new Date().toISOString().split('T')[0],
      data.ticker || "",
      data.figi || "",
      data.side || "",
      parseFloat(data.price) || 0,
      parseInt(data.qty) || 0,
      parseFloat(data.fees) || 0,
      new Date().toISOString() // timestamp записи
    ];
    
    console.log('📝 Prepared row data:', rowData);
    
    // Записываем данные
    try {
      sheet.appendRow(rowData);
      console.log('✅ Row appended successfully');
    } catch (error) {
      console.log('❌ Failed to append row:', error.toString());
      return createJsonResponse({
        ok: false, 
        error: "Failed to write to sheet: " + error.toString()
      });
    }
    
    // Успешный ответ
    const response = {
      ok: true, 
      message: "Trade logged successfully",
      data: rowData,
      spreadsheet_id: SPREADSHEET_ID,
      sheet_name: sheet.getName(),
      timestamp: new Date().toISOString()
    };
    
    console.log('✅ Success response:', response);
    return createJsonResponse(response);
      
  } catch (error) {
    console.log('❌ Critical error in doPost:', error.toString());
    console.log('Error stack:', error.stack);
    
    return createJsonResponse({
      ok: false,
      error: "Critical error: " + error.toString(),
      stack: error.stack
    });
  }
}

function createJsonResponse(data) {
  /**
   * Создает правильно отформатированный JSON ответ
   */
  return ContentService
    .createTextOutput(JSON.stringify(data, null, 2))
    .setMimeType(ContentService.MimeType.JSON)
    .setHeaders({
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
}

function doGet(e) {
  /**
   * Обработчик GET запросов для тестирования
   */
  console.log('GET request received:', e.parameter);
  
  return createJsonResponse({
    ok: true,
    message: "Google Apps Script is working",
    method: "GET",
    timestamp: new Date().toISOString(),
    parameters: e.parameter
  });
}

// Функция для тестирования скрипта из редактора
function testScript() {
  console.log('=== MANUAL TEST ===');
  
  const testData = {
    parameter: {
      date: "2025-06-12",
      ticker: "MANUAL_TEST",
      figi: "MANUAL_FIGI",
      side: "BUY",
      price: "123.45",
      qty: "1",
      fees: "0.1",
      token: "mySecret123"
    }
  };
  
  const result = doPost(testData);
  console.log('Test result:', result.getContent());
}
