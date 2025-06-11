use reqwest::blocking::Client;
use serde::Deserialize;
use std::fs;
use std::path::Path;
use hmac::{Hmac, Mac};
use sha2::{Sha256, Sha512, Digest};
use base64::{engine::general_purpose::STANDARD, Engine};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug)]
pub enum KrakenError {
    HttpError(reqwest::Error),
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
    api_key: String,
    api_secret: String,
}

impl KrakenClient {
    pub fn new() -> Self {
        let config_path = Path::new("config/config.yaml");
        let config_text = fs::read_to_string(config_path).expect("Failed to read config.yaml");
        let config: Config = serde_yaml::from_str(&config_text).expect("Invalid YAML");

        Self {
            client: Client::new(),
            pair: config.kraken.default_pair,
            api_key: config.kraken.api_key,
            api_secret: config.kraken.api_secret,
        }
    }

    pub fn generate_nonce(&self) -> String {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards")
            .as_millis()
            .to_string()
    }

    pub fn create_signature_message(&self, path: &str, nonce: &str, body_str: &str) -> Vec<u8> {
        let nonce_plus_data = format!("{}{}", nonce, body_str);
        let sha256_digest = Sha256::digest(nonce_plus_data.as_bytes());

        let mut message = path.as_bytes().to_vec();
        message.extend_from_slice(&sha256_digest);
        message
    }

    pub fn sign_message(&self, message: &[u8]) -> Result<String, KrakenError> {
        let decoded_secret = STANDARD.decode(&self.api_secret)
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        let mut mac = Hmac::<Sha512>::new_from_slice(&decoded_secret)
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        mac.update(message);
        let result = mac.finalize().into_bytes();
        Ok(STANDARD.encode(result))
    }
}

pub mod account;
pub mod markets;