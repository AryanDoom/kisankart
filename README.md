# KissanKart

KissanKart is a modern agriculture marketplace designed to bridge the gap between farmers and consumers. It provides a platform where farmers can sell their fresh produce directly to buyers, while also offering essential tools like weather forecasting to help with farm management.

## Project Features

### Farmer Side
*   **Secure Registration**: Validation for phone numbers and names to ensure authenticity.
*   **Crop Management**: A dedicated dashboard for farmers to list, update, and track their stock.
*   **Order Tracking**: View pending orders and mark them as completed upon delivery.
*   **Weather Intelligence**: Integrated 5-day weather forecast bot to help plan harvesting and sowing.

### Consumer Side
*   **Digital Marketplace**: Browse through a wide variety of fresh, organic produce with rich details.
*   **Shopping Cart System**: Easy to use cart functionality for a seamless shopping experience.
*   **Integrated Checkout**: A simulated payment gateway to ensure a smooth transition from cart to order.
*   **Order History**: Keep track of all previous purchases and their statuses.

---

## Technical Stack
*   **Backend**: Flask (Python)
*   **Database**: MongoDB (with in-memory demo fallback)
*   **Frontend**: HTML5, Vanilla CSS, JavaScript
*   **Integration**: OpenWeatherMap API for real-time weather data

---

## Installation Guide

### 1. Prerequisites
*   Python 3.x installed.
*   MongoDB (Optional, for persistent storage).

### 2. Setup
Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/yourusername/kisankart.git
cd kisankart

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory to configure your API keys:

```text
WEATHER_API_KEY=your_openweathermap_api_key_here
SECRET_KEY=your_secret_key_here
```

---

## How to Run

1.  Start the Flask application:
    ```bash
    python app.py
    ```
2.  Open your browser and navigate to `http://127.0.0.1:5000`.
3.  Choose your role (Farmer or Consumer) and start exploring the platform.

---

## Configuration Details
*   **Demo Mode**: The application is configured to run in demo mode by default if a database connection is not found, using in-memory storage for products and orders.
*   **Weather Bot**: Access the weather forecast via the "Info" tab. It uses geographical data to provide accurate local forecasts.

> [!NOTE]  
> If you are testing the registration logic, ensure you use a valid 10 digit phone number and an alphanumeric username.
