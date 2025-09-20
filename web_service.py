from flask import Flask, jsonify, request, render_template
import serial.tools.list_ports
import serial
import subprocess
import os

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ports', methods=['GET'])
def list_ports():
    try:
        ports = serial.tools.list_ports.comports()
        list_ports = [{'device': porta.device, 'description': porta.description} for porta in ports]
        return jsonify({'ports': list_ports})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
        
@app.route('/api/read_battery', methods=['POST'])
def read_battery():
    port = request.args.get('port')
    if not port:
        return jsonify({'erro': 'Parameter "port" is required'}), 400
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'm18.py')
        script_path = os.path.normpath(script_path)
        if not os.path.exists(script_path):
            return jsonify({'erro': 'Script m18.py'}), 404
        
        result = subprocess.run(['python', script_path, '--port', port, '--create_json'], capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'output': result.stdout.strip(),
                'error': result.stderr.strip() if result.stderr else None,
                'port': port
            })
        else:
            return jsonify({
                'erro': 'Error when executing m18.py',
                'details': result.stderr.strip()
            }), 500
    except Exception as e:
        return jsonify({'erro': f'Failed to execute m18.py: {str(e)}'}), 500
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
