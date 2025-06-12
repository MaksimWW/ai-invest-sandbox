
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
    
    // Получаем активную таблицу (или конкретную по ID)
    const sheet = SpreadsheetApp.getActiveSheet();
    
    // Записываем данные в том порядке, как их отправляет ваш код
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
