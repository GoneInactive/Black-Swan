use reqwest::blocking::Client;
use reqwest::Error;
use serde::Deserialize;
use std::collections::HashMap;
use std::fs;
use serde_json::Value;
use std::path::Path;

#[derive(Debug)]
pub enum KrakenError {
    HttpError(Error),
    ParseError(String),
    MissingField(String),
}

#[derive(Debug, Deserialize)]
struct Config {
    kraken: KrakenConfig,
}

#[derive(Debug, Deserialize)]
struct KrakenConfig {
    api_key: String,
    api_secret: String,
    default_pair: String,
}

pub struct KrakenClient {
    client: Client,
    pair: String,
}

impl KrakenClient {
    // Modify the KrakenClient::new method to load the config file from the correct path
    pub fn new() -> Self {
        // Load config.yaml from the correct location (config/config.yaml)
        let config_path = Path::new("config/config.yaml");
        let config_text = fs::read_to_string(config_path).expect("Failed to read config.yaml");
        let config: Config = serde_yaml::from_str(&config_text).expect("Invalid YAML");

        Self {
            client: Client::new(),
            pair: config.kraken.default_pair,
        }
    }

    // Get the ticker data from Kraken API
    fn get_ticker(&self) -> Result<HashMap<String, serde_json::Value>, KrakenError> {
        let url = format!(
            "https://api.kraken.com/0/public/Ticker?pair={}",
            self.pair
        );

        let response = self
            .client
            .get(&url)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json: serde_json::Value = response.json().map_err(|e| {
            KrakenError::ParseError(format!("Failed to parse JSON: {}", e.to_string()))
        })?;

        if let Some(result) = json["result"].as_object() {
            // Manually convert serde_json::Map to HashMap
            let mut result_map = HashMap::new();
            for (key, value) in result.iter() {
                result_map.insert(key.clone(), value.clone());
            }
            Ok(result_map)
        } else {
            Err(KrakenError::ParseError("Missing result field".into()))
        }
    }

    // Get the current bid from the Kraken API
    pub fn get_bid(&self) -> Result<f64, KrakenError> {
        let data = self.get_ticker()?;
        let pair_data = data.values().next().ok_or_else(|| KrakenError::ParseError("Missing pair data".to_string()))?;
        
        // The bid is stored in the "b" field, which is an array, and we want the first value (index 0)
        let bid = pair_data["b"][0]
            .as_str()
            .ok_or_else(|| KrakenError::ParseError("Missing bid".into()))?;
        
        Ok(bid.parse().unwrap_or(0.0))
    }

    // Get the current ask from the Kraken API
    pub fn get_ask(&self) -> Result<f64, KrakenError> {
        let data = self.get_ticker()?;
        let pair_data = data.values().next().ok_or_else(|| KrakenError::ParseError("Missing pair data".to_string()))?;
        
        // The ask is stored in the "a" field, which is an array, and we want the first value (index 0)
        let ask = pair_data["a"][0]
            .as_str()
            .ok_or_else(|| KrakenError::ParseError("Missing ask".into()))?;
        
        Ok(ask.parse().unwrap_or(0.0))
    }

    // Get the spread (ask - bid) from Kraken API
    pub fn get_spread(&self) -> Result<f64, KrakenError> {
        let bid = self.get_bid()?;
        let ask = self.get_ask()?;
        Ok(ask - bid)
    }

    // Get the balance (stub for now, will be implemented later)
    pub fn get_balance(&self) -> Result<f64, KrakenError> {
        // Placeholder value until private auth is added
        Ok(1000.0)
    }
}
