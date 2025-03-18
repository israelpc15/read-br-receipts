import boto3
import json
import fitz
import re
import csv
import logging
from io import BytesIO

def lambda_handler(event, context):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Get S3 bucket and key from event
    bucket = event['bucket']
    key = event['key']
    
    # Initialize S3 client
    s3 = boto3.client('s3')
    
    try:
        # Get PDF from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        pdf_content = response['Body'].read()
        
        # Process PDF content
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
            
        # Extract product block
        product_block = extract_product_block(text)
        
        # Extract products
        matches = extract_products(product_block)
        
        # Prepare results
        results = []
        for match in matches:
            results.append({
                'product_name': match[0].strip(),
                'code': match[1],
                'quantity': match[2],
                'unit': match[3],
                'unit_price': match[4],
                'total_price': match[5]
            })
        
        # Upload results to S3
        output_key = f"extracted/{key.split('/')[-1]}.json"
        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(results, ensure_ascii=False),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Extraction completed successfully',
                'products_found': len(results),
                'output_file': output_key
            })
        }
        
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

# Keep the existing helper functions
def extract_product_block(text):
    start_pattern = r', \s*(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\s'
    start_match = re.search(start_pattern, text)
    if start_match:
        start_pos = start_match.end()
        trimmed_text = text[start_pos:]
    else:
        trimmed_text = text

    end_marker = "Qtd. total de itens:"
    if end_marker in trimmed_text:
        product_block = trimmed_text.split(end_marker, 1)[0]
    else:
        product_block = trimmed_text

    product_block = re.sub(r'\s+', ' ', product_block)
    return product_block

def extract_products(text):
    product_pattern = (r'([A-ZÀ-Ú][A-ZÀ-Ú\s\/]+(?:\s+[a-zA-Z0-9À-Ú\/]+)*)\s+'
                      r'\(C[óo]digo:\s*(\d+)\)\s+'
                      r'Qtde\.:([\d,]+)\s+'
                      r'UN:\s*(\w+)\s+'
                      r'Vl\.\s*Unit\.:\s*([\d,]+)\s+'
                      r'Vl\.\s*Total\s+([\d,]+)')
    return re.findall(product_pattern, text)
