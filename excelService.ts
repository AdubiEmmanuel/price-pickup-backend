// Add more robust CSV parsing with better error handling
processCSVData(csvData: string) {
  try {
    // Log the first part of the CSV for debugging
    console.log('CSV data preview:', csvData.substring(0, 200));
    
    const lines = csvData.split('\n');
    if (lines.length === 0) {
      throw new Error('CSV file is empty');
    }
    
    // Get headers and normalize them (trim whitespace, convert to uppercase)
    const headers = lines[0].split(',').map(h => h.trim().toUpperCase());
    console.log('CSV headers found:', headers);
    
    // Check for required columns with flexible matching
    const skuNameVariations = ['SKU NAME', 'SKUNAME', 'SKU_NAME', 'PRODUCT NAME', 'ITEM NAME'];
    const skuNameIndex = headers.findIndex(h => skuNameVariations.includes(h));
    
    if (skuNameIndex === -1) {
      console.error('Available headers:', headers);
      throw new Error(`CSV format is invalid - SKU NAME not found. Available columns: ${headers.join(', ')}`);
    }
    
    // Process the data rows
    const result = [];
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue; // Skip empty lines
      
      const values = lines[i].split(',');
      if (values.length !== headers.length) {
        console.warn(`Line ${i+1} has ${values.length} values but should have ${headers.length}. Skipping.`);
        continue;
      }
      
      const row = {};
      headers.forEach((header, index) => {
        row[header] = values[index]?.trim() || '';
      });
      
      result.push(row);
    }
    
    return result;
  } catch (error) {
    console.error('CSV processing error:', error);
    throw error;
  }
}