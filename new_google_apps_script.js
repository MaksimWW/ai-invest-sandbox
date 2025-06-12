
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
    
    // ВАЖНО: Замените на ID вашей таблицы Google Sheets
    // ID таблицы можно взять из URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
    const SPREADSHEET_ID = "12ku68n4cEz7q3TZjoUMvp1hF3QC3a4XRRg@LIZKVdqje8tTgid"; // Замените на ваш ID!
    
    // Получаем конкретную таблицу по ID
    const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = spreadsheet.getActiveSheet(); // или getSheetByName("Sheet1")
    
    if (!sheet) {
      console.log('No sheet found');
      return ContentService
        .createTextOutput(JSON.stringify({
          ok: false, 
          error: "Sheet not found. Check spreadsheet ID and sheet name."
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Если первая строка пустая, добавляем заголовки
    const firstRow = sheet.getRange(1, 1, 1, 8).getValues()[0];
    if (firstRow[0] === '') {
      const headers = ['date', 'ticker', 'figi', 'side', 'price', 'qty', 'fees', 'pnl'];
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
      new Date().toISOString() // timestamp записи
    ];
    
    console.log('Adding row:', rowData);
    sheet.appendRow(rowData);
    
    return ContentService
      .createTextOutput(JSON.stringify({
        ok: true, 
        message: "Trade logged successfully",
        data: rowData,
        spreadsheet_id: SPREADSHEET_ID
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('Error in doPost:', error);
    return ContentService
      .createTextOutput(JSON.stringify({
        ok: false, 
        error: error.toString(),
        message: "Проверьте ID таблицы в коде скрипта"
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
