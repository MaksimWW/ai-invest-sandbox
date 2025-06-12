
function doPost(e) {
  try {
    console.log('Received POST request');
    console.log('Parameters:', e.parameter);
    
    const data = e.parameter;
    
    // Проверяем токен
    if (data.token !== "mySecret123") {
      console.log('Unauthorized access attempt');
      return ContentService
        .createTextOutput(JSON.stringify({ok: false, error: "Unauthorized"}))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Если это просто тест подключения
    if (data.test === "ping") {
      console.log('Ping test request received');
      return ContentService
        .createTextOutput(JSON.stringify({
          ok: true, 
          message: "Webhook is working",
          timestamp: new Date().toISOString()
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Получаем активную таблицу (будет автоматически ваша таблица)
    const sheet = SpreadsheetApp.getActiveSheet();
    
    if (!sheet) {
      console.log('No active sheet found');
      return ContentService
        .createTextOutput(JSON.stringify({
          ok: false, 
          error: "No active sheet found"
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Если первая строка пустая, добавляем заголовки
    const firstRow = sheet.getRange(1, 1, 1, 8).getValues()[0];
    if (firstRow[0] === '') {
      const headers = ['Дата', 'Тикер', 'FIGI', 'Операция', 'Цена', 'Количество', 'Комиссия', 'Время записи'];
      sheet.getRange(1, 1, 1, 8).setValues([headers]);
    }
    
    // Записываем данные
    const rowData = [
      data.date || new Date().toISOString().split('T')[0],
      data.ticker || "",
      data.figi || "",
      data.side || "",
      parseFloat(data.price) || 0,
      parseInt(data.qty) || 0,
      parseFloat(data.fees) || 0,
      new Date() // timestamp записи
    ];
    
    console.log('Adding row:', rowData);
    sheet.appendRow(rowData);
    
    return ContentService
      .createTextOutput(JSON.stringify({
        ok: true, 
        message: "Trade logged successfully",
        data: rowData
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('Error in doPost:', error);
    return ContentService
      .createTextOutput(JSON.stringify({
        ok: false, 
        error: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
