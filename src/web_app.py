"""
Flask web application with USPS-themed frontend
Pure frontend that calls the API service
"""
from flask import Flask, request, jsonify, render_template_string
import logging
import requests
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager

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
        
        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .footer a {
            color: #007bff;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Zippuff</h1>
        <p>USPS ZIP Code Lookup Tool</p>
    </div>
    
    <div class="container">
        <div class="card">
            <div class="tabs">
                <button class="tab active" onclick="showTab('zip-to-city')">ZIP to City/State</button>
                <button class="tab" onclick="showTab('city-to-zip')">City/State to ZIP</button>
                <button class="tab" onclick="showTab('validate')">Validate ZIP</button>
            </div>
            
            <!-- ZIP to City/State Tab -->
            <div id="zip-to-city" class="tab-content active">
                <form id="zipToCityForm">
                    <div class="form-group">
                        <label for="zipcode">ZIP Code:</label>
                        <input type="text" id="zipcode" name="zipcode" class="form-control" 
                               placeholder="Enter 5-digit ZIP code" maxlength="5" required>
                    </div>
                    <button type="submit" class="btn">🔍 Look Up City/State</button>
                </form>
                <div id="zipToCityResult" class="result" style="display: none;"></div>
            </div>
            
            <!-- City/State to ZIP Tab -->
            <div id="city-to-zip" class="tab-content">
                <form id="cityToZipForm">
                    <div class="form-group">
                        <label for="city">City:</label>
                        <input type="text" id="city" name="city" class="form-control" 
                               placeholder="Enter city name" required>
                    </div>
                    <div class="form-group">
                        <label for="state">State:</label>
                        <input type="text" id="state" name="state" class="form-control" 
                               placeholder="Enter 2-letter state code" maxlength="2" required>
                    </div>
                    <button type="submit" class="btn">🔍 Look Up ZIP Code</button>
                </form>
                <div id="cityToZipResult" class="result" style="display: none;"></div>
            </div>
            
            <!-- Validate ZIP Tab -->
            <div id="validate" class="tab-content">
                <form id="validateForm">
                    <div class="form-group">
                        <label for="validateZipcode">ZIP Code:</label>
                        <input type="text" id="validateZipcode" name="zipcode" class="form-control" 
                               placeholder="Enter ZIP code to validate" maxlength="5" required>
                    </div>
                    <button type="submit" class="btn">✅ Validate ZIP Code</button>
                </form>
                <div id="validateResult" class="result" style="display: none;"></div>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Looking up information...</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Powered by USPS API • Secure and Reliable ZIP Code Lookups</p>
        <p><a href="/health">API Health Check</a> • <a href="/api/config">Configuration</a></p>
    </div>
    
    <script>
        // API Service URL - will be injected by Flask
        const API_BASE_URL = '{{ api_base_url }}';
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
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
            resultDiv.style.display = 'block';
            resultDiv.className = `result ${isError ? 'error' : 'success'}`;
            
            if (isError) {
                resultDiv.innerHTML = `
                    <h3>❌ Error</h3>
                    <p>${data.error || 'An error occurred'}</p>
                `;
            } else {
                let html = '<h3>✅ Result</h3>';
                
                if (data.zipcode) {
                    html += `<div class="result-item">
                        <span class="result-label">ZIP Code:</span>
                        <span class="result-value">${data.zipcode}</span>
                    </div>`;
                }
                
                if (data.city) {
                    html += `<div class="result-item">
                        <span class="result-label">City:</span>
                        <span class="result-value">${data.city}</span>
                    </div>`;
                }
                
                if (data.state) {
                    html += `<div class="result-item">
                        <span class="result-label">State:</span>
                        <span class="result-value">${data.state}</span>
                    </div>`;
                }
                
                if (data.valid !== undefined) {
                    html += `<div class="result-item">
                        <span class="result-label">Valid:</span>
                        <span class="result-value">${data.valid ? 'Yes' : 'No'}</span>
                    </div>`;
                }
                
                resultDiv.innerHTML = html;
            }
        }
        
        // ZIP to City/State form
        document.getElementById('zipToCityForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const zipcode = document.getElementById('zipcode').value.trim();
            
            if (!zipcode) {
                showResult('zipToCityResult', { error: 'Please enter a ZIP code' }, true);
                return;
            }
            
            showLoading();
            
            try {
                console.log('Making API call to:', `${API_BASE_URL}/api/zip-to-city?zipcode=${encodeURIComponent(zipcode)}`);
                const response = await fetch(`${API_BASE_URL}/api/zip-to-city?zipcode=${encodeURIComponent(zipcode)}`);
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                const data = await response.json();
                console.log('Response data:', data);
                
                if (response.ok) {
                    showResult('zipToCityResult', data);
                } else {
                    showResult('zipToCityResult', data, true);
                }
            } catch (error) {
                console.error('Network error:', error);
                showResult('zipToCityResult', { error: `Network error: ${error.message}` }, true);
            } finally {
                hideLoading();
            }
        });
        
        // City/State to ZIP form
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
                const response = await fetch(`${API_BASE_URL}/api/city-to-zip?city=${encodeURIComponent(city)}&state=${encodeURIComponent(state)}`);
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
        
        // Validate ZIP form
        document.getElementById('validateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const zipcode = document.getElementById('validateZipcode').value.trim();
            
            if (!zipcode) {
                showResult('validateResult', { error: 'Please enter a ZIP code' }, true);
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/validate-zip?zipcode=${encodeURIComponent(zipcode)}`);
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

# New templates for health and config pages
HEALTH_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Health Check - Zippuff</title>
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
            background: linear-gradient(135deg, #28a745 0%, #218838 100%);
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
            border-left: 5px solid #28a745;
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
            color: #28a745;
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
        
        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #28a745;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .footer a {
            color: #007bff;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Zippuff</h1>
        <p>API Health Check</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>API Service Status</h2>
            <div class="result {{ 'success' if api_healthy else 'error' }}">
                <h3>API Service: {{ 'Healthy' if api_healthy else 'Unhealthy' }}</h3>
                {% if api_data %}
                    <p>Service is responding and returning data.</p>
                    <h4>API Response:</h4>
                    <pre>{{ api_data | tojson(indent=2) }}</pre>
                {% else %}
                    <p>Service is not responding or returning data.</p>
                    <p>Please check the API service logs for details.</p>
                {% endif %}
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by USPS API • Secure and Reliable ZIP Code Lookups</p>
            <p><a href="/">Back to Main App</a> • <a href="/api/config">Configuration</a></p>
        </div>
    </div>
</body>
</html>
"""

CONFIG_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Configuration - Zippuff</title>
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
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
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
        
        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .footer a {
            color: #007bff;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Zippuff</h1>
        <p>API Configuration</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Current Configuration</h2>
            <div class="result">
                <h3>Configuration Details</h3>
                <pre>{{ config | tojson(indent=2) }}</pre>
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by USPS API • Secure and Reliable ZIP Code Lookups</p>
            <p><a href="/">Back to Main App</a> • <a href="/health">Health Check</a></p>
        </div>
    </div>
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
    
    # Get API service URL from environment or config
    api_port = os.getenv('API_PORT', '59081')
    api_host = os.getenv('API_HOST', '192.168.3.78')  # Use server IP instead of localhost
    
    # Default API base URL (will be updated per request)
    api_base_url = f"http://{api_host}:{api_port}"
    
    app.logger.info(f"Web interface configured to use API service at: {api_base_url}")
    
    def get_api_base_url():
        """Get the appropriate API base URL based on request context"""
        try:
            # Use relative URL for HTTPS compatibility
            if request.headers.get('X-Forwarded-Proto') == 'https' or request.headers.get('X-Forwarded-SSL') == 'on':
                # If accessed via HTTPS, use relative URL that goes through nginx
                return "/api-proxy"
            else:
                # Fallback to direct IP for HTTP access
                return f"http://{api_host}:{api_port}"
        except RuntimeError:
            # Outside of request context, use default
            return api_base_url
    
    @app.route('/')
    def index():
        """Main page with USPS-themed frontend"""
        return render_template_string(HTML_TEMPLATE, api_base_url=get_api_base_url())
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            # Test API service connection
            api_response = requests.get(f"{api_base_url}/health", timeout=5)
            api_healthy = api_response.status_code == 200
            api_data = api_response.json() if api_healthy else None
        except Exception as e:
            api_healthy = False
            api_data = None
        
        return render_template_string(HEALTH_TEMPLATE, 
                                   api_healthy=api_healthy, 
                                   api_data=api_data,
                                   api_base_url=get_api_base_url())
    
    @app.route('/debug', methods=['GET'])
    def debug():
        """Debug endpoint to show API configuration"""
        return jsonify({
            'api_base_url': get_api_base_url(),
            'api_host': os.getenv('API_HOST', '192.168.3.78'),
            'api_port': os.getenv('API_PORT', '59081'),
            'test_url': f"{get_api_base_url()}/api/zip-to-city?zipcode=20012"
        })
    
    @app.route('/api-proxy/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def api_proxy(subpath):
        """Proxy API calls to the API service"""
        try:
            # Forward the request to the API service
            api_url = f"http://localhost:59081/{subpath}"
            response = requests.request(
                method=request.method,
                url=api_url,
                params=request.args,
                headers={key: value for key, value in request.headers if key != 'Host'},
                timeout=10
            )
            
            # Return the response from the API service
            return response.content, response.status_code, dict(response.headers)
            
        except Exception as e:
            app.logger.error(f"API proxy error: {e}")
            return jsonify({'error': f'API proxy error: {e}'}), 500
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration (without sensitive data)"""
        try:
            # Call API service for config
            response = requests.get(f"{api_base_url}/api/config", timeout=5)
            if response.status_code == 200:
                api_config = response.json()
                return render_template_string(CONFIG_TEMPLATE, 
                                           config=api_config,
                                           api_base_url=get_api_base_url())
            else:
                return render_template_string(CONFIG_TEMPLATE, 
                                           config={'error': 'API service unavailable'},
                                           api_base_url=get_api_base_url())
        except Exception as e:
            app.logger.error(f"Failed to get API config: {e}")
            return render_template_string(CONFIG_TEMPLATE, 
                                       config={'error': f'Connection error: {e}'},
                                       api_base_url=get_api_base_url())
    
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