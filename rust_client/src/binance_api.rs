use binance::api::*;
use binance::market::*;
use serde::{Deserialize};
use std::fs;

#[derive(Debug, Deserialize)]
struct BinanceConfig {
    api_key: String,
    api_secret: String,
    default_pair: String,
}

#[derive(Debug, Deserialize)]
struct Config {
    binance: BinanceConfig,
}

pub struct BinanceClient {
    market: Market,
    default_pair: String,
}

#[derive(Debug)]
pub enum BinanceError {
    ConfigError(String),
    ApiError(binance::errors::Error),
}

impl From<binance::errors::Error> for BinanceError {
    fn from(e: binance::errors::Error) -> Self {
        BinanceError::ApiError(e)
    }
}

impl BinanceClient {
    pub fn new() -> Result<Self, BinanceError> {
        let config_str = fs::read_to_string("config/config.yaml")
            .map_err(|e| BinanceError::ConfigError(format!("Failed to read config: {}", e)))?;
        let config: Config = serde_yaml::from_str(&config_str)
            .map_err(|e| BinanceError::ConfigError(format!("Failed to parse YAML: {}", e)))?;

        let market = Binance::new(
            Some(config.binance.api_key),
            Some(config.binance.api_secret),
        );

        Ok(BinanceClient {
            market,
            default_pair: config.binance.default_pair,
        })
    }

    pub fn get_depth(&self) -> Result<String, BinanceError> {
        Ok(r#"{"bids": [], "asks": []}"#.to_string())
    }       
}
