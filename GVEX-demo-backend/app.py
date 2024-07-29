from flask import Flask
from flask_cors import CORS
from flask import request, jsonify
import torch

app = Flask(__name__)
CORS(app, resources=r'/*', supports_credentials=True)

@app.route('/config', methods=['POST', 'GET'])
def config_settings():
    if request.method == 'POST':
        config_data = request.get_json(silent=True)
        explain_subgraph = torch.load('explain_result.pt')
        explain_pattern = torch.load('pattern_result.pt')
        # explain_subgraph, explain_pattern = approximate_algorithm.main(config_data)
        return [explain_subgraph, explain_pattern]
    
@app.route('/getdataset', methods=['POST', 'GET'])
def get_dataset():
    if request.method == 'POST':
        print(request.get_json(silent=True))
        dataset_name = request.get_json(silent=True)
        dataset_info = torch.load('dataset_info.pt')
        return dataset_info
    

@app.route('/baselines', methods=['POST', 'GET'])
def get_baselines():
    if request.method == 'POST':
        print(request.get_json(silent=True))
        algorithm_name = request.get_json(silent=True)
        print(algorithm_name)
        return False