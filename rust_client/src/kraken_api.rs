use reqwest::blocking::Client;
use serde::Deserialize;
use std::collections::HashMap;
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

#[derive(Debug)]
pub struct OrderResponse {
    pub txid: Vec<String>,
    pub description: String,
}

#[derive(Debug, Deserialize)]
pub struct OrderDescription {
    pub pair: String,
    #[serde(rename = "type")]
    pub order_type: String,
    pub ordertype: String,
    pub price: String,
    pub price2: String,
    pub leverage: String,
    pub order: String,
    pub close: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct OpenOrder {
    pub refid: Option<String>,
    pub userref: Option<String>,
    pub status: String,
    #[serde(deserialize_with = "deserialize_f64")]
    pub opentm: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub starttm: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub expiretm: f64,
    pub descr: OrderDescription,
    #[serde(deserialize_with = "deserialize_f64")]
    pub vol: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub vol_exec: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub cost: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub fee: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub price: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub stopprice: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub limitprice: f64,
    pub misc: String,
    pub oflags: String,
    pub reason: Option<String>,
}

fn deserialize_f64<'de, D>(deserializer: D) -> Result<f64, D::Error>
where
    D: serde::Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum StringOrFloat {
        String(String),
        Float(f64),
    }

    match StringOrFloat::deserialize(deserializer)? {
        StringOrFloat::String(s) => s.parse().map_err(serde::de::Error::custom),
        StringOrFloat::Float(f) => Ok(f),
    }
}

fn deserialize_number_from_string<'de, D>(deserializer: D) -> Result<f64, D::Error>
where
    D: serde::Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum StringOrFloat {
        String(String),
        Float(f64),
    }

    match StringOrFloat::deserialize(deserializer)? {
        StringOrFloat::String(s) => s.parse().map_err(serde::de::Error::custom),
        StringOrFloat::Float(f) => Ok(f),
    }
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

    pub fn get_open_orders_raw(&self) -> Result<String, KrakenError> {
        let nonce = self.generate_nonce();
        let body = format!("nonce={}", nonce);

        let path = "/0/private/OpenOrders";
        let url = format!("https://api.kraken.com{}", path);

        let message = self.create_signature_message(path, &nonce, &body);
        let signature = self.sign_message(&message)?;

        let response = self.client
            .post(&url)
            .header("API-Key", &self.api_key)
            .header("API-Sign", signature)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json_text = response.text()
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        Ok(json_text)
    }

    fn get_ticker(&self, pair: &str) -> Result<HashMap<String, serde_json::Value>, KrakenError> {
        let url = format!(
            "https://api.kraken.com/0/public/Ticker?pair={}",
            pair
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
            let mut result_map = HashMap::new();
            for (key, value) in result.iter() {
                result_map.insert(key.clone(), value.clone());
            }
            Ok(result_map)
        } else {
            Err(KrakenError::ParseError("Missing result field".into()))
        }
    }

    pub fn get_bid(&self, pair: &str) -> Result<f64, KrakenError> {
        let data = self.get_ticker(pair)?;
        let pair_data = data.values().next().ok_or_else(|| KrakenError::ParseError("Missing pair data".to_string()))?;
        
        let bid = pair_data["b"][0]
            .as_str()
            .ok_or_else(|| KrakenError::ParseError("Missing bid".into()))?;
        
        Ok(bid.parse().unwrap_or(0.0))
    }

    pub fn get_ask(&self, pair: &str) -> Result<f64, KrakenError> {
        let data = self.get_ticker(pair)?;
        let pair_data = data.values().next().ok_or_else(|| KrakenError::ParseError("Missing pair data".to_string()))?;
        
        let ask = pair_data["a"][0]
            .as_str()
            .ok_or_else(|| KrakenError::ParseError("Missing ask".into()))?;
        
        Ok(ask.parse().unwrap_or(0.0))
    }

    pub fn get_spread(&self, pair: &str) -> Result<f64, KrakenError> {
        let bid = self.get_bid(pair)?;
        let ask = self.get_ask(pair)?;
        Ok(ask - bid)
    }

    pub fn get_balance(&self) -> Result<HashMap<String, f64>, KrakenError> {
        let nonce = self.generate_nonce();
        let body = format!("nonce={}", nonce);

        let path = "/0/private/Balance";
        let url = format!("https://api.kraken.com{}", path);

        let message = self.create_signature_message(path, &nonce, &body);
        let signature = self.sign_message(&message)?;

        let response = self.client
            .post(&url)
            .header("API-Key", &self.api_key)
            .header("API-Sign", signature)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json: serde_json::Value = response.json()
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        if let Some(errors) = json.get("error").and_then(serde_json::Value::as_array) {
            if !errors.is_empty() {
                return Err(KrakenError::ParseError(
                    format!("Kraken API error: {:?}", errors)
                ));
            }
        }

        let result = json.get("result")
            .ok_or_else(|| KrakenError::MissingField("result".to_string()))?;

        let balances = result.as_object()
            .ok_or_else(|| KrakenError::ParseError("Expected result to be an object".to_string()))?
            .iter()
            .filter_map(|(k, v)| {
                v.as_str()
                    .and_then(|s| s.parse::<f64>().ok())
                    .map(|val| (k.clone(), val))
            })
            .collect();

        Ok(balances)
    }

    pub fn add_order(&self, pair: &str, side: &str, price: f64, volume: f64) -> Result<OrderResponse, KrakenError> {
        // Validate side parameter
        let side_lower = side.to_lowercase();
        if side_lower != "buy" && side_lower != "sell" {
            return Err(KrakenError::ParseError(
                "Side must be 'buy' or 'sell'".to_string()
            ));
        }

        let nonce = self.generate_nonce();
        
        // Build the order parameters
        let mut params = vec![
            ("nonce".to_string(), nonce.clone()),
            ("ordertype".to_string(), "limit".to_string()),
            ("type".to_string(), side_lower),
            ("volume".to_string(), volume.to_string()),
            ("price".to_string(), price.to_string()),
            ("pair".to_string(), pair.to_string()),
        ];

        // Create URL-encoded body
        let body = params
            .iter()
            .map(|(k, v)| format!("{}={}", k, v))
            .collect::<Vec<String>>()
            .join("&");

        let path = "/0/private/AddOrder";
        let url = format!("https://api.kraken.com{}", path);

        let message = self.create_signature_message(path, &nonce, &body);
        let signature = self.sign_message(&message)?;

        let response = self.client
            .post(&url)
            .header("API-Key", &self.api_key)
            .header("API-Sign", signature)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json: serde_json::Value = response.json()
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        // Check for API errors
        if let Some(errors) = json.get("error").and_then(serde_json::Value::as_array) {
            if !errors.is_empty() {
                return Err(KrakenError::ParseError(
                    format!("Kraken API error: {:?}", errors)
                ));
            }
        }

        let result = json.get("result")
            .ok_or_else(|| KrakenError::MissingField("result".to_string()))?;

        // Extract transaction IDs
        let txid = result.get("txid")
            .and_then(|t| t.as_array())
            .ok_or_else(|| KrakenError::ParseError("Missing txid array".to_string()))?
            .iter()
            .filter_map(|v| v.as_str().map(|s| s.to_string()))
            .collect::<Vec<String>>();

        // Extract order description
        let description = result.get("descr")
            .and_then(|d| d.get("order"))
            .and_then(|o| o.as_str())
            .unwrap_or("No description available")
            .to_string();

        Ok(OrderResponse {
            txid,
            description,
        })
    }

    fn generate_nonce(&self) -> String {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards")
            .as_millis()
            .to_string()
    }

    fn create_signature_message(&self, path: &str, nonce: &str, body_str: &str) -> Vec<u8> {
        let nonce_plus_data = format!("{}{}", nonce, body_str);
        let sha256_digest = Sha256::digest(nonce_plus_data.as_bytes());

        let mut message = path.as_bytes().to_vec();
        message.extend_from_slice(&sha256_digest);
        message
    }

    fn sign_message(&self, message: &[u8]) -> Result<String, KrakenError> {
        let decoded_secret = STANDARD.decode(&self.api_secret)
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        let mut mac = Hmac::<Sha512>::new_from_slice(&decoded_secret)
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        mac.update(message);
        let result = mac.finalize().into_bytes();
        Ok(STANDARD.encode(result))
    }
}