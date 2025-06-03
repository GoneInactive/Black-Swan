use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use serde::{Deserialize};
use std::fs;
use tungstenite::{connect, Message};
use url::Url;
use std::collections::HashMap;
use reqwest::blocking::Client;

#[pyfunction]
fn test_connection() -> PyResult<()> {
    let url = Url::parse("wss://ws.kraken.com")
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("URL parse error: {}", e)))?;
    let (mut socket, _) = connect(url)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("WebSocket connection failed: {}", e)))?;

    let subscribe_msg = r#"{
        "event": "subscribe",
        "pair": ["XBT/USD"],
        "subscription": {"name": "ticker"}
    }"#;

    socket.write_message(Message::Text(subscribe_msg.to_string()))
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to send message: {}", e)))?;

    if let Ok(msg) = socket.read_message() {
        if let Message::Text(txt) = msg {
            println!("Received message: {}", txt);
        }
    }

    Ok(())
}

#[derive(Debug, Deserialize)]
struct Config {
    kraken: KrakenCredentials,
}

#[derive(Debug, Deserialize)]
struct KrakenCredentials {
    api_key: String,
    api_secret: String,
}

fn load_config() -> KrakenCredentials {
    let content = fs::read_to_string("config/config.yaml").expect("Cannot read config");
    let cfg: Config = serde_yaml::from_str(&content).expect("Invalid config format");
    cfg.kraken
}

fn get_token(api_key: &str, api_secret: &str) -> String {
    let client = Client::new();
    let res = client
        .post("https://api.kraken.com/0/private/GetWebSocketsToken")
        .header("API-Key", api_key)
        .header("API-Sign", api_secret)  // Kraken expects API-Sign for private endpoints (optional here)
        .header("Content-Type", "application/x-www-form-urlencoded")
        .body("")
        .send()
        .expect("Failed to get token");

    let json: HashMap<String, serde_json::Value> = res.json().expect("Invalid JSON");
    json["result"]["token"].as_str().unwrap().to_string()
}

fn connect_auth_socket(token: &str) -> tungstenite::WebSocket<tungstenite::stream::MaybeTlsStream<std::net::TcpStream>> {
    let url = Url::parse("wss://ws-auth.kraken.com").unwrap();
    let (mut socket, _) = connect(url).expect("Failed to connect to auth WebSocket");

    let login_msg = serde_json::json!({
        "event": "subscribe",
        "subscription": {
            "name": "ownTrades",
            "token": token
        }
    });
    socket.write_message(Message::Text(login_msg.to_string())).unwrap();
    socket
}

#[pyfunction]
fn add_order(pair: String, side: String, volume: f64, ordertype: String) {
    let cfg = load_config();
    let token = get_token(&cfg.api_key, &cfg.api_secret);
    let mut socket = connect_auth_socket(&token);

    let msg = serde_json::json!({
        "event": "addOrder",
        "token": token,
        "ordertype": ordertype,
        "type": side,
        "volume": volume.to_string(),
        "pair": pair
    });

    socket.write_message(Message::Text(msg.to_string())).unwrap();
    if let Ok(msg) = socket.read_message() {
        if let Message::Text(txt) = msg {
            println!("{}", txt);
        }
    }
}

#[pyfunction]
fn get_orders() {
    let cfg = load_config();
    let token = get_token(&cfg.api_key, &cfg.api_secret);
    let mut socket = connect_auth_socket(&token);

    let msg = serde_json::json!({
        "event": "subscribe",
        "subscription": {
            "name": "openOrders",
            "token": token
        }
    });

    socket.write_message(Message::Text(msg.to_string())).unwrap();
    if let Ok(msg) = socket.read_message() {
        if let Message::Text(txt) = msg {
            println!("{}", txt);
        }
    }
}

#[pyfunction]
fn close_orders(txid: Vec<String>) {
    let cfg = load_config();
    let token = get_token(&cfg.api_key, &cfg.api_secret);
    let mut socket = connect_auth_socket(&token);

    for id in txid {
        let msg = serde_json::json!({
            "event": "cancelOrder",
            "token": token,
            "txid": id
        });
        socket.write_message(Message::Text(msg.to_string())).unwrap();

        if let Ok(msg) = socket.read_message() {
            if let Message::Text(txt) = msg {
                println!("{}", txt);
            }
        }
    }
}

#[pyfunction]
fn get_orderbook(pair: String, depth: u32) {
    let url = Url::parse("wss://ws.kraken.com").unwrap();
    let (mut socket, _) = connect(url).expect("WebSocket connection failed");

    let msg = serde_json::json!({
        "event": "subscribe",
        "subscription": {
            "name": "book",
            "depth": depth
        },
        "pair": [pair]
    });

    socket.write_message(Message::Text(msg.to_string())).unwrap();

    if let Ok(msg) = socket.read_message() {
        if let Message::Text(txt) = msg {
            println!("{}", txt);
        }
    }
}

#[pyfunction]
fn subscribe(pair: String) {
    let url = Url::parse("wss://ws.kraken.com").unwrap();
    let (mut socket, _) = connect(url).expect("WebSocket connection failed");

    let msg = serde_json::json!({
        "event": "subscribe",
        "subscription": {
            "name": "ticker"
        },
        "pair": [pair]
    });

    socket.write_message(Message::Text(msg.to_string())).unwrap();

    if let Ok(msg) = socket.read_message() {
        if let Message::Text(txt) = msg {
            println!("{}", txt);
        }
    }
}

#[pymodule]
fn rust_ws_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(subscribe, m)?)?;
    m.add_function(wrap_pyfunction!(get_orderbook, m)?)?;
    m.add_function(wrap_pyfunction!(add_order, m)?)?;
    m.add_function(wrap_pyfunction!(get_orders, m)?)?;
    m.add_function(wrap_pyfunction!(close_orders, m)?)?;
    m.add_function(wrap_pyfunction!(test_connection, m)?)?;
    Ok(())
}
