use reqwest::blocking::Client;
use reqwest::Error;
use serde::Deserialize;
use std::collections::HashMap;
use std::fs;
use serde_json::Value;
use std::path::Path;

// Error type for handling Binance API-related issues
#[derive(Debug)]
pub enum BinanceError {
    HttpError(Error),             // HTTP-level error
    ParseError(String),           // JSON parsing error
    MissingField(String),         // Missing expected data field
}

// Struct to load only the 'binance' section from the full config file
#[derive(Debug, Deserialize)]
struct FullConfig {
    binance: BinanceConfig,
}

// Binance config details from YAML
#[derive(Debug, Deserialize)]
struct BinanceConfig {
    api_key: String,              // Binance API key (currently unused)
    api_secret: String,          // Binance API secret (currently unused)
    default_symbol: String,      // Default trading symbol, e.g. "BTCUSDT"
}

// BinanceClient handles HTTP requests and symbol targeting
pub struct BinanceClient {
    client: Client,
    symbol: String,
}

impl BinanceClient {
    // Constructor to initialize BinanceClient using config/config.yaml
    pub fn new() -> Self {
        let config_path = Path::new("config/config.yaml");
        let config_text = fs::read_to_string(config_path).expect("Failed to read config.yaml");
        let config: FullConfig = serde_yaml::from_str(&config_text).expect("Invalid YAML");

        Self {
            client: Client::new(),
            symbol: config.binance.default_symbol,
        }
    }

    // Get 24-hour ticker stats from Binance US public API
    pub fn get_ticker(&self) -> Result<HashMap<String, Value>, BinanceError> {
        let url = format!(
            "https://api.binance.us/api/v3/ticker/24hr?symbol={}",
            self.symbol
        );

        let response = self
            .client
            .get(&url)
            .send()
            .map_err(BinanceError::HttpError)?;

        let json: Value = response.json().map_err(|e| {
            BinanceError::ParseError(format!("Failed to parse JSON: {}", e.to_string()))
        })?;

        if json.is_object() {
            let mut result_map = HashMap::new();
            if let Some(map) = json.as_object() {
                for (key, value) in map {
                    result_map.insert(key.clone(), value.clone());
                }
            }
            Ok(result_map)
        } else {
            Err(BinanceError::ParseError("Unexpected JSON format".into()))
        }
    }
}
