// ============================================================
// Google Apps Script — Partner Registration API
// ============================================================
// SETUP:
// 1. Go to https://script.google.com → New Project
// 2. Paste this entire file into Code.gs
// 3. Click Deploy → New deployment
// 4. Type: Web app
// 5. Execute as: Me
// 6. Who has access: Anyone
// 7. Click Deploy → copy the Web App URL
// 8. Paste that URL into partner-portal/index.html (SCRIPT_URL variable)
//
// SHEET SETUP:
// - Create a Google Sheet (or use existing)
// - First sheet (tab) will be used
// - Row 1 headers (script auto-creates if sheet is empty):
//   Name | Mobile | Location | Ref Code | Date | Status
// ============================================================

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    // Validate required fields
    if (!data.name || !data.mobile || !data.ref_code) {
      return jsonResponse({ success: false, error: 'Missing required fields' });
    }

    // Sanitize inputs
    var name = String(data.name).substring(0, 100).trim();
    var mobile = String(data.mobile).replace(/[^0-9+\- ]/g, '').substring(0, 20).trim();
    var address = String(data.address || '').substring(0, 200).trim();
    var location = String(data.location || '').substring(0, 100).trim();
    var geo = String(data.geo || '').substring(0, 50).trim();
    var refCode = String(data.ref_code).replace(/[^a-z0-9_\-]/gi, '').substring(0, 20).toLowerCase();

    if (!refCode || refCode.length < 3) {
      return jsonResponse({ success: false, error: 'Invalid ref code' });
    }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheets()[0];

    // Auto-create headers if sheet is empty
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['Name', 'Mobile', 'Address', 'Area', 'GPS', 'Ref Code', 'Date', 'Status']);
    }

    // Check for duplicate ref code
    var existingData = sheet.getDataRange().getValues();
    for (var i = 1; i < existingData.length; i++) {
      if (String(existingData[i][5]).toLowerCase() === refCode) {
        return jsonResponse({ success: false, error: 'Ref code already exists' });
      }
    }

    // Check for duplicate mobile
    for (var i = 1; i < existingData.length; i++) {
      if (String(existingData[i][1]).replace(/\D/g, '') === mobile.replace(/\D/g, '')) {
        return jsonResponse({ success: false, error: 'Mobile already registered', existing_ref: String(existingData[i][5]) });
      }
    }

    // Append row
    var now = new Date();
    var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm');
    sheet.appendRow([name, mobile, address, location, geo, refCode, dateStr, 'Active']);

    return jsonResponse({ success: true, ref_code: refCode });

  } catch (err) {
    return jsonResponse({ success: false, error: err.message });
  }
}

function doGet(e) {
  try {
    var action = (e.parameter.action || '').trim();

    // Check if ref code exists
    if (action === 'check' && e.parameter.ref) {
      var ref = String(e.parameter.ref).toLowerCase();
      var ss = SpreadsheetApp.getActiveSpreadsheet();
      var sheet = ss.getSheets()[0];
      var data = sheet.getDataRange().getValues();
      for (var i = 1; i < data.length; i++) {
        if (String(data[i][3]).toLowerCase() === ref) {
          return jsonResponse({ exists: true });
        }
      }
      return jsonResponse({ exists: false });
    }

    return jsonResponse({ status: 'ok', message: 'Partner Registration API' });

  } catch (err) {
    return jsonResponse({ success: false, error: err.message });
  }
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
