from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from flask import Flask, request, jsonify
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv
import orchastrator as orch
import asyncio

load_dotenv()
app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_string():
    data = request.json
    query = data.get('user_query', '')   
    
    try:
    # Process the input string and generate output
        credential = DefaultAzureCredential()
        output_string = orch.mainApp(query, credential)
    
    except HttpResponseError as e:
        # Log the error and return a JSON response with the error message
        print(f"HttpResponseError: {e}")
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        # Log any other exceptions and return a JSON response with the error message
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'output_string': output_string})

if __name__ == '__main__':
    app.run(debug=True, port=8080)