"""
Flask web application with USPS-themed frontend
"""
from flask import Flask, request, jsonify, render_template_string
import logging
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager
from usps_client import USPSClient, AddressInfo

# HTML template with USPS theme
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zippuff - USPS ZIP Code Lookup</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            padding: 2rem;
            margin-bottom: 2rem;
            border-left: 5px solid #007bff;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #495057;
        }
        
        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,123,255,0.3);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #6c757d 0%, #545b62 100%);
        }
        
        .btn-secondary:hover {
            box-shadow: 0 4px 12px rgba(108,117,125,0.3);
        }
        
        .result {
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 1rem;
        }
        
        .result.success {
            border-color: #28a745;
            background: #d4edda;
        }
        
        .result.error {
            border-color: #dc3545;
            background: #f8d7da;
        }
        
        .result h3 {
            color: #495057;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .result-item:last-child {
            border-bottom: none;
        }
        
        .result-label {
            font-weight: 600;
            color: #495057;
        }
        
        .result-value {
            color: #007bff;
            font-weight: 500;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 2rem;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .tab {
            flex: 1;
            padding: 1rem;
            background: #e9ecef;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .tab.active {
            background: #007bff;
            color: white;
        }
        
        .tab:hover:not(.active) {
            background: #dee2e6;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .usps-logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 1rem;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007bff;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                margin: 1rem auto;
            }
            
            .card {
                padding: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="usps-logo">📮</div>
        <h1>Zippuff</h1>
        <p>USPS ZIP Code Lookup Tool</p>
    </div>
    
    <div class="container">
        <div class="tabs">
            <button class="tab active" onclick="showTab('zip-to-city')">ZIP to City/State</button>
            <button class="tab" onclick="showTab('city-to-zip')">City/State to ZIP</button>
            <button class="tab" onclick="showTab('validate')">Validate ZIP</button>
        </div>
        
        <!-- ZIP to City/State Tab -->
        <div id="zip-to-city" class="tab-content active">
            <div class="card">
                <h2>Find City and State from ZIP Code</h2>
                <form id="zipToCityForm">
                    <div class="form-group">
                        <label for="zipcode">ZIP Code:</label>
                        <input type="text" id="zipcode" name="zipcode" class="form-control" 
                               placeholder="Enter 5-digit ZIP code (e.g., 90210)" maxlength="5">
                    </div>
                    <button type="submit" class="btn">Look Up City/State</button>
                </form>
                <div id="zipToCityResult"></div>
            </div>
        </div>
        
        <!-- City/State to ZIP Tab -->
        <div id="city-to-zip" class="tab-content">
            <div class="card">
                <h2>Find ZIP Code from City and State</h2>
                <form id="cityToZipForm">
                    <div class="form-group">
                        <label for="city">City:</label>
                        <input type="text" id="city" name="city" class="form-control" 
                               placeholder="Enter city name (e.g., Beverly Hills)">
                    </div>
                    <div class="form-group">
                        <label for="state">State:</label>
                        <input type="text" id="state" name="state" class="form-control" 
                               placeholder="Enter 2-letter state code (e.g., CA)" maxlength="2">
                    </div>
                    <button type="submit" class="btn">Look Up ZIP Code</button>
                </form>
                <div id="cityToZipResult"></div>
            </div>
        </div>
        
        <!-- Validate ZIP Tab -->
        <div id="validate" class="tab-content">
            <div class="card">
                <h2>Validate ZIP Code Format</h2>
                <form id="validateForm">
                    <div class="form-group">
                        <label for="validateZipcode">ZIP Code:</label>
                        <input type="text" id="validateZipcode" name="zipcode" class="form-control" 
                               placeholder="Enter ZIP code to validate" maxlength="5">
                    </div>
                    <button type="submit" class="btn">Validate ZIP Code</button>
                </form>
                <div id="validateResult"></div>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Looking up information...</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Powered by USPS API • Secure and Reliable ZIP Code Lookups</p>
    </div>
    
    <script>
        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        function showResult(elementId, data, isError = false) {
            const resultDiv = document.getElementById(elementId);
            
            if (isError) {
                resultDiv.innerHTML = `
                    <div class="result error">
                        <h3>❌ Error</h3>
                        <p>${data.error}</p>
                    </div>
                `;
            } else {
                let resultHtml = '<div class="result success"><h3>✅ Results</h3>';
                
                if (data.zipcode) {
                    resultHtml += `
                        <div class="result-item">
                            <span class="result-label">ZIP Code:</span>
                            <span class="result-value">${data.zipcode}</span>
                        </div>
                    `;
                }
                
                if (data.city) {
                    resultHtml += `
                        <div class="result-item">
                            <span class="result-label">City:</span>
                            <span class="result-value">${data.city}</span>
                        </div>
                    `;
                }
                
                if (data.state) {
                    resultHtml += `
                        <div class="result-item">
                            <span class="result-label">State:</span>
                            <span class="result-value">${data.state}</span>
                        </div>
                    `;
                }
                
                if (data.valid !== undefined) {
                    resultHtml += `
                        <div class="result-item">
                            <span class="result-label">Valid:</span>
                            <span class="result-value">${data.valid ? 'Yes' : 'No'}</span>
                        </div>
                    `;
                }
                
                resultHtml += '</div>';
                resultDiv.innerHTML = resultHtml;
            }
        }
        
        // ZIP to City/State Form
        document.getElementById('zipToCityForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const zipcode = document.getElementById('zipcode').value.trim();
            
            if (!zipcode) {
                showResult('zipToCityResult', { error: 'Please enter a ZIP code' }, true);
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch(`/api/zip-to-city?zipcode=${encodeURIComponent(zipcode)}`);
                const data = await response.json();
                
                if (response.ok) {
                    showResult('zipToCityResult', data);
                } else {
                    showResult('zipToCityResult', data, true);
                }
            } catch (error) {
                showResult('zipToCityResult', { error: 'Network error. Please try again.' }, true);
            } finally {
                hideLoading();
            }
        });
        
        // City/State to ZIP Form
        document.getElementById('cityToZipForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const city = document.getElementById('city').value.trim();
            const state = document.getElementById('state').value.trim();
            
            if (!city || !state) {
                showResult('cityToZipResult', { error: 'Please enter both city and state' }, true);
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch(`/api/city-to-zip?city=${encodeURIComponent(city)}&state=${encodeURIComponent(state)}`);
                const data = await response.json();
                
                if (response.ok) {
                    showResult('cityToZipResult', data);
                } else {
                    showResult('cityToZipResult', data, true);
                }
            } catch (error) {
                showResult('cityToZipResult', { error: 'Network error. Please try again.' }, true);
            } finally {
                hideLoading();
            }
        });
        
        // Validate ZIP Form
        document.getElementById('validateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const zipcode = document.getElementById('validateZipcode').value.trim();
            
            if (!zipcode) {
                showResult('validateResult', { error: 'Please enter a ZIP code' }, true);
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch(`/api/validate-zip?zipcode=${encodeURIComponent(zipcode)}`);
                const data = await response.json();
                
                if (response.ok) {
                    showResult('validateResult', data);
                } else {
                    showResult('validateResult', data, true);
                }
            } catch (error) {
                showResult('validateResult', { error: 'Network error. Please try again.' }, true);
            } finally {
                hideLoading();
            }
        });
        
        // Auto-format ZIP codes
        document.querySelectorAll('input[placeholder*="ZIP"]').forEach(input => {
            input.addEventListener('input', (e) => {
                e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 5);
            });
        });
        
        // Auto-format state codes
        document.getElementById('state').addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/[^A-Za-z]/g, '').slice(0, 2).toUpperCase();
        });
    </script>
</body>
</html>
"""


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Initialize configuration
    config = ConfigManager()
    
    # Setup logging
    log_config = config.get_logging_config()
    log_file = Path(log_config['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_config['level']),
        format=log_config['format'],
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Initialize USPS client
    usps_config = config.get_usps_config()
    usps_client = USPSClient(
        userid=usps_config['userid'],
        test_mode=usps_config['test_mode']
    )
    
    @app.route('/')
    def index():
        """Main page with USPS-themed frontend"""
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'zippuff',
            'version': config.get('app.version', '1.0.0')
        })
    
    @app.route('/api/zip-to-city', methods=['GET'])
    def zip_to_city():
        """Look up city and state from ZIP code"""
        zipcode = request.args.get('zipcode')
        
        if not zipcode:
            return jsonify({
                'error': 'ZIP code parameter is required'
            }), 400
        
        result = usps_client.zip_to_city_state(zipcode)
        
        if result.error:
            return jsonify({
                'error': result.error
            }), 400
        
        return jsonify({
            'zipcode': result.zipcode,
            'city': result.city,
            'state': result.state
        })
    
    @app.route('/api/city-to-zip', methods=['GET'])
    def city_to_zip():
        """Look up ZIP code from city and state"""
        city = request.args.get('city')
        state = request.args.get('state')
        
        if not city or not state:
            return jsonify({
                'error': 'Both city and state parameters are required'
            }), 400
        
        result = usps_client.city_state_to_zip(city, state)
        
        if result.error:
            return jsonify({
                'error': result.error
            }), 400
        
        return jsonify({
            'zipcode': result.zipcode,
            'city': result.city,
            'state': result.state
        })
    
    @app.route('/api/validate-zip', methods=['GET'])
    def validate_zip():
        """Validate ZIP code format"""
        zipcode = request.args.get('zipcode')
        
        if not zipcode:
            return jsonify({
                'error': 'ZIP code parameter is required'
            }), 400
        
        is_valid = usps_client.validate_zipcode(zipcode)
        
        return jsonify({
            'zipcode': zipcode,
            'valid': is_valid
        })
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration (without sensitive data)"""
        return jsonify({
            'test_mode': usps_config['test_mode'],
            'base_url': usps_config['base_url'],
            'app_version': config.get('app.version', '1.0.0')
        })
    
    return app


def main():
    """Run the Flask application"""
    config = ConfigManager()
    app_config = config.get_app_config()
    
    app = create_app()
    
    app.run(
        host=app_config['host'],
        port=app_config['port'],
        debug=app_config['debug']
    )


if __name__ == '__main__':
    main() 