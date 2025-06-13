
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
   * Обработчик GET запросов для тестирования и получения данных
   */
  console.log('GET request received:', e.parameter);
  
  const params = e.parameter;
  
  // Проверяем токен
  const expectedToken = "mySecret123"; // Ваш секретный токен
  if (params.token !== expectedToken) {
    console.log('❌ Unauthorized GET access attempt with token:', params.token);
    return createJsonResponse({
      ok: false, 
      error: "Unauthorized - invalid token"
    });
  }
  
  // Если запрашивается P/L
  if (params.action === "get_pnl") {
    try {
      console.log('📊 P/L calculation requested');
      
      const SPREADSHEET_ID = "12kdk6h4cEs7q31ZjoUMvpAIhF3OC384XRRg6LtZKVdo"; // ЗАМЕНИТЕ НА ВАШ ID!
      const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
      const sheet = spreadsheet.getActiveSheet();
      
      // Получаем все данные из таблицы
      const data = sheet.getDataRange().getValues();
      
      if (data.length <= 1) {
        // Только заголовки или пустая таблица
        return createJsonResponse({
          ok: true,
          pnl: 0.0,
          message: "No trades found"
        });
      }
      
      let totalPnl = 0.0;
      let buyPrice = {};  // Средняя цена покупки по тикерам
      let positions = {}; // Текущие позиции по тикерам
      
      // Пропускаем заголовок (первая строка)
      for (let i = 1; i < data.length; i++) {
        const row = data[i];
        const ticker = row[1];  // Колонка B - ticker
        const side = row[3];    // Колонка D - side
        const price = parseFloat(row[4]) || 0;  // Колонка E - price
        const qty = parseInt(row[5]) || 0;      // Колонка F - qty
        
        if (!ticker || !side || price <= 0 || qty <= 0) continue;
        
        if (!positions[ticker]) {
          positions[ticker] = 0;
          buyPrice[ticker] = 0;
        }
        
        if (side.toUpperCase() === 'BUY') {
          // Обновляем среднюю цену покупки
          const currentValue = positions[ticker] * buyPrice[ticker];
          const newValue = qty * price;
          const newQty = positions[ticker] + qty;
          
          if (newQty > 0) {
            buyPrice[ticker] = (currentValue + newValue) / newQty;
          }
          positions[ticker] = newQty;
          
        } else if (side.toUpperCase() === 'SELL') {
          // Вычисляем P/L от продажи
          const sellPnl = (price - buyPrice[ticker]) * qty;
          totalPnl += sellPnl;
          positions[ticker] -= qty;
          
          if (positions[ticker] < 0) {
            positions[ticker] = 0; // Не позволяем уйти в короткую позицию
          }
        }
      }
      
      console.log('✅ P/L calculated successfully:', totalPnl);
      
      return createJsonResponse({
        ok: true,
        pnl: Math.round(totalPnl * 100) / 100, // Округляем до 2 знаков
        positions: positions,
        timestamp: new Date().toISOString()
      });
      
    } catch (error) {
      console.log('❌ Error calculating P/L:', error.toString());
      return createJsonResponse({
        ok: false,
        error: "Failed to calculate P/L: " + error.toString()
      });
    }
  }
  
  // Обычный тест GET запроса
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
