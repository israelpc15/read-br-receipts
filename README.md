# read-br-receipts

This project contains a Lambda function that reads Brazilian receipts (BR receipts) from PDFs stored in an S3 bucket and returns all the products purchased. The main script (located in `aws/lambda_function.py`) extracts receipt text using PyMuPDF (the `fitz` module) and then leverages regular expressions to extract products information.

The physical brazilian receipt is generated with a QR Code, you must read the QRCode from a mobile phone, and them export as a PDF.

## Prerequisites

- Python 3.9 (or later)
- AWS CLI configured with appropriate credentials and permissions
- AWS Lambda and S3 permissions

## Setup and Installation

### 1. Check Out the Repository

Clone the repository:

```bash
git clone https://github.com/israelpc15/read-br-receipts.git
```

Change directory into the project:

```bash
cd read-br-receipts
```

### 2. Prepare the Lambda Package

This script doesn't execute if you don't install the required libraries. So I created a package folder to maintain the libraries.

#### a. Create a package directory

```bash
mkdir package
```

Navigate to the package folder:

```bash
cd package
```

Install the required libraries into the package folder:

```bash
pip3 install PyMuPDF -t .
```

After installation, create the ZIP file for deployment:

```bash
cd ..
zip -r /aws/nfse_extractor_lambda.zip .
```


### 3. Deploy the lambda function

Upload the deployment package using AWS CLI. Replace `YOUR_FUNCTION_NAME` with the actual Lambda function name:

```bash
aws lambda update-function-code --function-name YOUR_FUNCTION_NAME --zip-file fileb://nfse_extractor_lambda.zip
```

### 4. Configure and test the Lambda function

- Create a test event in the Lambda console with JSON content similar to:

```json
{
  "bucket": "your-s3-bucket-name",
  "key": "path/to/your/receipt.pdf"
}
```

- Execute the test to verify the function runs and check the CloudWatch logs for output.

## Troubleshooting

- **Timeouts:**  
  If you encounter timeouts, ensure that your function configuration (memory, timeout) is set appropriately. Since the sample function uses a simple print or log statement, timeouts suggest possible packaging or configuration issues.

- **Binary Compatibility:**  
  If you face errors like `invalid ELF header` for native modules (e.g., for PyMuPDF), make sure you are installing dependencies inside the Docker container, as described above.

## Additional Information

- This project is meant to extract and process receipt data using PDF parsing.
- The code uses the PyMuPDF library (`fitz` module) to extract text and regular expressions to extract product details.
- For further customization, update the extraction patterns in `lambda_function.py` (or `nfse_extractor_s3.py`).

Happy coding!
